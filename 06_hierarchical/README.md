# Project 6: Hierarchical Agent Teams

Startup idea validator with nested multi-agent teams.


## Graph

start -> market_research team (subgraph)
start -> technical_feasibility team (subgraph)
start -> financial team (subgraph)
combine results -> report_generator(node)
report_generator -> end

## Start

### market_research team:
- researcher (node) (uses tavily) (look for companies similar to our idea, explores market size, trends, competitors)
- validator (node) (uses llm knowledge) (it can ask the researcher to research again and provide more content, but the max iteration should be 3 i.e. we can't research more than 3 times)
- report_generator (node) (uses llm knowledge) (generates the final report)

class market_research_team:
    - final_report
    - research_output
    - validator_feedback
    - report_generator_output
    - max_iterations
    
start -> researcher node -> validator node (loop back to researcher node if validator requests more research, max 3 iterations) -> report generator node -> end

### technical_feasibility team:
- engineer (node) (uses llm knowledge) (analyzes if the idea is technicall feasible)
- validator (node) (uses llm knowledge) (be critical of the engineer and his analysis, can ask the engineer to analyze again and provide more refined content, but the max iteration should be 3 i.e. we can't analyze more than 3 times)
- report_generator (node) (uses llm knowledge) (generates the final report)

class technical_feasibility_team:
    - final_report
    - engineer_output
    - validator_feedback
    - report_generator_output
    - max_iterations
    
start -> engineer node -> validator node (loop back to engineer node if validator requests more analysis, max 3 iterations) -> report generator node -> end

### financial team:
- analyst (node) (uses llm knowledge) (analyzes the financial viability of the idea)
- validator (node) (uses llm knowledge) (be critical of the analyst and his analysis, can ask the analyst to analyze again and provide more refined content, but the max iteration should be 3 i.e. we can't analyze more than 3 times)
- report_generator (node) (uses llm knowledge) (generates the final report)

class financial_team:
    - final_report
    - analyst_output
    - validator_feedback
    - report_generator_output
    - max_iterations
    
start -> analyst node -> validator node (loop back to analyst node if validator requests more analysis, max 3 iterations) -> report generator node -> end

## Report Generator:
- generator (node) (uses llm knowledge) (generates the final report)

combines the final_report from all three subgraphs (nodes within this graph) and generates a final report. here we should wait for output from all three subgraphs before generating the final report.

## End