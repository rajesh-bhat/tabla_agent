import os
import logging

logger = logging.getLogger(__name__)

def validate_media_file(file_path: str) -> bool:
    """
    Validates if the file exists and has a supported video extension.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    supported_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() not in supported_extensions:
        logger.warning(f"Unsupported video extension: {ext}. Gemini might still support it, but proceed with caution.")
        return True 
        
    return True
