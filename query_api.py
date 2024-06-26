import os
import requests
from getpass import getpass
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
import re  # Regular expression library for simple keyword/emotion detection
import json
import pandas as pd

class JiraApi:
    def __init__(self):
        pass
    def get_issues(self):
        # JIRA API details
        jira_url = 'https://issues.onenetwork.com'  # Replace with your JIRA URL
        # Endpoint below only displays 50 issues.
        api_endpoint = '/rest/api/2/search?jql=filter=45133'
        # username = input("Enter JIRA username: ")  # Prompting the user for JIRA username
        # password = getpass("Enter JIRA password: ")  # Securely prompting for JIRA password
        maxResults_endpoint = '&maxResults='

        load_dotenv()
        jira_api_key = os.getenv('JIRA_API_KEY')
        token = jira_api_key
        headers = {
            "Authorization": "Bearer " + f"{token}",
            "Content-Type": "application/json"
        }

        # Send a request to JIRA to retrieve issues
        response = requests.get(jira_url + api_endpoint + maxResults_endpoint + '1', headers=headers)

        # Send a new request to JIRA to retrieve ALL issues
        maxResults = response.json().get('total', [])
        response = requests.get(jira_url + api_endpoint + maxResults_endpoint + f'{maxResults}', headers=headers)

        # print(response.json())
        # print(response.status_code)

        # Code below to remove null values
        # output = self.remove_nulls(response.json())

        output = response.json()
        
        # Define the keys you want to keep
        keys_to_keep = {'id', 'key', 'lastViewed', 'issuelinks', 'issuetype', 'updated', 'summary', 'priority', 'status', 'created', 'description'}

        # Filter the data
        # filtered_data = [{k: v for k, v in issue['fields'].items() if k in keys_to_keep} for issue in output['issues']]
        filtered_data = [
            {
                **{k: v for k, v in issue.items() if k in keys_to_keep},  # Include all top-level key-value pairs except 'fields'
                'fields': {k: v for k, v in issue['fields'].items() if k in keys_to_keep}  # Filtered 'fields' dictionary
            }
            for issue in output['issues']
        ]

        output['issues'] = filtered_data
        
        """Below code would be used to filter base issue based on status."""
        # # The value in the sub-dictionary that determines if the main dictionary is kept
        # status_to_keep = {'open'}

        # status_filtered_data = [
        #     issue for issue in output['issues']
        #     if issue['fields'].get('status') == status_to_keep
        # ]

        print(output)

        """Below code would be used to make an excel sheet based on the JSON"""
        # # Making an excel file and create a DataFrame
        # df = pd.DataFrame(output['issues'])
        # # Write DataFrame to Excel file
        # df.to_excel('outputdata.xlsx', index=False, engine='openpyxl')

        # Specify the file path and mode
        file_path = 'output.txt'  # Change 'output.txt' to your desired file path

        # Open the file and write the output
        with open(file_path, 'w', encoding='utf-8') as file:
            json_output = json.dump(output, file, ensure_ascii=False, indent=4) # Convert the dictionary to string before writing
        
        self.filter_issues(output)
        
        return json_output
    
    """
        Filters the issues to keep only values that are not null

        Args:
        data (dict): The dictionary containing the json.

        Returns:
        dict: A filtered dictionary.
    """
    def remove_nulls(self, data):
        if isinstance(data, dict):
            return {k: self.remove_nulls(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self.remove_nulls(item) for item in data if item is not None]
        else:
            return data
        
    """
        Filters the issues to keep only those that contain the blocked status or hasn't
        been touched in 4 days in any issue given by the JSON.

        Args:
        data (dict): The dictionary containing the key 'issues', which is a list of issues.

        Returns:
        list: A list of filtered issues that meet the requirements.
    """
    def filter_issues(self, data):
        filtered_issues = []

        # Iterate over each issue in the list of issues
        for issue in data.get('issues', []):
            # Retrieve information
            main_status = issue.get('fields', {}).get('status', {})
            date = issue.get('fields', {}).get('updated', {})
            # Check if it hasn't been updated in 4 days
            if self.is_older_than_four_days(date, 4):
                filtered_issues.append(issue.get('key', {}))
            # Check if the status is set as blocked
            elif main_status == "Blocked":
                filtered_issues.append(issue.get('key', {}))

            # Navigate to the 'issuelinks' sub-dictionary
            issuelinks = issue.get('fields', {}).get('issuelinks', {})
            
            for link_issue in issuelinks:
                # Check for 'inwardIssue' and 'outwardIssue' keys within 'issuelinks'
                similar_issue = self.get_issue_value(link_issue)
                status = similar_issue.get('fields', {}).get('status', {}).get('name', {})
                
                # If status is blocked add it
                if status == "Blocked":
                    filtered_issues.append(similar_issue.get('key', {}))
        print(filtered_issues)
        
        return filtered_issues
    
    """
        Retrieves the value of the issue key from the dictionary.

        Args:
        data (dict): The dictionary to search.
        default: The default value to return if neither key is found.

        Returns:
        The value corresponding to the issue key or the default value.
    """
    def get_issue_value(self, link_issue, default=None):
        return link_issue.get('outwardIssue') or link_issue.get('inwardIssue') or default
    
    """
        Checks if the given date string is older than four days from the current date.

        Args:
        date_str (str): The date string to check, in the format 'YYYY-MM-DDTHH:MM:SS.sssZ'.
        n_days (int): Amount of days to check is older than

        Returns:
        bool: True if the date is older than amount of days given, False otherwise.
    """
    def is_older_than_four_days(self, date_str, n_days):
        # Define the date format
        date_format = '%Y-%m-%dT%H:%M:%S.%f%z'
        
        # Parse the date string into a datetime object
        parsed_date = datetime.strptime(date_str, date_format)
        
        # Get the current date and time with timezone information
        current_date = datetime.now(pytz.timezone('UTC'))

        # Calculate the difference between the current date and the parsed date
        difference = current_date - parsed_date

        # Check if the difference is greater than or equal to four days
        return difference >= timedelta(days=n_days)
    
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