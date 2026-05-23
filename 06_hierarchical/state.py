from typing import TypedDict


class MarketResearchState(TypedDict):
    startup_idea: str
    search_results: str
    research_output: str
    validator_feedback: str
    validator_status: str
    final_report: str
    iteration_count: int


class TechnicalFeasibilityState(TypedDict):
    startup_idea: str
    engineer_output: str
    validator_feedback: str
    validator_status: str
    final_report: str
    iteration_count: int


class FinancialState(TypedDict):
    startup_idea: str
    analyst_output: str
    validator_feedback: str
    validator_status: str
    final_report: str
    iteration_count: int


class OverallState(TypedDict):
    startup_idea: str
    market_research_report: str
    technical_feasibility_report: str
    financial_report: str
    final_report: str
