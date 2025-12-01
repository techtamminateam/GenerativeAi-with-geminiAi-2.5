# optimized_pipeline.py
import os
import re
import json
import glob
import time
import logging
import hashlib
from collections import OrderedDict
from logging.handlers import TimedRotatingFileHandler
from typing import Dict
import warnings
import tiktoken
from tqdm import tqdm

# Keep pdfplumber/pdf2image imports in case you use them elsewhere in the project.
import pdfplumber
from pdf2image import convert_from_path

# Imaging / OCR / PDF libs
import fitz  # PyMuPDF
import io
import pytesseract
import cv2
import numpy as np
from PIL import Image

# LangChain / Gemini / FAISS (unchanged)
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
import google.generativeai as genai
from dotenv import load_dotenv

# ---------------- ENV SETUP ----------------
load_dotenv(".env")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ---------------- Gemini CONFIG ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model_name = os.getenv("GEMINI_MODEL")
gemini_model = genai.GenerativeModel(model_name=gemini_model_name,
                                     generation_config={"temperature": 0.0})

# ---------------- Encoding ----------------
encoding = tiktoken.encoding_for_model("gpt-4-32k")

# ---------------- Logger ----------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def setup_logger():
    if not logger.handlers:
        os.makedirs("logs", exist_ok=True)
        fh = TimedRotatingFileHandler("logs/pipeline.log", when="midnight", interval=1, backupCount=7)
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger


setup_logger()
warnings.filterwarnings("ignore", message="CropBox missing")

