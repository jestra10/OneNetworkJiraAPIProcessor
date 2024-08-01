### ENVIRONMENT SETUP

This code uses Poetry to run a virutal environment. Ensure that you have Poetry installed so that the code can be run.
This project uses python versions between 3.12 - 3.13.
To get the code running, "cd" into the project folder that contains the "pyproject.toml" file
and run "poetry install" in the terminal (you may also have to run "poetry lock".) The code should be up and running.
If you continue running into issues, try deleting the "poetry.lock" file and then running "poetry install" command.

To have this code work properly, you need a .env file containing an OpenAI key, a JIRA token, and a Postmark token.
These tokens are relevant to the "crew_theme.py" and "query_api.py" files.
To create a .env file, just create a new file and name it ".env".
To get your Postmark token, please go to the "EMAIL SETUP" subsection of this document.
To get your OpenAI key, use the following link to generate a secret key: https://platform.openai.com/api-keys.
To get your JIRA token, log into your company's JIRA website. Once logged in click on your profile picture
in the top right corner. From the dropdown menu, click "Profile". On the left side of the screen, you should see
and click a tab called "Personal Access Tokens". Once clicked, you can create a token for your use case.

An example of a .env file can be seen below. Replace the <> with the tokens you generated from above:

JIRA_API_KEY=<jira token>
OPENAI_API_KEY=<openai key>
EMAIL_API_KEY=<postmark token>

### EMAIL SETUP

For setting up the email and getting a token from Postmark, first head to this link: https://postmarkapp.com/email-api.
If you have not already, create an account (I recommend using your company email.) If you want to send an
email outside of your company domain, you will have to add a sender signature (which can be done by clicking
on the "Sender Signature" tab at the very top of the website.) Once you create an account and set that up,
you want to make a server (which can be accessed using this link https://account.postmarkapp.com/servers.)
Once a server has been created, click on it. You should now be on a page looking at the server you just created.
Towards the top you should see tabs that say "Message Streams", "Templates", "API Tokens", and "Settings."
Click the option of "API Tokens". From here you can generate/copy your API token. This will allow you to use
their services and send emails. Put the token you copied in your .env file.
