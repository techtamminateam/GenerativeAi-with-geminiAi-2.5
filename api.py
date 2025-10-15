import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn
from pathlib import Path
from starlette.status import HTTP_403_FORBIDDEN

# Import the processing functions from main.py
from main import main, setup_logger
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

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Document Processor API",
    description="API for processing insurance documents and extracting relevant information",
    version="1.0.0"
)

# Security configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    api_key_header: str = Security(api_key_header), #figure this out later----------------
):
    if api_key_header is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API Key header is missing"
        )
    
    if api_key_header != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )
    
    return api_key_header

# Initialize logger
logger = setup_logger()

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("BusinessOwners", exist_ok=True) #remove this after testing

# Define the mapping dictionaries
prompt_map = {
    "cyber": prompt_template_cyber,
    "general": prompt_template_general,
    "comercial_auto": prompt_template_commercial_auto,
    "general_liability": prompt_template_general_liability,
    "property": prompt_template_property,
    "business_owner": prompt_template_business_owner,
    "package": prompt_template_package
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

# Args:
#      file: PDF file to process
#      business_type: Type of business insurance document (default: business_owner) 
# Returns JSON response with extracted information
@app.post("/process-document/")
async def process_document(
    file: UploadFile = File(...),
    business_type: str = "business_owner",
    api_key: str = Depends(get_api_key)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    if business_type not in data_points_map:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported business type. Supported types: {list(data_points_map.keys())}"
        )
    
    try:
        # Save the uploaded file
        file_path = Path("uploads") / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the document
        result = main(
            str(file_path),
            business_type,
            data_points_map,
            prompt_map
        )
        
        # Clean up the uploaded file
        os.remove(file_path)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

#Get a list of supported business types for document processing.
@app.get("/supported-business-types/")
async def get_supported_business_types(
    api_key: str = Depends(get_api_key)
):
    return list(data_points_map.keys())

# Health check endpoint.
@app.get("/health/")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
