from crewai import Agent, Task, Crew
# from jira_tool import JiraTool
# from query_api import JiraApi
from dotenv import load_dotenv
import os


class ThemeCrew:
    def __init__(self):
        pass
    def problem_identifier(self, context):
        load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')
        serper_api_key = os.getenv('SERPER_API_KEY')
        os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o'
        os.environ["OPENAI_API_KEY"] = openai_api_key

        inputs = {
            "context": context
        }

        # senior_researcher_agent = Agent(
        #             role="B2B Product Manager",
        #             goal=("Analyze customer feedback and production tickets to identify common themes, areas for product enhancements, and"
        #                 "prioritize them based on urgency and potential impact. Then provide a list of ticet keys that created each theme."),
        #             backstory=(
        #                 "You are an expert B2B product manager with extensive experience in analyzing customer feedback and production tickets"
        #                 "to identify common themes and areas for product enhancements. Your task is to review a set of customer production tickets and report all the keys you see."
        #                 f"Do not make up any keys and ensure and verify that the keys are in the JSON data. A key will appear after a '\"key\":'. Here is the JSON data where you can find the keys: {context}"
        #             ),
        #             allow_delegation=False,
        #             verbose=True,
        #             # tools = [jira_api_tool]
        #         )
        # inquiry_resolution = Task(
        #             description=(
        #                 "You are an expert B2B product manager with extensive experience in analyzing customer feedback and production tickets"
        #                 "to identify common themes and areas for product enhancements. Your task is to review a set of customer production tickets and report all the keys you see. Here is the JSON for you to analyze. : {context}"
        #             ),
        #             expected_output=(
        #                 f"A list of ticket keys that was found from the JSON data: {context}.\n Verify that the keys (not IDs) are present in the JSON data and do not make any up."
        #             ),
        #             agent=senior_researcher_agent,
        #         )

        senior_researcher_agent = Agent(
                    role="B2B Product Manager",
                    goal=("Analyze customer feedback and production tickets to identify common themes, areas for product enhancements, and"
                        "prioritize them based on urgency and potential impact. Then provide a list of ticet keys that created each theme."),
                    backstory=(
                        "You are an expert B2B product manager with extensive experience in analyzing customer feedback and production tickets"
                        "to identify common themes and areas for product enhancements. Your task is to review a set of customer production tickets by looking at the summary and description"
                        "and provide a detailed analysis, focusing on:"
                        "Common Themes: Identify recurring issues or requests mentioned across multiple tickets."
                        "Enhancement Opportunities: Highlight specific areas where product enhancements can address these common themes."
                        "User Impact: Explain how these enhancements will improve the user experience and benefit the business."
                        "Prioritization: Suggest a prioritization order for addressing these enhancements based on urgency and potential impact."
                        "For each identified theme or enhancement, provide detailed feedback including:"
                        "Problem Statement: What is the recurring issue or request?"
                        "Proposed Enhancement: What specific changes or additions should be made to the product?"
                        "Expected Benefits: How will these changes improve the product for users and the business?"
                        "Issue Keys: Keep track of the issue keys that created each theme."
                        "Take it step by step. Before answering, compare the results to the issue keys provided. DO NOT MAKE UP KEYS. Ensure that you only consider legitimate keys present in the provided JSON data."
                        "Validate the presence of these keys in the JSON before including them in your analysis."
                    ),
                    allow_delegation=False,
                    verbose=True,
                    # tools = [jira_api_tool]
                )
        inquiry_resolution = Task(
                    description=(
                        "You are an expert B2B product manager with extensive experience in analyzing customer feedback and production tickets to identify"
                        "common themes and areas for product enhancements. Your task is to review a set of customer production tickets by looking at the summary and description and provide a detailed analysis, focusing on:"
                        "Common Themes: Identify recurring issues or requests mentioned across multiple tickets."
                        "Enhancement Opportunities: Highlight specific areas where product enhancements can address these common themes."
                        "User Impact: Explain how these enhancements will improve the user experience and benefit the business."
                        "Prioritization: Suggest a prioritization order for addressing these enhancements based on urgency and potential impact."
                        f"In each issue in the JSON there is a key, summary, and description. Remember the value in the keys field that helped you create each theme so you can report on it."
                        f"Ensure that you only consider and include legitimate keys present in the provided JSON data. The key would be after the phrase (\"key\":). The JSON will be missing the curly braces in it."
                        "Here is the JSON for you to analyze. : {context}"
                    ),
                    expected_output=(
                        "For each identified theme or enhancement, provide the issues/keys that created the detailed feedback including:"
                        "Problem Statement: What is the recurring issue or request?"
                        "Proposed Enhancement: What specific changes or additions should be made to the product?"
                        "Expected Benefits: How will these changes improve the product for users and the business?"
                        "Issue Keys: Keep track of the issue keys that created each theme - list of validated JSON keys used in the analysis."
                        "Take it step by step. Before answering, compare the results to the issue keys provided. DO NOT MAKE UP KEYS. Ensure that you only consider legitimate keys present in the provided JSON data."
                        "Validate the presence of these keys in the JSON before including them in your analysis. Provide a valid output that doesn't break OpenAI and raise errors."
                        #"Keep your final response to less than 1300 tokens."
                    ),
                    agent=senior_researcher_agent,
                )
        
        # verifier_agent = Agent(
        #             role="Quality Assurance Analyst",
        #             goal=("Ensure that all the keys provided in the output are present in the JSON data."),
        #             backstory=(
        #                 "You are an expert quality assurance agent with extensive experience in validating data and ensuring its accuracy."
        #                 "Your task is to review the output provided by the B2B Product Manager and verify that all the keys mentioned in the output are present in the JSON data."
        #                 f"I want you to analyze the issue keys not ids. Here is the JSON for you to analyze: {context}"
        #             ),
        #             allow_delegation=False,
        #             verbose=True,
        #             # tools = [jira_api_tool]
        #         )
        # verifier_resolution = Task(
        #             description=(
        #                 "You are an expert quality assurance agent with extensive experience in validating data and ensuring its accuracy."
        #                 "Your task is to review the output provided by the B2B Product Manager and verify that all the keys mentioned in the output are present in the JSON data."
        #                 f"Ensure that you only consider and include legitimate keys present in the provided JSON data. Here is the JSON for you to analyze: {context}"
        #             ),
        #             expected_output=(
        #                 "If there are keys not present in the JSON data given by the B2B Product Manager, go back to the B2B Product Manager and ask them to provide the correct keys."
        #             ),
        #             agent=verifier_agent,
        #         )

        crew = Crew(
                agents=[senior_researcher_agent],
                tasks=[inquiry_resolution],
                verbose=2,
                memory=True
                )

        result = crew.kickoff(inputs=inputs)
        print(result)
        return result
    
    def synthesize(self, context):
        load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')
        serper_api_key = os.getenv('SERPER_API_KEY')
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

        inputs = {
            "context": context
        }
        senior_researcher_agent = Agent(
                    role="B2B Product Manager",
                    goal=("Synthesize all the reports you are given into one big report. Make sure to include all information given to you and do not lose any information."),
                    backstory=(
                        "You are an expert B2B product manager with extensive experience in analyzing customer feedback and production tickets"
                        "to identify common themes and areas for product enhancements. Your task is to combine all the reports you are given into one singular report."
                    ),
                    allow_delegation=False,
                    verbose=True,
                    # tools = [jira_api_tool]
                )
        inquiry_resolution = Task(
                    description=(
                        "You are an expert B2B product manager with extensive experience in analyzing customer feedback and production tickets"
                        "to identify common themes and areas for product enhancements. Your task is to combine all the reports you are given into one singular report."
                        f"Here are the reports for you to combine into one: {context}"
                    ),
                    expected_output=(
                        "One combined report that includes all the information from the reports given to you. Make sure to include all information given to you and do not lose any information."
                    ),
                    agent=senior_researcher_agent,
                )
        
        # verifier_agent = Agent(
        #             role="Quality Assurance Analyst",
        #             goal=("Ensure that all the keys provided in the output are present in the JSON data."),
        #             backstory=(
        #                 "You are an expert quality assurance agent with extensive experience in validating data and ensuring its accuracy."
        #                 "Your task is to review the output provided by the B2B Product Manager and verify that all the keys mentioned in the output are present in the JSON data."
        #                 f"I want you to analyze the issue keys not ids. Here is the JSON for you to analyze: {context}"
        #             ),
        #             allow_delegation=False,
        #             verbose=True,
        #             # tools = [jira_api_tool]
        #         )
        # verifier_resolution = Task(
        #             description=(
        #                 "You are an expert quality assurance agent with extensive experience in validating data and ensuring its accuracy."
        #                 "Your task is to review the output provided by the B2B Product Manager and verify that all the keys mentioned in the output are present in the JSON data."
        #                 f"Ensure that you only consider and include legitimate keys present in the provided JSON data. Here is the JSON for you to analyze: {context}"
        #             ),
        #             expected_output=(
        #                 "If there are keys not present in the JSON data given by the B2B Product Manager, go back to the B2B Product Manager and ask them to provide the correct keys."
        #             ),
        #             agent=verifier_agent,
        #         )

        crew = Crew(
                agents=[senior_researcher_agent],
                tasks=[inquiry_resolution],
                verbose=2,
                memory=True
                )

        result = crew.kickoff(inputs=inputs)
        print(result)
        return result