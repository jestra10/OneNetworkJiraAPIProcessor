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
            response2 = requests.get(jira_url + api_endpoint + 'PAS-687', headers=headers)
        except:
            print("Error retrieving JSON from JIRA")
            return

        output = response.json()
        flattened_output = self.flatten_dict(output['fields'])
        output2 = response2.json()
        flattened_output1 = self.flatten_dict(output2['fields'])
        # Making an excel file and create a DataFrame
        df = pd.DataFrame([flattened_output])
        df2 = pd.DataFrame([flattened_output1])
        df = pd.concat([df, df2], ignore_index=True)

        """Below code would be used if wanted to include custome files in the output excel file."""
        # with open('customfield_dict.json', 'r') as file:
        #     customfield_dict = json.load(file)
        # rename_mapping = {}
        # for column_name in df.columns:
        #     if " " in column_name:
        #         # If the column name contains spaces, split and check the first part
        #         list_column_name = column_name.split()
        #         if list_column_name[0] in customfield_dict:
        #             rename_mapping[column_name] = customfield_dict[list_column_name[0]]
        #     # Check if the column name is in the customfield_dict
        #     elif column_name in customfield_dict:
        #         rename_mapping[column_name] = customfield_dict[column_name]
        # # Rename the columns in one go
        # df.rename(columns=rename_mapping, inplace=True)

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
    
    def create(self):
        master = pd.read_excel('Bayer/Bayer_PartnerMaster.xlsx', sheet_name='RMS.LSP Master')
        master_header = pd.DataFrame(columns=master.columns)
        vendor_master = pd.read_excel('Bayer/Bayer_VendorMasterFinalList.xlsx', sheet_name='Bayer-VendorMasterFinalList_060')
        provided_list = pd.read_excel('Bayer/Bayer_PartnerProvidedList.xlsx')
        intake_list = pd.read_excel('Bayer/Bayer_PartnerIntake.xlsx', sheet_name="Bayer POP Site Submissions Mast")
        intake_list_cleaned = intake_list.drop_duplicates(subset=['Legal Company Enterprise Name:'])
        intake_list_cleaned = intake_list_cleaned.reset_index(drop=True)
        intake_list_names = intake_list_cleaned['Legal Company Enterprise Name:']
        provided_list['filter_column'] = provided_list['Partner Organization Name'].str.lower()
        provided_list_cleaned = provided_list.drop_duplicates(subset=['filter_column'])
        provided_list_cleaned = provided_list_cleaned.drop(columns=['filter_column'])
        provided_list_cleaned = provided_list_cleaned.reset_index(drop=True)
        # blank_row = pd.DataFrame([[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]], columns=master_header)
        blank_row = pd.DataFrame([[None] * len(master.columns)], columns=master.columns)
        
        for index, row in vendor_master.iterrows():
            # if index == 0:
            #     master_header = pd.concat([master_header, blank_row], ignore_index=True)
            #     # master_header.loc[len(master_header)] = [None] * 34
            # else:
                # master_header.loc[len(master_header)] = [None] * 34
                master_header = pd.concat([master_header, blank_row], ignore_index=True)
                # master_header.at[index, 'Bayer_PartnerListName'] = row[index, 'Enterprise/Org']
                master_header.at[len(master_header)-1, 'Bayer_PartnerListName'] = provided_list_cleaned.at[index, 'Partner Name']
                master_header.at[len(master_header)-1, 'Vendor Number'] = provided_list_cleaned.at[index, '* Vendor No']
                if row['Match 0\nSimilarity Score'] >= 0.7:
                    master_header.at[len(master_header)-1, 'Bayer_PartnerResultsName'] = row['Match 0\nEnt Name']
        checked_list = []
        for index, row in intake_list_cleaned.iterrows():
        # for name in intake_list_names:
            name = row['Legal Company Enterprise Name:']
            admin_first_name = row['Enterprise Admin Name: First']
            admin_last_name = row['Enterprise Admin Name: Last']
            admin_email = row['Email']
            return_index = self.find_best_match(name, master_header['Bayer_PartnerListName'], checked_list)
            master_header.at[return_index, 'Bayer_PartnerIntakeName'] = name
            master_header.at[return_index, 'Enterprise Admin Name'] = admin_first_name
            master_header.at[return_index, 'Admin Last Name'] = admin_last_name
            master_header.at[return_index, 'Admin Email'] = admin_email
            checked = master_header.at[return_index, 'Bayer_PartnerListName']
            checked_list.append(checked)

                        
        master_header.to_excel('Bayer/check.xlsx', index=False)

    def levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        # If one of the strings is empty
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def similarity_score(self, name1, name2):
        distance = self.levenshtein_distance(name1, name2)
        max_len = max(len(name1), len(name2))
        return (max_len - distance) / max_len

    def find_best_match(self, name, candidate_list, checked_list):
        #make it one word at a time
        matches = []
        score = 0
        index = 0
        name_array = name.split()
        for candidate in candidate_list:
            if candidate not in checked_list:
                candidate_array = candidate.split()
                temp_score = self.similarity_score(name_array[0].lower(), candidate_array[0].lower())
                if temp_score > score:
                    matches = []
                if temp_score >= score:
                    score = temp_score
                    index = candidate_list[candidate_list == candidate].index[0]
                    matches.append((candidate, candidate_array, index))
        # if score > 0.6:
        i = 1
        score = 0
        # print(str(len(name_array)) + "- name_array")
        while len(matches) > 1 and i < len(name_array):
            temp_matches = []
            # print(str(i) + "- i")
            for match in matches:
                # print(match)
                if i < len(match[1]):
                    # print(name_array[i].lower())
                    # print(match[1][i].lower())
                    temp_score = self.similarity_score(name_array[i].lower(), match[1][i].lower())
                    # print("return from similarity_score")
                    if temp_score > score:
                        temp_matches = []
                    if temp_score >= score:
                        score = temp_score
                        index = candidate_list[candidate_list == match[0]].index[0]
                        temp_matches.append(match)
            # print(str(len(temp_matches)) + "- temp_matches")
            if len(temp_matches) == 0:
                # print("returned" + str(matches[0][2]))
                return matches[0][2]
            
            matches = temp_matches
            i += 1
        # else:
        #     for candidate in candidate_list:
        #         if candidate not in checked_list:
        #             temp_score = self.similarity_score(name.lower(), candidate.lower())
        #             if temp_score > score:
        #                 score = temp_score
        #                 index = candidate_list[candidate_list == candidate].index[0]
        #     print("returned" + str(index))
        #     return index
                
        index = matches[0][2]
        # Sort matches by score in descending order
        # matches.sort(key=lambda x: x[1], reverse=True)
        # print("returned1 " + str(matches[0][2]))
        return index


    def temp(self):
        # JIRA API details
        jira_url = 'https://issues.onenetwork.com'  # Replace with your JIRA URL
        # Endpoint below only displays 50 issues.
        api_endpoint = '/rest/api/latest/field'
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
            response = requests.get(jira_url + api_endpoint, headers=headers)
        except:
            print("Error retrieving JSON from JIRA")
            return
        final_dict = {}
        output = response.json()
        for issue in output:
            final_dict[issue['id']] = issue['name'] + '(' + issue['id'] + ')'
        print(final_dict)


Updater().create()