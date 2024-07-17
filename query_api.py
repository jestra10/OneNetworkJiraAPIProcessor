#!/home/jestra10/JQLv2/.venv/Scripts/python.exe


import os
import requests
import math
from getpass import getpass
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
# from postmarker.models.email import PostmarkMessage

class JiraApi:
    def __init__(self):
        pass
    def identify_themes(self):
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

        try:
            # Send a request to JIRA to retrieve issues
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

        # Open the file and write the output
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
            self.write_to_file(result, "Outputs/output"+str(i+1)+"4.txt")

        final_result = theme_crew.synthesize('\n'.join(results))
        # # final_result = theme_crew.problem_identifier(cleaned_string)
        # final_result = theme_crew.synthesize(result1+ '\n' + result2 + '\n' + result3 + '\n' + result4 + '\n' + result5 + '\n' + result6)
        print(final_result)
        self.write_to_file(final_result, 'Outputs/final4.txt')
        # Specify the file path
        file_path = 'Outputs/final4.txt'
        # Open the file in write mode and write the string to the file
        with open(file_path, 'w') as file:
            file.write(final_result)
        return json_output
    
    def write_to_file(self, data, file_path):
        with open(file_path, 'w') as file:
            file.write(data)

    def helper_identify_themes(self, issue):
        issue_links = issue.get('fields', {}).get('issuelinks', {})
        keys = ""
        for link_issue in issue_links:
            # Check for 'inwardIssue' and 'outwardIssue' keys within 'issuelinks'
            similar_issue = self.get_issue_value(link_issue)
            keys = keys + similar_issue.get('key', {})
        return keys
    
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

        try:
            # Send a request to JIRA to retrieve issues
            response = requests.get(jira_url + api_endpoint + maxResults_endpoint + '1', headers=headers)

            # Send a new request to JIRA to retrieve ALL issues
            maxResults = response.json().get('total', [])
            response = requests.get(jira_url + api_endpoint + maxResults_endpoint + f'{maxResults}', headers=headers)
        except:
            print("Error retrieving JSON from JIRA")

        # print(response.json())
        # print(response.status_code)

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

        # type_to_not_keep = {'new feature'}
        # try:
        #     status_filtered_data = [
        #         issue for issue in output['issues']
        #         if issue['fields'].get('status').get('name', '').lower() not in status_to_not_keep
        #     ]
        #     output['issues'] = status_filtered_data
        # except:
        #     print("Error trying to filter JSON's base issues based on status")
        
        # Define the keys you want to keep
        keys_to_keep = {'id', 'key', 'labels', 'lastViewed', 'issuelinks', 'issuetype', 'updated', 'summary', 'priority', 'status', 'created', 'description', 'fixVersions', 'reporter', 'assignee', 'duedate'}

        try: 
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
        except:
            print("Error trying to filter certain keys throughout whole JSON")
        
        # print(output)

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
        
        actual_issues, oneis_dictionary = self.filter_issues(output, jira_url, headers, status_to_not_keep)
        api_issue_endpoint = '/rest/api/2/issue/'
        data = json.dumps({ "update": { "labels": [ {"add": "Autoflag"} ] } })
        
        # AI_keys_to_keep = {'key', 'lastViewed', 'issuetype', 'updated', 'summary', 'priority', 'created', 'description', 'reporter', 'duedate'}
        AI_keys_to_keep = {
            'key': None,
            'fields': {
                'lastViewed': None,
                'updated': None,
                'description': None,
                'summary': None,
                'created': None,
                'duedate': None,
                'labels': None,
                'priority': ['name'],
                'status': ['name'],
                'reporter': ['name', 'key'],
            },
        }
        AI_input_list = []
        # for issue in critical_issues:
        #     check = requests.put(jira_url + api_issue_endpoint + issue, headers=headers, data=data)
            # print(check.status_code)
            # important_data = requests.get(jira_url + api_issue_endpoint + issue, headers=headers)
            # important_data = important_data.json()
            # filtered_data = [
            #     {
            #         **{k: v for k, v in important_data.items() if k in keys_to_keep},  # Include all top-level key-value pairs except 'fields'
            #         'fields': {k: v for k, v in important_data['fields'].items() if k in AI_keys_to_keep}  # Filtered 'fields' dictionary
            #     }
            # ]
            # readable_output = json.dumps(filtered_data, indent=4)
            # cleaned_string = re.sub(r'[{}]', '', readable_output)
            # AI_input_list.append(cleaned_string)
        for issue in actual_issues:
            # important_data = issue
            # filtered_data = [
            #     {
            #         **{k: v for k, v in important_data.items() if k in keys_to_keep},  # Include all top-level key-value pairs except 'fields'
            #         'fields': {k: v for k, v in important_data['fields'].items() if k in AI_keys_to_keep}  # Filtered 'fields' dictionary
            #     }
            # ]
            key_name = issue.get('key', {})
            check = requests.put(jira_url + api_issue_endpoint + key_name, headers=headers, data=data)
            filtered_data = self.filter_json(issue, AI_keys_to_keep)
            readable_output = json.dumps(filtered_data, indent=4)
            cleaned_string = re.sub(r'[{}]', '', readable_output)
            AI_input_list.append(cleaned_string)
        crew = ThemeCrew()
        # additional_text = crew.AI_summary(AI_input_list)
        additional_text = "blah blah blah"
        self.send_email(actual_issues, jira_url, additional_text, oneis_dictionary)
        return json_output
    
    def filter_json(self, data, keys_to_keep):
        # keys_to_keep = {'key', 'lastViewed', 'issuetype', 'updated', 'summary', 'priority', 'status', 'created', 'description', 'reporter', 'duedate'}
        filtered_data = {}
        for key, sub_keys in keys_to_keep.items():
            if key in data:
                if isinstance(sub_keys, dict):
                    # Recursive call for nested sub-dictionaries
                    filtered_data[key] = self.filter_json(data[key], sub_keys)
                elif isinstance(sub_keys, list):
                    # Sub-dictionary filtering
                    filtered_data[key] = {sub_key: data[key][sub_key] for sub_key in sub_keys if sub_key in data[key]}
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

        # Iterate over each issue in the list of issues
        for issue in data.get('issues', []):
            # Retrieve information
            main_status = issue.get('fields', {}).get('status', {})
            date = issue.get('fields', {}).get('updated', {})
            fix_versions = issue.get('fields', {}).get('fixVersions', {})
            key = issue.get('key', {})
            try:
                assignee = issue.get('fields', {}).get('assignee', {}).get('name', {})
            except:
                assignee = "No Owner"
            summary = issue.get('fields', {}).get('summary', {})
            if len(fix_versions) > 0:
                    fix_version_name = fix_versions[0].get('name', {})
            else:
                fix_version_name = 'placeholder'
            if "ONEIS" in key:
                if key not in oneis_issues:
                    oneis_issues.update({key: {"key": key, "owner": assignee, "summary": summary}})
            # Check if the status is set as blocked
            if main_status == "Blocked":
                if key not in filtered_issues:
                    if fix_version_name.lower() not in fix_version_to_not_keep:
                        filtered_issues.append(key)
                        actual_issues.append(issue)
            # Check if it hasn't been updated in 4 days
            elif self.is_older_than_four_days(date, 4):
                type_check = issue.get('fields', {}).get('issuetype', {}).get('name', {})
                if key not in filtered_issues:
                    if type_check != "New Feature":
                        if fix_version_name.lower() not in fix_version_to_not_keep:
                            # This is a temporary filter
                            if 'QAT' not in key:
                                filtered_issues.append(key)
                                actual_issues.append(issue)
                                # filtered_issues.append(issue.get('key', {}))

            # Navigate to the 'issuelinks' sub-dictionary
            issuelinks = issue.get('fields', {}).get('issuelinks', {})
            for link_issue in issuelinks:
                # Check for 'inwardIssue' and 'outwardIssue' keys within 'issuelinks'
                similar_issue = self.get_issue_value(link_issue)
                status = similar_issue.get('fields', {}).get('status', {}).get('name', {})
                key = similar_issue.get('key', {})
                summary = similar_issue.get('fields', {}).get('summary', {})
                if "ONEIS" in key:
                        if key not in oneis_issues:
                            response = requests.get(jira_url + link + key, headers=headers)
                            output = response.json()
                            try:
                                assignee = output.get('fields', {}).get('assignee', {}).get('name', {})
                            except:
                                assignee = "No Owner"                      
                            oneis_issues.update({key: {"key": key, "owner": assignee, "summary": summary}})
                if status not in status_to_not_keep:
                    # Code for HTML table for displaying ONEIS issues
                    '''Below code is for a FILTERED ONEIS issues dictionary'''
                    # if "ONEIS" in key:
                    #     if key not in oneis_issues:
                    #         response = requests.get(jira_url + link + key, headers=headers)
                    #         output = response.json()
                    #         assignee = output.get('fields', {}).get('assignee', {}).get('name', {}) 
                    #         fix_versions_linked = output.get('fields', {}).get('fixVersions', {})
                    #         if len(fix_versions_linked) > 0:
                    #             fix_version_linked_name = fix_versions_linked[0].get('name', {})
                    #         else:
                    #             fix_version_linked_name = 'placeholder'
                            
                    #         if fix_version_linked_name.lower() not in fix_version_to_not_keep:                        
                    #             oneis_issues.update({key: {"key": key, "owner": assignee, "summary": summary}})
                    # If status is blocked add it
                    if status == "Blocked":
                        if key not in filtered_issues:
                            response = requests.get(jira_url + link + key, headers=headers)
                            output = response.json()

                            fix_versions_linked = output.get('fields', {}).get('fixVersions', {})
                            if len(fix_versions_linked) > 0:
                                fix_version_linked_name = fix_versions_linked[0].get('name', {})
                            else:
                                fix_version_linked_name = 'placeholder'
                            
                            if fix_version_linked_name.lower() not in fix_version_to_not_keep:
                                filtered_issues.append(key)
                                actual_issues.append(issue)
        # print(testing_array)
        # print(filtered_issues)
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
            created_date = issue.get('fields', {}).get('created', {})
            days = self.days_passed(created_date)
            key = issue.get('key', {})
            summary = issue.get('fields', {}).get('summary', {})
            text = text + '<p><a href=' + jira_url + link + key + '>' + key + ' - ' + str(days) + ' days old</a>: ' + summary + '</p>'
        # Initialize the Postmark client with your server token
        text = text + '\n' + "<p><strong>Common Patterns (Autodetected)</strong></p>" + '\n' + additional_text
        text = text + "<p><strong>Resource Load</strong></p> \n <table><tr><th>Owner</th><th>Ticket Number</th><th>Summary</th></tr>"
        assignee_to_be_sorted = []
        for ticket in oneis_dictionary.values():
            key = ticket['key']
            owner = ticket['owner']
            summary = ticket['summary']
            assignee_to_be_sorted.append("<tr><td>" + owner + "</td><td>" + key + "</td><td>" + summary + "</td></tr>")
        assignee_to_be_sorted.sort()
        for row in assignee_to_be_sorted:
            text = text + row
        text = text + "</table>"
        email_token = os.getenv('EMAIL_API_KEY')
        client = PostmarkClient(server_token=email_token)
        self.write_to_file(text, 'Outputs/check.txt')
        # Create a Postmark message
        # client.emails.send(
        #     From="jaestrada@onenetwork.com",
        #     To="kwaldman@onenetwork.com , jaestrada@onenetwork.com" ,
        #     Subject="Issues That Are Blocked or Older Than 4 Days",
        #     HtmlBody=text
        # )
        print(text)

        # # Email configuration
        # sender_email = "jaestrada@elogex.com"
        # receiver_email = "jaestrada@elogex.com"
        # subject = "Test"
        # body = "Test"

        # # Create a multipart message and set headers
        # message = MIMEMultipart()
        # message["From"] = sender_email
        # message["To"] = receiver_email
        # message["Subject"] = subject

        # # Add body to email
        # message.attach(MIMEText(body, "plain"))

        # # Connect to the SMTP server
        # with smtplib.SMTP("smtp.office365.com", 587) as server:
        #     server.starttls()  # Enable TLS encryption
        #     server.login("jaestrada@elogex.com", "Passport611!")
        #     text = message.as_string()
        #     server.sendmail(sender_email, receiver_email, text)

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

# if __name__ == "__main__":
#     jira_api = JiraApi()  # Create an instance of the JiraApi class
#     issues = jira_api.get_issues()  # Call the get_issues method
#     # keys_list = ['SGLG-2576', 'LN-110866', 'LN-110859', 'LN-110797', 'LN-110765', 'LN-110586', 'LN-109372', 'LN-108719', 'LN-108697', 'LN-101457', 'INTEG-1953']
#     # email = jira_api.send_email(keys_list, 'https://issues.onenetwork.com')
jira_api = JiraApi()  # Create an instance of the JiraApi class
# issues = jira_api.identify_themes()
issues = jira_api.get_issues()  # Call the get_issues method
print("worked")