from google import adk
from google.adk.agents import ParallelAgent, SequentialAgent
from .taal_agent import get_taal_agent
from .sam_agent import get_sam_agent
from .bpm_agent import get_bpm_agent

def get_orchestrator_agent():
    """
    Returns the main orchestrator agent using ADK's ParallelAgent and SequentialAgent.
    
    Architecture:
    1. ParallelAgent runs Taal and Sam agents concurrently
    2. BPM agent runs next, using Taal and Sam results, outputs final JSON
    """
    # Create the specialized analysis agents
    taal_agent = get_taal_agent()
    sam_agent = get_sam_agent()
    bpm_agent = get_bpm_agent()
    
    # Create ParallelAgent to run Taal and Sam agents concurrently
    parallel_taal_sam = ParallelAgent(
        name="ParallelTaalSamAnalysis",
        sub_agents=[taal_agent, sam_agent],
        description="Runs Taal and Sam analysis agents in parallel."
    )
    
    # Create SequentialAgent to orchestrate: 
    # Step 1: Parallel Taal+Sam
    # Step 2: BPM (uses Taal and Sam results, outputs final JSON)
    sequential_pipeline = SequentialAgent(
        name="TablaAnalysisPipeline",
        sub_agents=[parallel_taal_sam, bpm_agent],
        description="Coordinates analysis: Taal+Sam in parallel, then BPM with final JSON output."
    )
    
    return sequential_pipeline
