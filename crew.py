from crewai import Agent, Task, Crew
from jira_tool import JiraTool
from query_api import JiraApi
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
serper_api_key = os.getenv('SERPER_API_KEY')
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

# jira_api_tool = JiraTool()
jira_api_tool = JiraApi()
context = jira_api_tool.get_issues()

inputs = {
    "context": context
}

senior_researcher_agent = Agent(
            role="Senior Company Researcher/Customer Service Specialist",
            goal=("From the JSON provided to you, identify 'blocked' issues:"
            "whether its by using the blocked flag"
            "or by using strong emotion in the comments"
            "or by the issue not being touched in N days (start with N=4)"
            "or other ideas"),
            backstory=(
                "You are a Senior Company Researcher and "
                " are now working on providing "
                "research to your customer, a super important customer "
                " to you."
                "You need to make sure that you provide the best research and find all necessary information!"
                "Make sure to provide every issue that is being blocked. In your response, ensure that the issue"
                " ID is included before every issue that you list."
            ),
            allow_delegation=False,
            verbose=True,
            # tools = [jira_api_tool]
        )
inquiry_resolution = Task(
            description=(
                "Your customer just reached out with a super important ask. Find every blocked issue from the JSON you are given."
                "Make sure to use everything you know "
                "to provide the best answers possible."
                "You must strive to provide a complete "
                "and accurate response to the customer's inquiry."
                f"Here is the JSON for you to analyze: {context}"
            ),
            expected_output=(
                "A list of issues that meets the requirements stated by your customer."
                "Ensure that the issue ID is included before every issue that you list."
            ),
            agent=senior_researcher_agent,
        )
crew = Crew(
        agents=[senior_researcher_agent],
        tasks=[inquiry_resolution],
        verbose=2,
        memory=True
        )

result = crew.kickoff(inputs=inputs)
print(result)