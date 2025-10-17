from pydantic import BaseModel


class MeetingSummary(BaseModel):
    agenda: list[str] | None = None
    location: str | None = None
    date: str | None = None
    time: str | None = None
    duration: str | None = None
    participants: list[str] | None = None
    topics: list[str] | None = None
    summary: str | None = None
    key_points: list[str] | None = None
    action_items: list[str] | None = None
    next_steps: list[str] | None = None
    decisions: list[str] | None = None
    recommendations: list[str] | None = None
    follow_ups: list[str] | None = None
    questions: list[str] | None = None
    concerns: list[str] | None = None
    feedback: list[str] | None = None
    suggestions: list[str] | None = None
    improvements: list[str] | None = None
