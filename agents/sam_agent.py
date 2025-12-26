from google import adk
from google.genai import types

# System prompt for Sam Detection Agent
SAM_SYSTEM_PROMPT = """
You are a **Sam Detection Specialist**, an expert in identifying the exact moment when a Tabla player lands on the 'Sam' (the first beat of a rhythmic cycle).

Analyze the provided video and determine:
1. The exact timestamp (in seconds) when the player lands on Sam
2. The quality of the Sam landing (emphasis, synchronization)

Output format: "At [timestamp], the player lands on Sam with [quality assessment]"

Example: "At 0:03, the player lands on Sam with proper emphasis and precise synchronization"

Be specific with the timestamp. Output nothing else.
"""

def get_sam_agent():
    """
    Returns the Sam Detection Agent.
    """
    return adk.Agent(
        name="SamAgent",
        model="gemini-3-pro-preview",
        instruction=SAM_SYSTEM_PROMPT,
        generate_content_config=types.GenerateContentConfig(temperature=0.2),
        output_key="sam_result"  # Store result in session state
    )