# ---------------- TESSERACT PATH ----------------
# Adjust this if necessary for your environment
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---------------- HELPERS ----------------
def hash_image(img: Image.Image) -> str:
    """Hash a PIL image (PNG bytes) for duplicate detection."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return hashlib.md5(buf.getvalue()).hexdigest()


def clean_text_for_llm(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(.)\1{4,}", r"\1\1", text)
    text = text.replace("✔", "[CHECKED]").replace("☑", "[CHECKED]").replace("☐", "[UNCHECKED]")
    return text.strip()


def split_text(text, max_tokens=4000, buffer=400):
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens - buffer):
        chunk = encoding.decode(tokens[i:i + max_tokens - buffer])
        chunks.append(chunk)
    return chunks


def create_vectorstore(texts):
    """Generate embeddings and create a FAISS vector store."""
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-large",
        model="text-embedding-3-large"
    )
    return FAISS.from_texts(texts, embeddings)


def normalize_dict_keys(data):
    return {k.lower().replace(' ', '').replace('_', ''): v for k, v in data.items()}


def save_dict_to_json(data, output_path):
    base_path = output_path.replace(".pdf", "")
    if isinstance(data, dict):
        json_path = f"{base_path}_structured.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"✅ Saved structured JSON to {json_path}")
        return json_path
    else:
        txt_path = f"{base_path}_extracted.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(str(data))
        logger.info(f"📝 Saved extracted text to {txt_path}")
        return txt_path


def load_extracted_text(output_path: str) -> str:
    txt_path = output_path.replace(".pdf", "_extracted.txt")
    if os.path.exists(txt_path):
        logger.info(f"Loading cached extracted text from {txt_path}")
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


# ---------------- IMAGE PREPROCESSING + HYBRID OCR (fast) ----------------
def preprocess_image_fast(pil_img: Image.Image) -> Image.Image:
    """
    Lightweight preprocessing: grayscale -> small Gaussian blur -> Otsu threshold.
    Faster than heavy denoising + adaptive threshold for most scanned documents.
    """
    img = pil_img.convert("L")
    arr = np.array(img)

    # small Gaussian blur to remove tiny noise
    arr = cv2.GaussianBlur(arr, (3, 3), 0)

    # Otsu threshold (fast, robust)
    _, thresh = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)


def fast_ocr(pil_img: Image.Image) -> str:
    """
    Single fast Tesseract pass (PSM 6 recommended for blocks/forms).
    Keep OEM 1 (LSTM) for best accuracy on modern Tesseract builds.
    """
    config = "--oem 1 --psm 6 -l eng"
    return pytesseract.image_to_string(pil_img, config=config)


# Keep a compatibility wrapper named hybrid_ocr (original code references it).
def hybrid_ocr(pil_img: Image.Image) -> str:
    # For speed, just call the fast_ocr single pass. If you want to experiment,
    # you can later try multiple configs and pick best; that costs time.
    return fast_ocr(pil_img)


# ---------------- FAST PAGE RENDERING ----------------
def render_page_fast(page, scale: float = 1.7) -> Image.Image:
    """
    Render a page using PyMuPDF matrix scaling, which is faster than repeatedly using DPI.
    scale ~1.7 approximates ~150 DPI for most pages — adjust if you need higher fidelity.
    """
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))


# ---------------- SCANNED PAGE DETECTION (vectorized, fast) ----------------
def is_scanned_page(page, thumb_scale: float = 0.25, white_threshold: int = 245, dark_ratio_threshold: float = 0.06) -> bool:
    """
    Fast detection if page is scanned (rasterized) by creating a tiny thumbnail and using vectorized numpy ops.

    - thumb_scale: small scale factor (0.25) to produce a tiny image (very fast)
    - white_threshold: pixel value above which we consider a pixel "white"
    - dark_ratio_threshold: fraction of non-white pixels above which we treat as scanned
    """
    try:
        # small matrix for thumbnail
        mat = fitz.Matrix(thumb_scale, thumb_scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
        arr = np.array(img)

        # vectorized: proportion of pixels darker than white_threshold
        dark_pixels = np.count_nonzero(arr < white_threshold)
        total = arr.size
        dark_ratio = dark_pixels / total

        # If the thumbnail has a reasonable amount of dark pixels -> likely contains raster content
        return dark_ratio > dark_ratio_threshold
    except Exception as e:
        logger.debug(f"is_scanned_page detection failed: {e}")
        return False


# ---------------- REGEX EXTRACTION ----------------
def extract_with_regex(text, data_points):
    results = {}
    compiled_patterns = {k: re.compile(p, re.IGNORECASE | re.DOTALL) for k, p in data_points.items()}
    for key, pattern in compiled_patterns.items():
        match = pattern.search(text)
        results[key] = match.group(1).strip() if match else None
    return results


# ---------------- PDF TEXT EXTRACTION (OPTIMIZED) ----------------
def text_extract_from_pdf(pdf_path: str) -> str:
    page_texts: Dict[int, str] = {}
    seen_image_hashes = set()

    try:
        doc = fitz.open(pdf_path)

        for page_idx in tqdm(range(len(doc)), desc="Extracting All Signals"):
            page = doc[page_idx]
            page_num = page_idx + 1

            segments = [f"[PAGE {page_num} START]"]

            # ---------------- Digital Text ----------------
            raw_text = page.get_text("text") or ""
            raw_text_clean = raw_text.strip()

            if raw_text_clean:
                text_lines = [clean_text_for_llm(line) for line in raw_text_clean.splitlines() if line.strip()]
                if text_lines:
                    segments.append("[TEXT] " + " ".join(text_lines))

            # ---------------- Tables (PyMuPDF) ----------------
            try:
                tables = page.find_tables()
                if tables:
                    for t_idx, table in enumerate(tables, start=1):
                        segments.append(f"[TABLE {t_idx}]")
                        df = table.to_pandas()
                        for r_idx, row in df.iterrows():
                            row_text = " | ".join(clean_text_for_llm(str(v)) if v else "" for v in row.values)
                            segments.append(f"  [ROW {r_idx+1}] {row_text}")
            except Exception:
                # table extraction is optional; ignore failures
                pass

            # ---------------- Scanned Page Detection (fast) ----------------
            # Decide if we need OCR:
            # - If no digital text -> likely scanned OR
            # - If thumbnail analysis suggests raster content -> likely scanned
            scanned = False
            if not raw_text_clean:
                scanned = True
            else:
                # If text exists but small, or thumbnail shows raster content, run OCR
                if len(raw_text_clean) < 30:
                    scanned = True
                else:
                    # thumbnail test (fast)
                    try:
                        if is_scanned_page(page):
                            scanned = True
                    except Exception as e:
                        logger.debug(f"Thumbnail detection error on page {page_num}: {e}")
                        scanned = False

            # ---------------- OCR for Scanned Pages ----------------
            if scanned:
                # Fast render (matrix scaling) -> high enough resolution for accurate OCR
                img = render_page_fast(page, scale=1.7)

                img_hash = hash_image(img)

                if img_hash not in seen_image_hashes:
                    seen_image_hashes.add(img_hash)

                    processed_img = preprocess_image_fast(img)
                    ocr_raw = hybrid_ocr(processed_img)

                    if ocr_raw and ocr_raw.strip():
                        ocr_lines = [clean_text_for_llm(line) for line in ocr_raw.splitlines() if line.strip()]
                        if ocr_lines:
                            if "|" in ocr_raw or re.search(r"\s{3,}", ocr_raw):
                                segments.append("[OCR_TABLE] " + " ".join(ocr_lines))
                            else:
                                segments.append("[OCR] " + " ".join(ocr_lines))
                else:
                    logger.info(f"OCR skipped for page {page_num} (duplicate image)")

            segments.append(f"[PAGE {page_num} END]")

            # Remove duplicates and store
            segments = list(OrderedDict.fromkeys(segments))
            page_texts[page_num] = "\n".join(segments)

    except Exception as e:
        logger.error(f"❌ Failed to process {pdf_path}: {e}", exc_info=True)
        raise

    # Return all pages in order
    return "\n".join(page_texts[p] for p in sorted(page_texts.keys()))


# ---------------- MAIN PROCESS ----------------
def main(file_path, business, data_points_map, prompt_map):
    logger.info(f"Processing {file_path}")

    large_text = load_extracted_text(file_path)
    if large_text is None:
        large_text = text_extract_from_pdf(file_path)
        save_dict_to_json(large_text, file_path)

    pdf_tokens = len(encoding.encode(large_text))
    logger.info(f"Original PDF tokens: {pdf_tokens}")

    # Split and create vectorstore if too many tokens
    if pdf_tokens > 40000:
        logger.info("Splitting text due to token limit")
        max_tokens = 4000
        if business == "package":
            max_tokens = 5000
        texts = split_text(large_text, max_tokens, buffer=400)
        vectorstore = create_vectorstore(texts)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
        docs = retriever.get_relevant_documents("insurance policy document")
        combined_text = "\n\n".join([d.page_content for d in docs])
    else:
        combined_text = large_text

    # --- Step 1: Regex extraction
    regex_results = extract_with_regex(combined_text, data_points_map.get(business, lambda: {})())

    # --- Step 2: Gemini fallback for missing fields
    missing_keys = [k for k, v in regex_results.items() if not v]
    if missing_keys:
        user_prompt = prompt_map[business](combined_text)
        prompt_text = f"You are an insurance data extractor. Fill missing fields: {missing_keys}\n\n{user_prompt}"

        prompt_token_count = len(encoding.encode(prompt_text))
        logger.info(f"📨 Sending {prompt_token_count} tokens to Gemini for fallback extraction")

        try:
            if business in ["cyber", "general_liability", "comercial_auto"]:
                gemini_flash_model = genai.GenerativeModel(model_name=gemini_model_name,
                                                          generation_config={"temperature": 0.0})
                logger.info(f"Extracting using {gemini_model_name} for {business} business")
                response = gemini_flash_model.generate_content(
                    ["JSON only", prompt_text],
                    generation_config={"response_mime_type": "application/json"}
                )
            else:
                response = gemini_model.generate_content(
                    ["JSON only", prompt_text],
                    generation_config={
                        "response_mime_type": "application/json",
                    })
                logger.info(f"Extracting using {gemini_model} for {business} business")

            gemini_data = json.loads(response.text.replace("```json", '').replace("```", ''))
            for k in missing_keys:
                regex_results[k] = gemini_data.get(k, None)
        except Exception as e:
            logger.error(f"Gemini fallback failed: {e}", exc_info=True)

    return normalize_dict_keys(regex_results)


# ---------------- RUN ----------------
if __name__ == "__main__":
    from utils.data_points import (
        cyber_data_points,
        general_liability_data_points,
        business_owner_data_points,
        comercial_auto_data_points,
        workers_compensation_points,
        property_data_points
    )
    from utils.queryy import (
        prompt_template_cyber,
        prompt_template_general,
        prompt_template_commercial_auto,
        prompt_template_general_liability,
        prompt_template_property,
        prompt_template_business_owner,
        prompt_template_package,
        prompt_template_workers_compensation
    )

    content_folder = "package"  # Change as needed
    business = "package"  # Change as needed

    # Example: you can put a glob pattern or a list of files
    pdf_files = glob.glob(os.path.join(content_folder, "Package 4.6.2025 Renewal Dec Policy# BKS57204580 Insured Copy.pdf"))

    prompt_map = {
        "cyber": prompt_template_cyber,
        "general": prompt_template_general,
        "comercial_auto": prompt_template_commercial_auto,
        "general_liability": prompt_template_general_liability,
        "property": prompt_template_property,
        "business_owner": prompt_template_business_owner,
        "package": prompt_template_package,
        "workers_comp": prompt_template_workers_compensation
    }

    data_points_map = {
        "cyber": cyber_data_points,
        "general": business_owner_data_points,
        "comercial_auto": comercial_auto_data_points,
        "general_liability": general_liability_data_points,
        "property": property_data_points,
        "business_owner": business_owner_data_points,
        "package": business_owner_data_points,
        "workers_comp": workers_compensation_points
    }

    for file_path in pdf_files:
        try:
            result = main(file_path, business, data_points_map, prompt_map)
            save_dict_to_json(result, file_path)
        except Exception as e:
            logger.error(f"❌ Failed {file_path}: {e}", exc_info=True)
        
