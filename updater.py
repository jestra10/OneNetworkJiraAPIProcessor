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

class Updater:
    def __init__(self):
        pass
    def update(self):
        # JIRA API details
        jira_url = 'https://issues.onenetwork.com'  # Replace with your JIRA URL
        # Endpoint below only displays 50 issues.
        api_endpoint = '/rest/api/2/issue/'
        # username = input("Enter JIRA username: ")  # Prompting the user for JIRA username
        # password = getpass("Enter JIRA password: ")  # Securely prompting for JIRA password

        load_dotenv()
        jira_api_key = os.getenv('JIRA_API_KEY')
        token = jira_api_key
        headers = {
            "Authorization": "Bearer " + f"{token}",
            "Content-Type": "application/json"
        }

        try:
            # Send a request to JIRA to retrieve issues
            response = requests.get(jira_url + api_endpoint + 'PAS-870', headers=headers)
        except:
            print("Error retrieving JSON from JIRA")
            return

        output = response.json()
        flattened_output = self.flatten_dict(output['fields'])
        # Making an excel file and create a DataFrame
        df = pd.DataFrame([flattened_output])
        # Write DataFrame to Excel file
        df.to_excel('Outputs/outputdata.xlsx', index=False, engine='openpyxl')
        print(output)

    def flatten_dict(self, d, parent_key='', sep=' '):
        items = []  # Initialize an empty list to collect key-value pairs
        for k, v in d.items():
            # Form the new key by appending the current key to the parent key
            # If parent_key is empty, new_key is just k (the current key)
            # If parent_key is not empty, new_key is parent_key + sep + k
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):  # If the value is a dictionary, recursively flatten it
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:  # If the value is not a dictionary, add the key-value pair to the list
                items.append((new_key, v))
        return dict(items)  # Convert the list of key-value pairs back into a dictionary


Updater().update()