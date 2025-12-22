import os
import logging
from google import adk
from google import genai
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents import get_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TablaApp")

class TablaFeedbackApp:
    def __init__(self, app_name="TablaFeedbackSystem"):
        self.agent = get_agent()
        self.session_service = InMemorySessionService()
        self.runner = adk.Runner(
            app_name=app_name,
            agent=self.agent,
            session_service=self.session_service
        )
        # Initialize Gemini Client for file uploads
        self.genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        logger.info(f"App '{app_name}' initialized with agent '{self.agent.name}'")

    async def run_feedback(self, media_uri: str, user_id="prod_user", session_id=None):
        """
        Runs the agent to get feedback on the provided video/audio.
        """
        if session_id is None:
            import uuid
            session_id = f"session_{uuid.uuid4().hex[:8]}"

        try:
            # Check if session exists, create if not
            session = await self.session_service.get_session(
                app_name=self.runner.app_name, 
                user_id=user_id, 
                session_id=session_id
            )
            if not session:
                await self.session_service.create_session(
                    app_name=self.runner.app_name, 
                    user_id=user_id, 
                    session_id=session_id
                )
                logger.info(f"Created new session: {session_id}")

            # 1. Upload the video file using the File API
            # Gemini models cannot access local file paths directly via 'from_uri'
            logger.info(f"Uploading file to Gemini File API: {media_uri}")
            uploaded_file = self.genai_client.files.upload(file=media_uri)
            
            # Wait for the file to be processed (important for videos)
            import time
            while uploaded_file.state.name == "PROCESSING":
                logger.info("Waiting for video processing...")
                time.sleep(2)
                uploaded_file = self.genai_client.files.get(name=uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception("Video processing failed on Gemini side.")

            # 2. Prepare the message using the uploaded file's URI
            message = types.Content(
                role="user", 
                parts=[
                    types.Part.from_uri(
                        file_uri=uploaded_file.uri, 
                        mime_type=uploaded_file.mime_type
                    ), 
                    types.Part.from_text(text="Please identify the Taal and identify the exact timestamp (in seconds) of when I land on the Sam.")
                ]
            )
        except Exception as e:
            logger.error(f"Failed to prepare video data or session: {e}")
            raise

        logger.info(f"Starting feedback analysis for: {uploaded_file.uri} in session: {session_id}")
        
        full_response = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if part.text:
                        full_response += part.text
        
        logger.info("Feedback analysis complete.")
        return full_response
