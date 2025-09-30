from tools import summaryTool, speechToTextTool
from utils.getMarkdown import generate_markdown_summary
# Enhanced main.py with proper typing
from typing import AsyncGenerator, Tuple, Optional, Dict, Any
import logging
from config.settings import validate_environment

logger = logging.getLogger(__name__)

async def summaryAgent(input_path: str) -> AsyncGenerator[Tuple[str, Optional[str]], None]:
    if not validate_environment():
        raise SystemExit("Missing required environment variables")
    """
    Process audio file through transcription and summarization pipeline.
    
    Args:
        input_path: Path to the audio file to process
        
    Yields:
        Tuple of (status_message, accumulated_result)
    """
    try:
        yield "🧠 Transcribe started...", None
        
        # Transcribe audio
        logger.info(f"Transcribing audio file: {input_path}")
        transcript_result = speechToTextTool(input_path)
        
        if not transcript_result.get("success", False):
            yield f"❌ Transcription failed: {transcript_result.get('error', 'Unknown error')}", None
            return
            
        yield "✅ Transcription completed.", None
        
        # Summarize transcript
        logger.info("Summarizing transcript...")
        yield "🧠 Summarizing transcript...", None
        
        summary = summaryTool(transcript_result["text"])
        yield "✅ Summary generation completed.", None
        
        # Generate markdown
        marked_down_data = generate_markdown_summary(summary)
        yield "✅ Summary complete.", marked_down_data
        
    except Exception as e:
        logger.error(f"Error in summaryAgent: {e}")
        yield f"❌ Error: {str(e)}", None



# async def summaryAgent(input) -> str:
#     print("Hello from sample-app!");
#     instructions = "\
#     You are a helpful assistant that summarizes meetings.\
#     Use SpeechToText tool to transcribe mp3 file to text. \
#     Use summaryTool to summarize the meeting transcript. \
#     ";
#     print('ready to call agent');
#     agent = Agent(name="Assistant", instructions=instructions, tools=[speechToTextTool, summaryTool])
#     print('after agent call>>>>>>>>>>>>');

#     summary = await Runner.run(agent, input)
#     print('after run syncss>>>>>>>>>>>>', summary.final_output);

#     print(summary.final_output)
#     return summary.final_output
