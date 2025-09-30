from typing import Union
from pydantic import BaseModel
from typing import List, Optional
from models.meeting_schema import MeetingSummary


def generate_markdown_summary(summary: Union[MeetingSummary, dict]) -> str:
    if isinstance(summary, dict) and "properties" in summary:
            summary_obj = MeetingSummary(**summary["properties"])
    elif isinstance(summary, dict):
            summary_obj = MeetingSummary(**summary)        
    
    def format_list(items: List[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "**Not Specified**"

    def format_str(item: Optional[str]) -> str:
        return item if item else "**Not Specified**"

    md = f"""
# 📋 Meeting Summary

**📅 Date:** {format_str(summary_obj.date)}  
**📍 Location:** {format_str(summary_obj.location)}  
**⏰ Time:** {format_str(summary_obj.time)}  
**🕒 Duration:** {format_str(summary_obj.duration)}

---

## 📝 Agenda
{format_list(summary_obj.agenda)}

## 👥 Participants
{format_list(summary_obj.participants)}

## 🧠 Topics Discussed
{format_list(summary_obj.topics)}

## 🧾 Summary
> {format_str(summary_obj.summary)}

## 📌 Key Points
{format_list(summary_obj.key_points)}

## ✅ Action Items
{format_list(summary_obj.action_items)}

## 🔜 Next Steps
{format_list(summary_obj.next_steps)}

## 🧑‍⚖️ Decisions
{format_list(summary_obj.decisions)}

## 💡 Recommendations
{format_list(summary_obj.recommendations)}

## 🔁 Follow Ups
{format_list(summary_obj.follow_ups)}

## ❓ Questions
{format_list(summary_obj.questions)}

## 😟 Concerns
{format_list(summary_obj.concerns)}

## 🗣️ Feedback
{format_list(summary_obj.feedback)}

## 💬 Suggestions
{format_list(summary_obj.suggestions)}

## 🛠️ Improvements
{format_list(summary_obj.improvements)}
"""
    return md;
    # return Markdown(md)

# 🧪 Example usage:
# display(generate_markdown_summary(summary_data))
