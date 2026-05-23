from typing import TypedDict

class ContentState(TypedDict):
    topic: str
    research: str
    draft: str
    editor_feedback: str
    seo_output: str
    current_agent: str
    iteration_count: int
    research_count: int
    final_post: str


