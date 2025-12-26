"""
Optimized UI module for the Agentic Summarizer App.
Features improved error handling, progress tracking, and user experience.
"""

from utils.hf_compat import patch_hf_hub_download

# ruff: noqa: E402
patch_hf_hub_download()  # 🔥 MUST be before pyannote imports

import logging
import os
import tempfile
from collections.abc import AsyncGenerator

# from functools import wraps
import gradio as gr
from dotenv import load_dotenv

from config.settings import settings
from main import summaryAgent, voiceRecognitionAgent
from utils.file_utils import cleanup_temp_file, validate_audio_file
from utils.logging_config import setup_logging

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)


class ProgressTracker:
    """Enhanced progress tracking with dynamic steps and better UX."""

    def __init__(self, total_steps: int = 4):
        self.total_steps = total_steps
        self.current_step = 0
        self.steps = [
            "Initializing...",
            "Transcribing audio...",
            "Generating summary...",
            "Formatting output...",
        ]

    def next_step(self) -> tuple[str, int]:
        """Get next step information."""
        if self.current_step < self.total_steps:
            self.current_step += 1
            return self.steps[self.current_step - 1], self.current_step
        return "Complete", self.total_steps

    def get_progress_percentage(self) -> int:
        """Get current progress percentage."""
        return int((self.current_step / self.total_steps) * 100)


class UIComponents:
    """Centralized UI component styling and HTML generation."""

    @staticmethod
    def get_status_html(status: str, is_error: bool = False) -> str:
        """Generate styled status HTML."""
        color = "#ef4444" if is_error else "#10b981" if "✅" in status else "#6b7280"
        icon = "❌" if is_error else "✅" if "✅" in status else "🔄"

        return f"""
        <div style="margin-top: 12px; padding: 8px 12px; border-radius: 6px; 
                    background-color: {"#fef2f2" if is_error else "#f0fdf4" if "✅" in status else "#f9fafb"}; 
                    border-left: 4px solid {color};">
            <span style="color: {color}; font-weight: 500;">{icon} {status}</span>
        </div>
        """

    @staticmethod
    def get_progress_html(step: int, total: int, step_name: str = "") -> str:
        """Generate enhanced progress bar HTML."""
        percent = int((step / total) * 100)

        return f"""
        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 500; color: #374151;">Progress</span>
                <span style="font-size: 14px; color: #6b7280;">{step}/{total} ({percent}%)</span>
            </div>
            <div style="width: 100%; background-color: #e5e7eb; border-radius: 8px; height: 8px; overflow: hidden;">
                <div style="width: {percent}%; height: 100%; background: linear-gradient(90deg, #3b82f6, #1d4ed8); 
                            transition: width 0.5s ease-in-out; border-radius: 8px;"></div>
            </div>
            {f'<div style="margin-top: 4px; font-size: 12px; color: #6b7280;">{step_name}</div>' if step_name else ""}
        </div>
        """

    @staticmethod
    def get_error_html(error_message: str) -> str:
        """Generate error display HTML."""
        return f"""
        <div style="margin: 16px 0; padding: 16px; border-radius: 8px; 
                    background-color: #fef2f2; border: 1px solid #fecaca;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 20px; margin-right: 8px;">❌</span>
                <span style="font-weight: 600; color: #dc2626;">Error</span>
            </div>
            <p style="color: #7f1d1d; margin: 0; font-size: 14px;">{error_message}</p>
        </div>
        """

    @staticmethod
    def get_success_html(message: str) -> str:
        """Generate success display HTML."""
        return f"""
        <div style="margin: 16px 0; padding: 16px; border-radius: 8px; 
                    background-color: #f0fdf4; border: 1px solid #bbf7d0;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 20px; margin-right: 8px;">✅</span>
                <span style="color: #166534; font-weight: 500;">{message}</span>
            </div>
        </div>
        """


