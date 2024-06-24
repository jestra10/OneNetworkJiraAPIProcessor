import os
import requests
from getpass import getpass
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re  # Regular expression library for simple keyword/emotion detection
import json

class JiraApi:
    def __init__(self):
        pass
    def get_issues(self):
        # JIRA API details
        jira_url = 'https://issues.onenetwork.com'  # Replace with your JIRA URL
        api_endpoint = '/rest/api/2/search?jql=filter=45133'
        # username = input("Enter JIRA username: ")  # Prompting the user for JIRA username
        # password = getpass("Enter JIRA password: ")  # Securely prompting for JIRA password

        load_dotenv()
        jira_api_key = os.getenv('JIRA_API_KEY')
        token = jira_api_key
        headers = {
            "Authorization": "Bearer " + f"{token}",
            "Content-Type": "application/json"
        }

        # Send a request to JIRA to create an issue
        response = requests.get(jira_url + api_endpoint, headers=headers)

        # print(response.json())
        print(response.status_code)
        output = self.remove_nulls(response.json())
        
        # Define the keys you want to keep
        keys_to_keep = {'lastViewed', 'issuelinks', 'issuetype', 'updated', 'summary', 'priority', 'status', 'created', 'description'}

        # Filter the data
        filtered_data = [{k: v for k, v in issue['fields'].items() if k in keys_to_keep} for issue in output['issues']]
        print("Filtered data sample:", filtered_data[:5])  # Print first 5 to see what's getting through
        # print(output['issues'][0])
        output['issues'] = filtered_data
        
        print(output)
        # Specify the file path and mode
        file_path = 'output.txt'  # Change 'output.txt' to your desired file path

        # Open the file and write the output
        with open(file_path, 'w', encoding='utf-8') as file:
            json_output = json.dump(output, file, ensure_ascii=False, indent=4) # Convert the dictionary to string before writing
        # hey
        return json_output

    def remove_nulls(self, data):
        if isinstance(data, dict):
            return {k: self.remove_nulls(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self.remove_nulls(item) for item in data if item is not None]
        else:
            return data
    
    """
    Commented code below this is an example of how to do it manually,
    would have to change the fields it accesses in the JSON however to make it work.
    """
    # Function to check if an issue is blocked
    # def is_blocked(issue):
    #     # Define the threshold for days untouched
    #     days_untouched = 4

    #     # Get today's date
    #     today = datetime.now()

    #     # Check for blocked flag
    #     if issue['status'] == 'blocked':
    #         return True
        
    #     # Check for strong emotion in comments
    #     emotion_keywords = ['urgent', 'immediately', 'critical', 'emergency']
    #     for comment in issue['comments']:
    #         if any(word in comment.lower() for word in emotion_keywords):
    #             return True
        
    #     # Check if the issue has not been touched in N days
    #     last_updated_date = datetime.strptime(issue['last_updated'], '%Y-%m-%d')
    #     if (today - last_updated_date).days >= days_untouched:
    #         return True
        
    #     return False

    # def filter_blocked(self, issues):
    #     # Filter issues that are blocked
    #     blocked_issues = [issue for issue in issues if self.is_blocked(issue)]

    #     # Print blocked issues
    #     print(blocked_issues)

if __name__ == "__main__":
    jira_api = JiraApi()  # Create an instance of the JiraApi class
    issues = jira_api.get_issues()  # Call the get_issues method
    # print(issues)  # Print the issues retrieved