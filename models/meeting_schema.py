from typing import List, Optional
from pydantic import BaseModel

class MeetingSummary(BaseModel):
    agenda: Optional[List[str]] = None
    location: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    duration: Optional[str] = None
    participants: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    decisions: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    follow_ups: Optional[List[str]] = None
    questions: Optional[List[str]] = None
    concerns: Optional[List[str]] = None
    feedback: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
