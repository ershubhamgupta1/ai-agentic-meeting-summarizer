from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from config.settings import settings
from utils.openai_client import OpenAIClient
from models.meeting_schema import MeetingSummary

load_dotenv()  # Load environment variables from .env
client = OpenAIClient().client

def summaryTool(text: str) -> str:
    """
    You are a meeting summarizer. You will be given a meeting transcript and you will need to summarize the meeting, don't ask further questions.   
    """
    schema = MeetingSummary.model_json_schema()
    schemaData = {json.dumps(schema, indent=2)}

    systemPrompt = f"""
            You are a meeting summarizer. You will be given a meeting transcript.
            Your task is to generate a strict JSON summary of a meeting, following this JSON schema exactly:

            {schemaData}
            if any of the schema fields are not available then either return None or [] depends upon schema type.
            Please respond with **valid JSON only**. Do not include any explanation, markdown, or commentary and don't ask further questions. Do not wrap the JSON in code blocks. Only the raw JSON object should be returned.
            """

    print('ready to call summary tool!!!');

    # Optionally validate it's proper JSON
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            messages=[
                {
                    "role": "system",
                    "content": systemPrompt
                },
                {
                    "role": "user",
                    "content": f"Here is the meeting transcript: {text}"
                }
            ]
        )
        content = response.choices[0].message.content.strip()
        # ✅ Parse JSON from the string
        summary_data = json.loads(content)
        summary_data = json.loads({"properties": {"agenda": {"items": ["Progress on the onboarding flow", "Updates on the analytics dashboard", "Status of customer feedback processing"], "title": "Agenda", "type": "array"}, "location": {"anyOf": [{"type": "string", "value": "Online"}, {"type": "None"}], "title": "Location"}, "date": {"anyOf": [{"type": "string", "value": "Not specified"}, {"type": "None"}], "title": "Date"}, "time": {"anyOf": [{"type": "string", "value": "Not specified"}, {"type": "None"}], "title": "Time"}, "duration": {"anyOf": [{"type": "string", "value": "Not specified"}, {"type": "None"}], "title": "Duration"}, "participants": {"items": ["John", "Sarah", "Raj", "Lisa"], "title": "Participants", "type": "array"}, "topics": {"items": ["Onboarding flow progress", "Analytics dashboard updates", "Customer feedback processing status"], "title": "Topics", "type": "array"}, "summary": {"title": "Summary", "type": "string", "value": "The team discussed the progress of various tasks. Sarah is finishing the onboarding flow, Raj is fixing bugs in the analytics dashboard, and Lisa is preparing a summary report of customer feedback."}, "key_points": {"items": ["Sarah finished the UI components for the onboarding flow", "Raj is fixing bugs with dynamic filtering in the analytics dashboard", "Lisa has categorized about 300 customer responses"], "title": "Key Points", "type": "array"}, "action_items": {"items": ["Sarah to integrate UI components with the backend and complete testing", "Raj to fix bugs and pass the dashboard to Ka", "Lisa to prepare a summary report of customer feedback"], "title": "Action Items", "type": "array"}, "next_steps": {"items": ["Wrap up all tasks before Friday"], "title": "Next Steps", "type": "array"}, "decisions": {"items": [], "title": "Decisions", "type": "array"}, "recommendations": {"items": [], "title": "Recommendations", "type": "array"}, "follow_ups": {"items": [], "title": "Follow Ups", "type": "array"}, "questions": {"items": [], "title": "Questions", "type": "array"}, "concerns": {"items": [], "title": "Concerns", "type": "array"}, "feedback": {"items": [], "title": "Feedback", "type": "array"}, "suggestions": {"items": [], "title": "Suggestions", "type": "array"}, "improvements": {"items": [], "title": "Improvements", "type": "array"}}, "required": ["agenda", "location", "date", "time", "duration", "participants", "topics", "summary", "key_points", "action_items", "next_steps", "decisions", "recommendations", "follow_ups", "questions", "concerns", "feedback", "suggestions", "improvements"], "title": "MeetingSummary", "type": "object"});
        return {"properties": {"agenda": ["Onboarding flow progress", "Analytics dashboard update", "Customer feedback processing"], "location": None, "date": None, "time": None, "duration": None, "participants": ["John", "Sarah", "Raj", "Lisa"], "topics": ["Onboarding flow", "Analytics dashboard", "Customer feedback"], "summary": "The team discussed the progress of various tasks. Sarah is integrating the UI components with the backend and testing should be done by tomorrow. Raj is fixing bugs with dynamic filtering in the analytics dashboard. Lisa has categorized about 300 customer responses and will prepare a summary report by end of day. The aim is to wrap all tasks up before Friday.", "key_points": ["Sarah finished the UI components for the onboarding flow", "Raj is fixing bugs in the analytics dashboard", "Lisa has categorized 300 customer responses"], "action_items": ["Sarah to integrate UI components with backend and complete testing", "Raj to fix bugs in analytics dashboard", "Lisa to prepare summary report of customer feedback"], "next_steps": ["Sarah to complete testing of onboarding flow", "Raj to fix bugs and pass the dashboard to Ka", "Lisa to prepare customer feedback summary report"], "decisions": ["All tasks to be wrapped up before Friday"], "recommendations": [], "follow_ups": [], "questions": [], "concerns": [], "feedback": [], "suggestions": [], "improvements": []}, "title": "MeetingSummary", "type": "object"};
        return summary_data  # ensure it's valid JSON
    except json.JSONDecodeError:
        raise ValueError("Response from model is not valid JSON")