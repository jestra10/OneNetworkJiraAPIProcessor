import os
import requests
from getpass import getpass
from dotenv import load_dotenv
import pandas as pd

token = 'place token here'

class Updater:
    def __init__(self):
        pass
    def update(self):
        # JIRA API details
        jira_url = 'https://issues.onenetwork.com'  # Replace with your JIRA URL
        # Endpoint below only displays 50 issues.
        # api_endpoint = '/rest/api/2/issue/'
        api_endpoint = '/rest/api/2/search?jql=project=PAS&fields=id,key,self,summary,labels,components,comment'
        # username = input("Enter JIRA username: ")  # Prompting the user for JIRA username
        # password = getpass("Enter JIRA password: ")  # Securely prompting for JIRA password
        maxResults_endpoint = '&maxResults='

        # load_dotenv()
        # jira_api_key = os.getenv('JIRA_API_KEY')
        # token = jira_api_key
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

        keys = {'issue key', 'summary', 'labels', 'components', 'comment comments 0 body'}
        output = response.json()
        first_run = True
        for issue in output['issues']:
            # print(issue['fields'])
            # flattened_output = self.flatten_dict(issue['fields'])
            flattened_output = self.flatten_essentials_dict(issue['fields'])
            flattened_output['issue key'] = issue['key']
            # print(flattened_output)
            # flattened_output = self.filter_dict(flattened_output, keys)
            if first_run:
                # Making an excel file and create a DataFrame
                df = pd.DataFrame([flattened_output])
                first_run = False
            else:
                # Making an excel file and create a DataFrame
                df2 = pd.DataFrame([flattened_output])
                df = pd.concat([df, df2], ignore_index=True)
        # output2 = response2.json()
        # flattened_output1 = self.flatten_dict(output2['fields'])
        # flattened_output1['issue key'] = output2['key']
        # flattened_output1 = self.filter_dict(flattened_output1, keys)
        # Making an excel file and create a DataFrame
        # df = pd.DataFrame([flattened_output])
        # df2 = pd.DataFrame([flattened_output1])
        # df = pd.concat([df, df2], ignore_index=True)

        """Below code would be used if wanted to include custome fields in the output excel file."""
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
        # df.to_excel('Outputs/outputdata.xlsx', index=False, engine='openpyxl')
        print("Finished process and created a combined excel file.")
        return df
        # print(output)
    
    def filter_dict(self, dict, keys):
        return {k: v for k, v in dict.items() if k in keys}

    def flatten_essentials_dict(self, d):
        return_dict = {}
        comment = d.get('comment').get('comments')
        if len(comment) > 0:
            last_comment_index = len(comment) - 1
            return_dict['last comment'] = comment[last_comment_index].get('body')
        else:
            return_dict['last comment'] = None
        return_dict['labels'] = d.get('labels')
        component = d.get('components')
        if len(component) > 0:
            return_dict['component'] = component[0].get('name')
        else:
            return_dict['component'] = None
        return_dict['summary'] = d.get('summary')
        return return_dict
        
    # '''I don't like the way its being done so I'm going to do it manually. If theres a comment then ill add it manually, etc.'''
    # def flatten_dict(self, d, parent_key='', sep=' '):
    #     items = []  # Initialize an empty list to collect key-value pairs
    #     for k, v in d.items():
    #         # Form the new key by appending the current key to the parent key
    #         # If parent_key is empty, new_key is just k (the current key)
    #         # If parent_key is not empty, new_key is parent_key + sep + k
    #         new_key = f"{parent_key}{sep}{k}" if parent_key else k
    #         if isinstance(v, dict):  # If the value is a dictionary, recursively flatten it
    #             items.extend(self.flatten_dict(v, new_key, sep=sep).items())
    #         elif isinstance(v, list):  # If the value is a list, iterate through the list
    #             for index, item in enumerate(v):
    #                 # print(k)
    #                 if k == 'labels' or k == 'components':
    #                     if isinstance(item, dict):  # Check if the item is a dictionary
    #                         items.extend(self.flatten_dict(item, f"{new_key}{sep}{index}", sep=sep).items())
    #                 else:  # If the item is not a dictionary, add it as is
    #                     items.append((f"{new_key}{sep}{index}", item))
    #         else:  # If the value is not a dictionary, add the key-value pair to the list
    #             items.append((new_key, v))
    #     return dict(items)  # Convert the list of key-value pairs back into a dictionary
    
    def create(self):
        # load_dotenv()
        # jira_api_key = os.getenv('JIRA_API_KEY')
        # token = input("Enter JIRA token: ")
        # username = input("Enter JIRA username: ")  # Prompting the user for JIRA username
        # password = getpass("Enter JIRA password: ")  # Securely prompting for JIRA password
        headers = {
            "Authorization": "Bearer " + f"{token}",
            "Content-Type": "application/json"
        }
        master_columns = ['Order','Partner Type','Multi-Org?','Bayer_PartnerListName','Bayer_PartnerIntakeName','Bayer_PartnerResultsName','New Onboarding Admin Wave 1 Data Load?','Engagement Status','Wave','InTake Form Completed?', 'Preferred Connectivity Type','Bayer Priority','ONE Comment','Bayer Comment','Labels','Components','Shipping Location','Registered for Training?','Attended Training?','Category','Vendor Number','Affiliates','VAT / SCAC','Partner Requested SCAC','PAS Ticket','INTEG Ticket','Enterprise','Admin Name','Admin Last Name','Admin Email','Technical Contact First Name','Technical Contact Last Name','Technica Contact Email','Send new email','Bayer V3 Comments','New email','Valid email']
        master_header = pd.DataFrame(columns=master_columns)
        vendor_master = pd.read_excel('Bayer/Bayer_VendorMasterFinalList.xlsx')
        provided_list = pd.read_excel('Bayer/Bayer_PartnerProvidedList.xlsx')
        intake_list = pd.read_excel('Bayer/Bayer_PartnerIntake.xlsx')
        intake_list_cleaned = intake_list.drop_duplicates(subset=['Legal Company Enterprise Name:'])
        intake_list_cleaned = intake_list_cleaned.reset_index(drop=True)
        provided_list['filter_column'] = provided_list['Partner Organization Name'].str.lower()
        provided_list_cleaned = provided_list.drop_duplicates(subset=['filter_column'])
        provided_list_cleaned = provided_list_cleaned.drop(columns=['filter_column'])
        provided_list_cleaned = provided_list_cleaned.reset_index(drop=True)
        # blank_row = pd.DataFrame([[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]], columns=master_header)
        blank_row = pd.DataFrame([[None] * len(master_columns)], columns=master_columns)
        # issue_df = self.update()
        
        checked_issue_list = []
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
                # print(row['Enterprise/Org'])
                score, issue_name, issue_key, last_comment, labels, components = self.find_issue_match(row['Enterprise/Org'], checked_issue_list, headers)
                # print(score)
                if score > .51:
                    # print(issue_name)
                    # print(row['Enterprise/Org'])
                    # print(score)
                    master_header.at[len(master_header)-1, 'PAS Ticket'] = issue_key
                    master_header.at[len(master_header)-1, 'INTEG Ticket'] = issue_name
                    master_header.at[len(master_header)-1, 'ONE Comment'] = last_comment
                    master_header.at[len(master_header)-1, 'Labels'] = labels
                    master_header.at[len(master_header)-1, 'Components'] = components
                    checked_issue_list.append(issue_name)
                
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

    def find_issue_match(self, name, checked_list, headers):
        jira_url = 'https://issues.onenetwork.com'  # Replace with your JIRA URL
        # Endpoint below only displays 50 issues.
        # api_endpoint = '/rest/api/2/issue/'
        api_endpoint = '/rest/api/2/search?jql=project=PAS AND summary ~\"'
        rest_api_endpoint = '\"&fields=id,key,self,summary,labels,components,comment'
        
        search_name = name.replace('&', '')
        search_name = search_name.replace('(', '')
        search_name = search_name.replace(')', '')
        search_name = search_name.replace('AND', 'and')
        # print(search_name)
        response = requests.get(jira_url + api_endpoint + search_name + rest_api_endpoint, headers=headers)
        print(response.status_code)
        try:
            response = requests.get(jira_url + api_endpoint + search_name + rest_api_endpoint, headers=headers)
            output = response.json()
            issues = output['issues']
            score = 0
            # index = 0
            # name_array = name.split(']')
            # if len(name_array) > 1:
            #     clean_name = name_array[1].strip()
            # else:
            #     clean_name = name
            # print(clean_name)
            # for candidate in candidate_list:
            #     if name not in checked_list:
            #         temp_score = self.similarity_score(name.lower(), candidate.lower())
            #         if temp_score >= score:
            #             score = temp_score
            #             index = candidate_list[candidate_list == candidate].index[0]
            if len(issues) > 0:
                issue = issues[0]
                issue_name = issue['fields']['summary']
                issue_name_array = issue_name.split(']')
                name = name.strip()
                if len(issue_name_array) > 1:
                    clean_issue_name = issue_name_array[1].strip()
                else:
                    clean_issue_name = issue_name.strip()
                last_comment_list = issue['fields']['comment']['comments']
                if len(last_comment_list) > 0:
                    last_comment = last_comment_list[len(last_comment_list) - 1]['body']
                else:
                    last_comment = None
                labels = issue['fields']['labels']
                components = issue['fields']['components']
                score = self.similarity_score(name.lower(), clean_issue_name.lower())
                # print(clean_issue_name)
                # print (score)
                return score, issue['fields']['summary'], issue['key'], last_comment, labels, components

                # else:
                #     for candidate in candidate_list:
                #         if candidate not in checked_list:
                #             temp_score = self.similarity_score(name.lower(), candidate.lower())
                #             if temp_score > score:
                #                 score = temp_score
                #                 index = candidate_list[candidate_list == candidate].index[0]
                #     print("returned" + str(index))
                #     return index
                # Sort matches by score in descending order
                # matches.sort(key=lambda x: x[1], reverse=True)
                # print("returned1 " + str(matches[0][2]))
        except:
            print("Error retrieving JSON from JIRA")
        score = 0
        return score, None, None, None, None, None

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