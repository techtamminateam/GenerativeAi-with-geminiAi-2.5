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

import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from PIL import Image

from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
import google.generativeai as genai
from dotenv import load_dotenv

# ---------------- ENV SETUP ----------------
load_dotenv(".env")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ---------------- Gemini CONFIG ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("models/gemini-2.5-pro")

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

# ---------------- HELPERS ----------------
def hash_image(img) -> str:
    import io
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

# ---------------- IMAGE PREPROCESSING + HYBRID OCR ----------------
def preprocess_image_for_ocr(pil_img):
    """Enhance image for OCR using denoising and adaptive thresholding."""
    img_cv = np.array(pil_img)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=30)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 35, 11
    )
    return Image.fromarray(thresh)

def hybrid_ocr(pil_img):
    """
    Hybrid OCR using multiple PSM modes to handle mixed layouts:
    - psm 4: multiple columns or text blocks
    - psm 6: uniform block (tables/forms)
    - psm 11: sparse text (scattered info)
    """
    configs = [
        "--oem 1 --psm 4 -l eng",
        "--oem 1 --psm 6 -l eng",
        "--oem 1 --psm 11 -l eng"
    ]

    best_text = ""
    for cfg in configs:
        text = pytesseract.image_to_string(pil_img, config=cfg)
        if len(text.strip()) > len(best_text):
            best_text = text
    return best_text

# ---------------- REGEX EXTRACTION ----------------
def extract_with_regex(text, data_points):
    results = {}
    for key, pattern in data_points.items():
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            results[key] = match.group(1).strip() if match else None
        except Exception:
            results[key] = None
    return results

# ---------------- PDF TEXT EXTRACTION ----------------
def text_extract_from_pdf(pdf_path: str) -> str:
    page_texts: Dict[int, str] = {}
    seen_image_hashes = set()
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in tqdm(pdf.pages, desc="Extracting All Signals"):
                page_num = page.page_number
                segments = [f"[PAGE {page_num} START]"]

                # Digital text
                raw_text = page.extract_text(x_tolerance=0.5, y_tolerance=1.5, layout=True)
                if raw_text:
                    text_lines = [clean_text_for_llm(line) for line in raw_text.splitlines() if line.strip()]
                    if text_lines:
                        segments.append("[TEXT] " + " ".join(text_lines))

                # Tables
                tables = page.extract_tables()
                if tables:
                    for t_idx, table in enumerate(tables, start=1):
                        segments.append(f"[TABLE {t_idx}]")
                        for r_idx, row in enumerate(table, start=1):
                            if any(cell and cell.strip() for cell in row):
                                row_text = " | ".join([clean_text_for_llm(cell) if cell else "" for cell in row])
                                segments.append(f"  [ROW {r_idx}] {row_text}")

                # OCR for images (Hybrid)
                if page.images:
                    img = convert_from_path(pdf_path, dpi=300, first_page=page_num, last_page=page_num)[0]
                    img_hash = hash_image(img)
                    if img_hash not in seen_image_hashes:
                        seen_image_hashes.add(img_hash)

                        processed_img = preprocess_image_for_ocr(img)
                        ocr_raw = hybrid_ocr(processed_img)

                        if ocr_raw.strip():
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
        logger.error(f"❌ Failed to process {pdf_path}: {e}")
        raise

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
        texts = split_text(large_text,max_tokens,buffer=400)
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

        if business in ["cyber","general_liability","comercial_auto"]:
            gemini_flash_model = genai.GenerativeModel("models/gemini-2.5-flash")
            logger.info(f"Extracting using Gemini 2.5-flash for {business} business")
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
        try:
            gemini_data = json.loads(response.text.replace("```json", '').replace("```", ''))
            for k in missing_keys:
                regex_results[k] = gemini_data.get(k, None)
        except Exception as e:
            logger.error(f"Gemini fallback failed: {e}")

    return normalize_dict_keys(regex_results)

# ---------------- RUN ----------------
if __name__ == "__main__":
    from utils.data_points import (
        cyber_data_points,
        general_liability_data_points,
        business_owner_data_points,
        comercial_auto_data_points
    )
    from utils.queryy import (
        prompt_template_cyber,
        prompt_template_general,
        prompt_template_commercial_auto,
        prompt_template_general_liability,
        prompt_template_property,
        prompt_template_business_owner,
        prompt_template_package
    )

    content_folder = "package"  # Change as needed
    business = "package"  # Change as needed
    pdf_files = glob.glob(os.path.join(content_folder, "*pdf"))

    prompt_map = {
        "cyber": prompt_template_cyber,
        "general": prompt_template_general,
        "comercial_auto": prompt_template_commercial_auto,
        "general_liability": prompt_template_general_liability,
        "property": prompt_template_property,
        "business_owner": prompt_template_business_owner,
        "package": prompt_template_business_owner
    }

    data_points_map = {
        "cyber": cyber_data_points,
        "general": business_owner_data_points,
        "comercial_auto": comercial_auto_data_points,
        "general_liability": general_liability_data_points,
        "property": cyber_data_points,
        "business_owner": business_owner_data_points,
        "package": business_owner_data_points
    }

    for file_path in pdf_files:
        try:
            result = main(file_path, business, data_points_map, prompt_map)
            save_dict_to_json(result, file_path)
        except Exception as e:
            logger.error(f"❌ Failed {file_path}: {e}", exc_info=True)
