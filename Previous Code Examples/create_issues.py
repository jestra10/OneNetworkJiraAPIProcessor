
import requests
import sys
from getpass import getpass

# Check if the correct number of arguments are passed
if len(sys.argv) != 3:
    print("Usage: python scriptname.py 'Task Summary' 'Task Description'")
    sys.exit(1)

# Task details from command line arguments
task_summary = sys.argv[1]
task_description = sys.argv[2]

# Hardcoded data structure
projects = [
        {'Project Name': 'PMO', 'Summary':'HPE', 'Project Manager Name': 'kwaldman', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Kroger', 'Project Manager Name': 'ccasey', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'ARC', 'Project Manager Name': 'pchavali', 'Frequency': 'monthly'},
        {'Project Name': 'PMO', 'Summary':'CEVA', 'Project Manager Name': 'pchavali', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Comvita', 'Project Manager Name': 'jportwain', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Dana', 'Project Manager Name': 'mhuffman', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Fiskars', 'Project Manager Name': 'jkim', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Fujifilm', 'Project Manager Name': 'jkim', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'GM-RXO', 'Project Manager Name': 'rangadi', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Imperial', 'Project Manager Name': 'kwaldman', 'Frequency': 'monthly'},
        {'Project Name': 'PMO', 'Summary':'PepsiCo', 'Project Manager Name': 'rcletus', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'JnJ', 'Project Manager Name': 'dreynolds', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Moy Park', 'Project Manager Name': 'jkim', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'USAID', 'Project Manager Name': 'abrits', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'WHO', 'Project Manager Name': 'jbonner', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'APLL', 'Project Manager Name': 'rvaidya', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Bayer', 'Project Manager Name': 'skarmarkar', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'DHL', 'Project Manager Name': 'kwaldman', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Dollar General', 'Project Manager Name': 'ccasey', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Dunnes Stores', 'Project Manager Name': 'ccasey', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Kenvue', 'Project Manager Name': 'ccasey', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'NEOM', 'Project Manager Name': 'ccasey', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'Philips', 'Project Manager Name': 'ccasey', 'Frequency': 'weekly'},
        {'Project Name': 'PMO', 'Summary':'BP Castrol', 'Project Manager Name': 'ccasey', 'Frequency': 'weekly'}
]


# JIRA API details
jira_url = 'https://issues.onenetwork.com'  # Replace with your JIRA URL
api_endpoint = '/rest/api/2/issue/'
username = input("Enter JIRA username: ")  # Prompting the user for JIRA username
password = getpass("Enter JIRA password: ")  # Securely prompting for JIRA password
headers = {'Content-Type': 'application/json'}

# Iterate over the hardcoded project data
for project in projects:
    project_name = project['Project Name']
    pm_name = project['Project Manager Name']

    # Create the issue data
    issue_data = {
        "fields": {
            "project": {
                "key": "PMO"  # Replace with your JIRA project key
            },
            "summary": f"{task_summary} on {project['Summary']}",
            "description": task_description,
            "issuetype": {
                "name": "Task"  # Or whatever issue type you need
            },
            "assignee": {
                "name": pm_name  # Ensure this matches the JIRA username of the PM
            }
        }
    }

    # Send a request to JIRA to create an issue
    response = requests.post(jira_url + api_endpoint, json=issue_data, auth=(username, password), headers=headers)

    # Check for successful creation
    if response.status_code == 201:
        print(f"Issue created successfully for {project_name} and {task_summary}")
    else:
        print(f"Failed to create issue for {project_name}: {response.content}")

# End of script
