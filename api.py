import os
import shutil
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app import TablaFeedbackApp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TablaAPI")

app = FastAPI(title="Tabla Agent")

# Ensure directories exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize the ADK App
tabla_app = TablaFeedbackApp()

@app.post("/analyze")
async def analyze_media(file: UploadFile = File(...)):
    """
    Receives an audio file, saves it, and runs the ADK agent for feedback.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Save file temporarily
    file_extension = os.path.splitext(file.filename)[1]
    temp_filename = f"{uuid.uuid4()}{file_extension}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {temp_path}. Running analysis...")
        
        # Run ADK agent
        feedback = await tabla_app.run_feedback(os.path.abspath(temp_path))
        
        return {"feedback": feedback, "filename": file.filename}
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Optional: cleanup file after analysis if desired
        # os.remove(temp_path)
        pass

# Serve static files for the frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
