import os
import logging
from google import adk
from google import genai
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents import get_orchestrator_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TablaApp")

class TablaFeedbackApp:
    def __init__(self, app_name="TablaFeedbackSystem"):
        # Initialize the orchestrator agent (which manages sub-agents internally)
        self.agent = get_orchestrator_agent()
        self.session_service = InMemorySessionService()
        self.runner = adk.Runner(
            app_name=app_name,
            agent=self.agent,
            session_service=self.session_service
        )
        
        # Initialize Gemini Client for file uploads
        self.genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        logger.info(f"Orchestrator agent initialized with {len(self.agent.sub_agents)} sub-agents")

    async def run_feedback(self, media_uri: str, user_id="prod_user", session_id=None):
        """
        Runs the orchestrator agent which automatically coordinates sub-agents.
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

            # Upload the video file using the File API
            logger.info(f"Uploading file to Gemini File API: {media_uri}")
            uploaded_file = self.genai_client.files.upload(file=media_uri)
            
            # Wait for the file to be processed
            import time
            while uploaded_file.state.name == "PROCESSING":
                logger.info("Waiting for video processing...")
                time.sleep(2)
                uploaded_file = self.genai_client.files.get(name=uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception("Video processing failed on Gemini side.")

            # Prepare the video message
            message = types.Content(
                role="user", 
                parts=[
                    types.Part.from_uri(
                        file_uri=uploaded_file.uri, 
                        mime_type=uploaded_file.mime_type
                    ), 
                    types.Part.from_text(text="Analyze this Tabla performance using your sub-agents.")
                ]
            )
        except Exception as e:
            logger.error(f"Failed to prepare video data or session: {e}")
            raise

        logger.info(f"Starting orchestrator agent analysis (sub-agents will run in parallel)")
        
        # Run the orchestrator agent - it will automatically coordinate sub-agents
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
        
        logger.info("Orchestrator analysis complete.")
        
        # Extract only the JSON output (the last valid JSON in the response)
        import json
        import re
        
        # Try to find JSON object in the response
        json_match = re.search(r'\{[^{}]*"taal_identification"[^{}]*"sam_analysis"[^{}]*"tempo_bpm"[^{}]*\}', full_response, re.DOTALL)
        
        if json_match:
            try:
                # Validate it's proper JSON
                json_str = json_match.group(0)
                json.loads(json_str)  # Validate
                logger.info(f"Extracted clean JSON: {json_str[:100]}...")
                return json_str
            except json.JSONDecodeError:
                logger.warning("Found JSON-like text but failed to parse, returning full response")
                return full_response
        else:
            logger.warning("No JSON found in response, returning full response")
            return full_response
