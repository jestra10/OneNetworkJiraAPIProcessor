from crewai_tools import BaseTool
from query_api import JiraApi

class JiraTool(BaseTool):
    name: str ="JIRA API tool"
    description: str = ("Uses the JIRA API to get information from JIRA."
                        "Use this tool to get information from JIRA."
                        )
    
    def _run(self) -> str:
        # Your custom code tool goes here
        jira_api = JiraApi()
        result = jira_api.get_issues()
        return result