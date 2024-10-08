#!/home/jestra10/JQLv2/.venv/Scripts/python.exe
import os
import requests
import math
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
import re  # Regular expression library for simple keyword/emotion detection
import json
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from postmarker.core import PostmarkClient
from crew_theme import ThemeCrew

class JiraApi:
    def __init__(self):
        pass
    """
    This method retrieves the issues from JIRA and uses CrewAI to identify and summarize themes in the issues.
    It will print the out the final result and write it to a file.

    Args:

    Returns:
        str: The final result of the themes identified and summarized
    """
    def identify_themes(self):
        # JIRA API base url
        jira_url = 'https://issues.onenetwork.com'
        # Endpoint below only displays 50 issues
        api_endpoint = '/rest/api/2/search?jql=filter=45133'
        maxResults_endpoint = '&maxResults='

        # Load the JIRA API key from the .env file
        load_dotenv()
        jira_api_key = os.getenv('JIRA_API_KEY')
        token = jira_api_key
        headers = {
            "Authorization": "Bearer " + f"{token}",
            "Content-Type": "application/json"
        }

        try:
            # Send a request to JIRA to retrieve number of issues
            response = requests.get(jira_url + api_endpoint + maxResults_endpoint + '1', headers=headers)

            # Send a new request to JIRA to retrieve ALL issues
            maxResults = response.json().get('total', [])
            response = requests.get(jira_url + api_endpoint + maxResults_endpoint + f'{maxResults}', headers=headers)
        except:
            print("Error retrieving JSON from JIRA")
            return

        output = response.json()
        
        # Define the keys you want to keep
        keys_to_keep = {'key', 'summary', 'description'}#, 'issuelinks'}

        # Filter the data to keep only the keys you want
        try: 
            filtered_data = [
                {
                    **{k: v for k, v in issue.items() if k in keys_to_keep},  # Include all top-level key-value pairs except 'fields'
                    'fields': {k: v for k, v in issue['fields'].items() if k in keys_to_keep}  # Filtered 'fields' dictionary
                }
                for issue in output['issues']
                if "LN" in issue.get('key', {}) #or "LN" in self.helper_identify_themes(issue) #this gets based issues but not linked issues look into it
            ]
            output['issues'] = filtered_data
        except:
            print("Error trying to filter certain keys throughout whole JSON")

        # Specify the file path and mode
        file_path = 'output_theme.txt'  # Change 'output.txt' to your desired file path

        # Open the file and write the output to check if the above filtering worked
        with open(file_path, 'w', encoding='utf-8') as file:
            json_output = json.dump(output, file, ensure_ascii=False, indent=4) # Convert the dictionary to string before writing
        
        length_segment = round(len(output['issues'])/6)
        theme_crew = ThemeCrew()
        results = []
        for i in range(6):
            if i == 0:
                start = 0
            else:
                start = (length_segment * i) + 1
            end = length_segment * (i + 1)
            issues = output['issues'][start:end]
            readable_output = json.dumps(issues, indent=4)
            cleaned_string = re.sub(r'[{}]', '', readable_output)
            result = theme_crew.problem_identifier(cleaned_string)
            results.append(result)
            # self.write_to_file(result, "Outputs/output"+str(i+1)+"4.txt")

        final_result = theme_crew.synthesize('\n'.join(results))
        print(final_result)
        # self.write_to_file(final_result, 'Outputs/final4.txt')
        # Specify the file path
        file_path = 'Outputs/final4.txt'
        # Open the file in write mode and write the string to the file
        with open(file_path, 'w') as file:
            file.write(final_result)
        return final_result
    
    """
    This is a helper method that writes the data to a file.

    Args:
        str: The data to write to the file
        str: The file path to write the data to

    Returns:
    """
    def write_to_file(self, data, file_path):
        with open(file_path, 'w') as file:
            file.write(data)

    def helper_identify_themes(self, issue):
        try:
            issue_links = issue.get('fields', {}).get('issuelinks', {})
        except:
            issue_links = []
        keys = ""
        for link_issue in issue_links:
            # Check for 'inwardIssue' and 'outwardIssue' keys within 'issuelinks'
            similar_issue = self.get_issue_value(link_issue)
            try:
                keys = keys + similar_issue.get('key', {})
            except:
                keys = keys
        return keys
    
    def get_issues(self):
        # JIRA API base url
        jira_url = 'https://issues.onenetwork.com'
        # Endpoint below only displays 50 issues.
        api_endpoint = '/rest/api/2/search?jql=filter=45133'
        maxResults_endpoint = '&maxResults='
        filter_endpoint = '&fields=id,key,labels,lastViewed,issuelinks,issuetype,updated,summary,priority,status,created,description,fixVersions,reporter,assignee,duedate'

        # Load the JIRA API key from the .env file
        load_dotenv()
        jira_api_key = os.getenv('JIRA_API_KEY')
        token = jira_api_key
        headers = {
            "Authorization": "Bearer " + f"{token}",
            "Content-Type": "application/json"
        }

        try:
            # Send a request to JIRA to retrieve number of issues
            response = requests.get(jira_url + api_endpoint + maxResults_endpoint + '1', headers=headers)

            # Send a new request to JIRA to retrieve ALL issues
            maxResults = response.json().get('total', [])
            response = requests.get(jira_url + api_endpoint + maxResults_endpoint + f'{maxResults}' + filter_endpoint, headers=headers)
        except:
            print("Error retrieving JSON from JIRA")

        # Code below to remove null values
        # output = self.remove_nulls(response.json())

        output = response.json()

        """Below code would be used to filter base issue based on status."""
        # The status value in the base issues that determines if the issue is kept or not
        status_to_not_keep = {'marked for completion', 'resolved', 'closed', 'canceled', 'done', 'will not implement', 'work completed', 'answered', 'not a bug', 'waiting for customer'}

        try:
            status_filtered_data = [
                issue for issue in output['issues']
                if issue['fields'].get('status').get('name', '').lower() not in status_to_not_keep
            ]
            output['issues'] = status_filtered_data
        except:
            print("Error trying to filter JSON's base issues based on status")
        
        """Below code would filter the output fields - but found a way to make JIRA do it which is much faster."""
        # Define the keys you want to keep
        # keys_to_keep = {'id', 'key', 'labels', 'lastViewed', 'issuelinks', 'issuetype', 'updated', 'summary', 'priority', 'status', 'created', 'description', 'fixVersions', 'reporter', 'assignee', 'duedate'}
        # try: 
        #     # Filter the data
        #     filtered_data = [
        #         {
        #             **{k: v for k, v in issue.items() if k in keys_to_keep},  # Include all top-level key-value pairs except 'fields'
        #             'fields': {k: v for k, v in issue['fields'].items() if k in keys_to_keep}  # Filtered 'fields' dictionary
        #         }
        #         for issue in output['issues']
        #     ]
        #     output['issues'] = filtered_data
        # except:
        #     print("Error trying to filter certain keys throughout whole JSON")

        # Specify the file path and mode
        file_path = 'output.txt'  # Change 'output.txt' to your desired file path

        # Open the file and write the output
        with open(file_path, 'w', encoding='utf-8') as file:
            json_output = json.dump(output, file, ensure_ascii=False, indent=4) # Convert the dictionary to string before writing
        
        actual_issues, oneis_dictionary = self.filter_issues(output, jira_url, headers, status_to_not_keep)
        api_issue_endpoint = '/rest/api/2/issue/'
        # ai_filter_endpoint = '&fields=key,lastViewed,issuetype,updated,summary,priority,created,description,reporter,duedate'
        data = json.dumps({ "update": { "labels": [ {"add": "Autoflag"} ] } })
        
        """Below code specified fields to keep in the AI summary. This is no longer needed as JIRA now does the filtering."""
        # AI_keys_to_keep = {'key', 'lastViewed', 'issuetype', 'updated', 'summary', 'priority', 'created', 'description', 'reporter', 'duedate'}
        AI_keys_to_keep = {
            'key': None,
            'fields': {
                'lastViewed': None,
                'updated': None,
                'description': None,
                'summary': None,
                'created': None,
                'labels': None,
                'priority': ['name'],
                'status': ['name'],
                'reporter': ['name'],
            },
        }
        AI_input_list = []

        for issue in actual_issues:
            try:
                key_name = issue.get('key', {})
            except:
                key_name = "Error retrieving key"
            check = requests.put(jira_url + api_issue_endpoint + key_name, headers=headers, data=data)
            filtered_data = self.filter_json(issue, AI_keys_to_keep)
            readable_output = json.dumps(filtered_data, indent=4)
            cleaned_string = re.sub(r'[{}]', '', readable_output)
            AI_input_list.append(cleaned_string)
        crew = ThemeCrew()
        AI_input_string = ''.join(AI_input_list)
        cleaned_AI_input_string = AI_input_string.replace("\n", "").replace("\r", "").replace("\t", " ")
        
        try:
            additional_text = crew.AI_summary(cleaned_AI_input_string)
        except:
            additional_text = "Error in AI Summary"
        
        self.send_email(actual_issues, jira_url, additional_text, oneis_dictionary)
        return json_output
    
    def filter_json(self, data, keys_to_keep):
        filtered_data = {}
        for key, sub_keys in keys_to_keep.items():
            if key in data:
                if isinstance(sub_keys, dict):
                    # Recursive call for nested sub-dictionaries
                    filtered_data[key] = self.filter_json(data[key], sub_keys)
                elif isinstance(sub_keys, list):
                    # Sub-dictionary filtering
                    if data[key] is not None:
                        filtered_data[key] = {sub_key: data[key][sub_key] for sub_key in sub_keys if sub_key in data[key]}
                    else:
                        pass
                else:
                    # Main dictionary filtering
                    filtered_data[key] = data[key]
        # with open("Outputs/check.txt", 'w', encoding='utf-8') as file:
        #     output = json.dump(filtered_data, file, ensure_ascii=False, indent=4)
        return filtered_data
    
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
    def filter_issues(self, data, jira_url, headers, status_to_not_keep):
        filtered_issues = []
        # testing_array = []
        actual_issues = []
        oneis_issues = {}

        fix_version_to_not_keep = {'neo 3.11', 'neo 3.10', 'neo 3.12', 'neo 3.9.1', 'sdk', 'glg neo 3.10.1', 'neo 3.9.0.0.7', 'glg neo 3.9.1'}
        link = '/rest/api/2/issue/'

        try:
            issue_list = data.get('issues', [])
        except:
            issue_list = []
        # Iterate over each issue in the list of issues - each of these issues have already been filtered by the status
        for issue in issue_list:
            # Retrieve information
            try:
                main_status = issue.get('fields', {}).get('status', {}).get('name', {})
            except: 
                main_status = "Error retrieving status"

            try:
                date = issue.get('fields', {}).get('updated', {})
            except:
                date = "Error retrieving date"

            try:
                fix_versions = issue.get('fields', {}).get('fixVersions', {})
            except:
                fix_versions = []

            try:
                key = issue.get('key', {})
            except:
                key = "Error retrieving key"

            try:
                type_check = issue.get('fields', {}).get('issuetype', {}).get('name', {})
            except: 
                type_check = "Error retrieving type"

            try:
                assignee = issue.get('fields', {}).get('assignee', {}).get('name', {})
            except:
                assignee = "No Owner"

            try:
                summary = issue.get('fields', {}).get('summary', {})
            except:
                summary = "Error retrieving summary"

            if len(fix_versions) > 0:
                    fix_version_name = fix_versions[0].get('name', {})
            else:
                fix_version_name = 'placeholder'
            
            if main_status.lower() not in status_to_not_keep:
                if "ONEIS" in key:
                    if key not in oneis_issues:
                            if type_check != "New Feature":
                                oneis_issues.update({key: {"key": key, "owner": assignee, "summary": summary}})
                # Check if it hasn't been updated in 4 days
                if self.is_older_than_four_days(date, 4) or main_status.lower() == "blocked":
                    if key not in filtered_issues:
                        if type_check != "New Feature":
                            if fix_version_name.lower() not in fix_version_to_not_keep:
                                # This is a temporary filter
                                if 'QAT' not in key:
                                    filtered_issues.append(key)
                                    actual_issues.append(issue)
                                    # filtered_issues.append(issue.get('key', {}))

            # Navigate to the 'issuelinks' sub-dictionary
            try:
                issuelinks = issue.get('fields', {}).get('issuelinks', {})
            except: 
                issuelinks = []
            for link_issue in issuelinks:
                # Check for 'inwardIssue' and 'outwardIssue' keys within 'issuelinks'
                similar_issue = self.get_issue_value(link_issue)
                try:
                    status = similar_issue.get('fields', {}).get('status', {}).get('name', {})
                except:
                    status = "Error retrieving status"
                try:
                    key = similar_issue.get('key', {})
                except:
                    key = "Error retrieving key"
                try:
                    summary = similar_issue.get('fields', {}).get('summary', {})
                except:
                    summary = "Error retrieving summary"
                if status.lower() not in status_to_not_keep:
                    # Code for HTML table for displaying ONEIS issues
                    if "ONEIS" in key:
                        if key not in oneis_issues:
                            try:
                                response = requests.get(jira_url + link + key, headers=headers)
                                output = response.json()
                                type_check = output.get('fields', {}).get('issuetype', {}).get('name', {})
                                if type_check != "New Feature":
                                    try:
                                        assignee = output.get('fields', {}).get('assignee', {}).get('name', {})
                                    except:
                                        assignee = "No Owner"                      
                                    oneis_issues.update({key: {"key": key, "owner": assignee, "summary": summary}})
                            except:
                                pass
                    # If status is blocked add it
                    if status.lower() == "blocked":
                        if key not in filtered_issues:
                            try:
                                response = requests.get(jira_url + link + key, headers=headers)
                                output = response.json()
                                type_check = output.get('fields', {}).get('issuetype', {}).get('name', {})
                                if type_check != "New Feature":
                                    fix_versions_linked = output.get('fields', {}).get('fixVersions', {})
                                    if len(fix_versions_linked) > 0:
                                        fix_version_linked_name = fix_versions_linked[0].get('name', {})
                                    else:
                                        fix_version_linked_name = 'placeholder'
                                    
                                    if fix_version_linked_name.lower() not in fix_version_to_not_keep:
                                        filtered_issues.append(key)
                                        actual_issues.append(issue)
                            except:
                                pass
        # return_issues = testing_array + filtered_issues
        return actual_issues, oneis_issues
    
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
    
    
    def time_calculator(self, date_str):
        # Define the date format
        date_format = '%Y-%m-%dT%H:%M:%S.%f%z'
        
        # Parse the date string into a datetime object
        parsed_date = datetime.strptime(date_str, date_format)
        
        # Get the current date and time with timezone information
        current_date = datetime.now(pytz.timezone('UTC'))

        # Calculate the difference between the current date and the parsed date
        difference = current_date - parsed_date

        return difference

    def days_passed(self, date_str):
        # Calculate the difference between the current date and the parsed date
        difference = self.time_calculator(date_str)

        # Calculate the total number of days including fractional days
        total_days = difference.days + difference.seconds / (60 * 60 * 24)  # Convert seconds to days  
        rounded_days = math.ceil(total_days)
        # Check if the difference is greater than or equal to four days
        return rounded_days   

    """
        Checks if the given date string is older than four days from the current date.

        Args:
        date_str (str): The date string to check, in the format 'YYYY-MM-DDTHH:MM:SS.sssZ'.
        n_days (int): Amount of days to check is older than

        Returns:
        bool: True if the date is older than amount of days given, False otherwise.
    """
    def is_older_than_four_days(self, date_str, n_days):
        # Calculate the difference between the current date and the parsed date
        difference = self.time_calculator(date_str)

        # Check if the difference is greater than or equal to four days
        return difference >= timedelta(days=n_days)        
    
    """
        Send an email with the links to the problem issues.

        Args:
        keys_list (list): List of keys to issues that have not been updated in more than 4 days or are blocked.

        Returns:
        output_code (str): Code on whether or not the email request went through
    """
    def send_email(self, issue_list, jira_url, additional_text, oneis_dictionary):
        text = "<head><title>Table with Borders</title><style>table {border-collapse: collapse;width: 100%;}th, td {border: 1px solid black;padding: 8px;text-align: left;}</style></head>"
        text = text + "<p><strong>List of Blocked or Stalled Tickets</strong></p>"
        link = '/browse/'
        for issue in issue_list:
            try:
                created_date = issue.get('fields', {}).get('created', {})
                days = self.days_passed(created_date)
            except:
                days = "Error retrieving days passed"
            try:
                key = issue.get('key', {})
            except:
                key = "Error retrieving key"
            try:
                summary = issue.get('fields', {}).get('summary', {})
            except:
                summary = "Error retrieving summary"
            text = text + '<p><a href=' + jira_url + link + key + '>' + key + ' - ' + str(days) + ' days old</a>: ' + summary + '</p>'
        # Initialize the Postmark client with your server token
        text = text + '\n' + "<p><strong>Common Patterns (Autodetected)</strong></p>" + '\n' + additional_text
        text = text + "<p><strong>Resource Load</strong></p> \n <table><tr><th>Owner</th><th>Ticket Number</th><th>Summary</th></tr>"
        assignee_to_be_sorted = []
        for ticket in oneis_dictionary.values():
            key = ticket['key']
            owner = ticket['owner']
            summary = ticket['summary']
            assignee_to_be_sorted.append("<tr><td>" + owner + "</td><td>" + "<a href=" + jira_url + link + key + ">" + key + "</a></td><td>" + summary + "</td></tr>")
        assignee_to_be_sorted.sort()
        for row in assignee_to_be_sorted:
            text = text + row
        text = text + "</table>"
        email_token = os.getenv('EMAIL_API_KEY')
        client = PostmarkClient(server_token=email_token)
        # self.write_to_file(text, 'Outputs/check.txt')
        # Create a Postmark message
        client.emails.send(
            From="jaestrada@onenetwork.com",
            To="kwaldman@onenetwork.com , jaestrada@onenetwork.com" ,
            Subject="Issues That Are Blocked or Older Than 4 Days",
            HtmlBody=text
        )
        print(text)

jira_api = JiraApi()  # Create an instance of the JiraApi class
# issues = jira_api.identify_themes()
issues = jira_api.get_issues()  # Call the get_issues method
print("worked")