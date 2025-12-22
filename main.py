import sys
import asyncio
import os
from dotenv import load_dotenv
from app import TablaFeedbackApp
from tools.media_utils import validate_media_file

# Load environment variables
load_dotenv()

async def run_cli():
    if len(sys.argv) < 2:
        print("\033[91mUsage: python3 main.py <path_to_tabla_video>\033[0m")
        return

    video_file = sys.argv[1]
    
    # 1. Validate input
    if not validate_media_file(video_file):
        print(f"\033[91mError: File '{video_file}' is invalid or does not exist.\033[0m")
        return

    # 2. Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\033[93mWarning: GOOGLE_API_KEY not found in environment. Ensure it is set.\033[0m")

    # 3. Process
    app = TablaFeedbackApp()
    try:
        feedback = await app.run_feedback(os.path.abspath(video_file))
        
        print("\n" + "="*50)
        print("\033[92mFEEDBACK FROM TABLA AGENT\033[0m")
        print("="*50)
        print(feedback)
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\033[91mAn error occurred during analysis: {e}\033[0m")

if __name__ == "__main__":
    asyncio.run(run_cli())