async def gradio_wrapper(
    audio_path: str, progress=gr.Progress()
) -> AsyncGenerator[tuple[str, str | None], None]:
    """
    Enhanced wrapper for the summary agent with comprehensive error handling and progress tracking.

    Args:
        audio_path: Path to the audio file
        progress: Gradio progress tracker

    Yields:
        Tuple of (status_html, final_summary)
    """
    final_summary = None
    progress_tracker = ProgressTracker()
    logger.info(f"audio_path============{audio_path}")
    try:
        # Validate input file
        if not audio_path:
            error_html = UIComponents.get_error_html(
                "No file uploaded. Please select an audio file."
            )
            yield error_html, None
            return

        if not os.path.exists(audio_path):
            error_html = UIComponents.get_error_html(f"File not found: {audio_path}")
            yield error_html, None
            return

        # Validate file type and size
        if not validate_audio_file(audio_path):
            error_html = UIComponents.get_error_html(
                f"Invalid file. Please upload a supported audio file (MP3, WAV, M4A) "
                f"under {settings.MAX_FILE_SIZE // (1024 * 1024)}MB."
            )
            yield error_html, None
            return

        # Initialize progress
        step_name, step_num = progress_tracker.next_step()
        progress_html = UIComponents.get_progress_html(
            step_num, progress_tracker.total_steps, step_name
        )
        status_html = UIComponents.get_status_html("🚀 Starting processing...")
        yield progress_html + status_html, None

        # Process through summary agent
        async for status, accumulated in summaryAgent(audio_path):
            step_name, step_num = progress_tracker.next_step()
            progress_html = UIComponents.get_progress_html(
                step_num, progress_tracker.total_steps, step_name
            )
            status_html = UIComponents.get_status_html(status)

            combined_html = progress_html + status_html
            yield combined_html, None
            final_summary = accumulated

        # Final success state
        progress_html = UIComponents.get_progress_html(
            progress_tracker.total_steps, progress_tracker.total_steps, "Complete"
        )
        success_html = UIComponents.get_success_html("Summary generated successfully!")
        final_html = progress_html + success_html

        yield final_html, final_summary

    except Exception as e:
        logger.error(f"Error in gradio_wrapper: {e}")
        error_html = UIComponents.get_error_html(
            f"An unexpected error occurred: {str(e)}"
        )
        yield error_html, None

    finally:
        try:
            if audio_path and os.path.exists(audio_path):
                tmp_dir = tempfile.gettempdir()
                # Only delete if it's inside the OS temp directory (i.e., a Gradio temp upload)
                if (
                    os.path.commonprefix([os.path.abspath(audio_path), tmp_dir])
                    == tmp_dir
                ):
                    cleanup_temp_file(audio_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup file {audio_path}: {e}")


async def voice_recognition_wrapper(
    comparison_audio_path: str,
    progress=gr.Progress(),
) -> AsyncGenerator[tuple[str, str | None], None]:
    """Run the voice recognition agent with progress feedback."""
    progress_tracker = ProgressTracker(total_steps=3)
    progress_tracker.steps = [
        "Preparing inputs...",
        "Processing audio...",
        "Identifying speaker...",
    ]

    try:
        if not comparison_audio_path.name:
            error_html = UIComponents.get_error_html(
                "Please upload the audio file you want to identify."
            )
            yield error_html, None
            return

        step_name, step_num = progress_tracker.next_step()
        progress_html = UIComponents.get_progress_html(
            step_num, progress_tracker.total_steps, step_name
        )
        status_html = UIComponents.get_status_html(
            "🚀 Starting voice recognition workflow..."
        )
        yield progress_html + status_html, None

        result = await voiceRecognitionAgent(
            comparison_audio_path.name,
        )

        events = result.get("events", [])
        if events:
            for index, event in enumerate(events, start=1):
                step_name, step_num = (
                    progress_tracker.next_step()
                    if progress_tracker.current_step < progress_tracker.total_steps
                    else (f"Event {index}", progress_tracker.current_step)
                )
                progress_html = UIComponents.get_progress_html(
                    min(step_num, progress_tracker.total_steps),
                    progress_tracker.total_steps,
                    step_name,
                )
                status_html = UIComponents.get_status_html(event)
                yield progress_html + status_html, None

        if result.get("success"):
            speakers = result.get("identified_speakers", [])

            final_html = UIComponents.get_success_html(
                f"Identified {len(speakers)} speaker(s)."
            )

            message_lines = [
                "### Voice Recognition Result",
                f"- **Total Speakers:** {len(speakers)}",
                "- **Identified Speakers:**",
            ]

            for spk in speakers:
                message_lines.append(f"  - `{spk}`")

            yield final_html, "\n".join(message_lines)
        else:
            error_message = result.get("error", "Speaker not recognized.")
            error_html = UIComponents.get_error_html(error_message)
            message_lines = [
                "### Voice Recognition Result",
                # f"- **Speaker Name:** `{speaker_name.strip()}`",
                f"- **Outcome:** {error_message}",
            ]
            yield error_html, "\n".join(message_lines)

    except Exception as e:
        logger.error(f"Error in voice_recognition_wrapper: {e}")
        error_html = UIComponents.get_error_html(f"An unexpected error occurred: {e}")
        yield error_html, None


def create_ui() -> gr.Blocks:
    """Create and configure the Gradio UI interface."""

    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    .file-upload {
        border: 2px dashed #d1d5db !important;
        border-radius: 8px !important;
    }
    .file-upload:hover {
        border-color: #3b82f6 !important;
        background-color: #f8fafc !important;
    }
    .btn-primary {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .btn-primary:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    .markdown-output {
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 16px !important;
        background-color: #fafafa !important;
    }
    """

    with gr.Blocks(
        title="🤖 Agentic Summarizer", theme=gr.themes.Soft(), css=custom_css
    ) as demo:
        # Header
        gr.Markdown("""
        # 🤖 Agentic Summarizer App
        
        Transform your meeting recordings into structured summaries with AI-powered transcription and analysis.
        
        **Supported formats:** MP3, WAV, M4A | **Max file size:** 50MB
        """)

        with gr.Tabs():
            with gr.TabItem("Meeting Summarizer"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # Input section
                        gr.Markdown("### 📁 Upload Audio File")
                        input_file = gr.File(
                            file_types=[".mp3", ".wav", ".m4a"],
                            label="Choose your meeting recording",
                            elem_classes=["file-upload"],
                        )

                        # Action button
                        summarize_btn = gr.Button(
                            "🚀 Generate Summary",
                            variant="primary",
                            elem_classes=["btn-primary"],
                            size="lg",
                        )

                        # Progress and status display
                        gr.Markdown("### 📊 Progress")
                        progress_and_status = gr.HTML(
                            value="<p style='color: #6b7280; text-align: center; margin: 20px 0;'>Ready to process your audio file...</p>"
                        )

                    with gr.Column(scale=2):
                        # Output section
                        gr.Markdown("### 📋 Meeting Summary")
                        formatted_output = gr.Markdown(
                            label="",
                            elem_classes=["markdown-output"],
                            value="*Your meeting summary will appear here after processing...*",
                        )

                gr.Markdown("""
                ---
                <div style="text-align: center; color: #6b7280; font-size: 14px; margin-top: 20px;">
                    <p>💡 <strong>Tip:</strong> For best results, use clear audio recordings with minimal background noise.</p>
                    <p>🔒 Your files are processed securely and are not stored permanently.</p>
                </div>
                """)

                summarize_btn.click(
                    fn=gradio_wrapper,
                    inputs=input_file,
                    outputs=[progress_and_status, formatted_output],
                    show_progress=False,
                )

                input_file.change(
                    fn=lambda: (
                        "<p style='color: #6b7280; text-align: center; margin: 20px 0;'>Ready to process your audio file...</p>",
                        "*Your meeting summary will appear here after processing...*",
                    ),
                    outputs=[progress_and_status, formatted_output],
                )

            with gr.TabItem("Voice Recognition"):
                gr.Markdown("### 🔍 Identify Speaker in New Audio")
                voice_comparison_file = gr.File(
                    file_types=[".mp3", ".wav", ".m4a"],
                    label="Audio to identify",
                    elem_classes=["file-upload"],
                )
                voice_recognize_btn = gr.Button(
                    "🔍 Identify Speaker",
                    variant="primary",
                    elem_classes=["btn-primary"],
                    size="lg",
                )
                voice_progress = gr.HTML(
                    value="<p style='color: #6b7280; text-align: center; margin: 20px 0;'>Ready to run voice recognition...</p>"
                )
                voice_output = gr.Markdown(
                    value="*Voice recognition results will appear here after processing...*",
                    elem_classes=["markdown-output"],
                )

                voice_recognize_btn.click(
                    fn=voice_recognition_wrapper,
                    inputs=[
                        voice_comparison_file,
                    ],
                    outputs=[voice_progress, voice_output],
                    show_progress=False,
                )

    return demo


def main():
    """Main function to launch the application."""
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        setup_logging(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),  # e.g., "/tmp/app.log"
        )
        logger.info("Starting Agentic Summarizer App...")

        # Create and launch the UI
        demo = create_ui()
        demo.queue()

        launch_kwargs = {
            "share": settings.GRADIO_SHARE,
            "server_name": "0.0.0.0" if settings.RUNNING_IN_SPACE else "127.0.0.1",
            "server_port": settings.PORT,
            "show_error": True,
            "quiet": False,
            "prevent_thread_lock": False,
            "inbrowser": False,
        }

        demo.launch(**launch_kwargs)

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main()
