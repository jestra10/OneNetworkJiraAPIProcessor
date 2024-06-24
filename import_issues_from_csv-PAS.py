import requests
from getpass import getpass
import csv
from time import sleep

username = input("Enter JIRA username: ")
token = input("Enter JIRA TOKEN: ")
project_code = input("Enter the 3 digit project code: ")
csv_file_name = input("Enter the CSV file name: ")

jira_url = 'https://issues.onenetwork.com'
api_endpoint = '/rest/api/2/issue/'
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
}

with open(csv_file_name, mode='r', encoding='latin1') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    for row in csv_reader:
        print(row)
    print("--------------------\n")
    csv_file.seek(0)  # Reset CSV file pointer to the beginning
    next(csv_reader)  # Skip the header row
    for row in csv_reader:
        print("Debug: Starting to create issue_data")
        issue_data = {
            "fields": {
                "project": {
                    "key": project_code
                },
                "summary": row['Summary'],
                "description": row['Description'],
                "issuetype": {
                    "name": row['Type']
                },
                "assignee": {
                    "name": row['Assignee']
                },
                "reporter": {
                    "name": row['Reporter']
                },
                "customfield_15074": row['Enterprise Admin Name'],  # Replace with actual custom field ID
                "customfield_15075": row['Enterprise Admin Email'],  # Replace with actual custom field ID
                "customfield_15071": {"id": "19039", "value": row['Preferred Connectivity Method']},  # Replace with actual custom field ID
                "customfield_15072": row['EIN/SCAC'],  # Replace with actual custom field ID
                "customfield_15068": row['Technical Contact Name'],  # Replace with actual custom field ID
                "customfield_15069": row['Technical Contact Email'],  # Replace with actual custom field ID
                "customfield_15076": row['Entry ID'],  # Replace with actual custom field ID
                "labels": [row['label']]
            }
        }
        print("Debug: Preparing to post issue_data")
        response = requests.post(jira_url + api_endpoint, json=issue_data, headers=headers)
        print("Debug: issue_data posted successfully")
        if response.status_code == 201:
            print(f"Issue created successfully for {row['Summary']}")
        else:
            print(f"Failed to create issue for {row['Summary']}: {response.content}")
        sleep(1)  # Sleep for 1 second between each API call
        sleep(1)  # Sleep for 1 second between each API call