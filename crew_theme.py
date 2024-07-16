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

        crew = Crew(
                agents=[senior_researcher_agent],
                tasks=[inquiry_resolution],
                verbose=2,
                memory=True
                )

        result = crew.kickoff(inputs=inputs)
        print(result)
        return result
    
    def AI_summary(self, issues):
        load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

        inputs = {
            "issues": issues
        }
        senior_researcher_agent = Agent(
                    role="B2B Product Manager",
                    goal=("Your primary objective is to review a list of JIRA Server tickets that have not been updated in the last four days or are in a blocked status. Using your extensive knowledge, you will group these tickets by their root cause or area of concern. For this task, consider the summary, description, reporter, dates, priority, and labels of each ticket. Your goal is to:"
                        "Analyze each ticket and determine the underlying issues."
                        "Group tickets based on common problems or areas of concern."
                        "Provide a detailed summary for each group, explaining the common issue and relevant details."
                        "Add specific justifications for the grouping on each ticket, leveraging your deep expertise to provide clear and actionable feedback."),
                    backstory=(
                        "Act as a brilliant software architect with deep expertise in b2b software.  Here is a list of JIRA Server tickets that haven't been updated in "
                        "4 days or are in blocked status. I would like you to review this list and group the tickets by root cause or area of concern. To do this "
                        "grouping, please consider the following fields for each ticket: key, summary, description, reporter, dates, and priority. Please group these "
                        "tickets based on their root cause or area of concern, considering the provided fields. For each group, provide a summary that explains"
                        " the common issue and any relevant details. Please add specific justification for the grouping on each ticket."
                    ),
                    allow_delegation=False,
                    verbose=True,
                    # tools = [jira_api_tool]
                )
        inquiry_resolution = Task(
                    description=(
                        "As a brilliant software architect with deep expertise in B2B software, your task is to review a list of JIRA Server tickets that haven't been updated in the last four days or are currently in a blocked status. Your goal is to categorize these tickets by their root cause or area of concern. To perform this grouping, consider the following fields for each ticket: summary, description, reporter, dates, and priority."
                        "Review the provided list of JIRA Server tickets."
                        "Analyze the key, summary, description, reporter, dates, priority, and labels of each ticket."
                        "Group the tickets based on their root cause or area of concern."
                        "Provide a detailed summary for each group, explaining the common issue and any relevant details."
                        "Add specific justifications for the grouping on each ticket."
                        "When reporting the key, it should be a hyperlink. Put it in the exact HTML text format of the following: key + ': ' + '<a href=' + 'https://issues.onenetwork.com/browse/' + key + '>' + key + '</a>'."
                        f"Here are the reports for you to analyze in a list with each element (issue) being in JSON format missing the curly brackets: {issues}"
                    ),
                    expected_output=(
                        "A categorized list of JIRA Server tickets grouped by their root cause or area of concern."
                        "A detailed summary for each group that explains the common issue and provides relevant details."
                        "Specific justifications for the grouping on each ticket, demonstrating a clear understanding of the root cause or area of concern.\n"
                        "Your response should be in HTML text. Follow the format below and make them bullet points in HTMl respecting the break lines and tabs. Include the tabs and breaklines in the HTML text:\n"
                        "Group 1: [Common Issue]\n"
                        "   Summary: [Explanation of the common issue]\n"
                        "   Tickets:\n"
                        "       Ticket 1: [Key, Summary, Description, Reporter, Dates, Priority, Labels, Justification]\n"
                        "       Ticket 2: [Key, Summary, Description, Reporter, Dates, Priority, Labels, Justification]\n"
                        "       ...\n"
                        "Group 2: [Common Issue]\n"
                        "   Summary: [Explanation of the common issue]\n"
                        "   Tickets:\n"
                        "       Ticket 1: [Key, Summary, Description, Reporter, Dates, Priority, Labels, Justification]\n"
                        "       Ticket 2: [Key, Summary, Description, Reporter, Dates, Priority, Labels, Justification]\n"
                        "       ...\n"
                        "Your final answer must include a comprehensive and organized list of categorized tickets with detailed justifications for each grouping."
                        "Ensure that the key is a hyperlink with the link to the JIRA ticket. The link will follow the format: https://issues.onenetwork.com/browse/[key] where [key] is the ticket key."
                        "Also ensure that the response is in HTML format with the correct tabs and breaklines for readability. Make sure that each part of each ticket gets its own bullet point."
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
        return result