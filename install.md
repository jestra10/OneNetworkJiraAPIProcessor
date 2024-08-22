### ENVIRONMENT SETUP

This code uses Poetry to run a virutal environment. Ensure that you have Poetry installed so that the code can be run.
This project uses python versions between 3.12 - 3.13.
To get the code running, "cd" into the project folder that contains the "pyproject.toml" file
and run "poetry install" in the terminal (you may have to run "poetry lock" first.) The code should be ready to go.
If you continue running into issues and errors keep popping up when running the above commands, try deleting the "poetry.lock" file and then running "poetry install" command again. This should hopefully fix your issues. After you run these commands, run "poetry shell". This will enter your terminal into the virtual environment and allow you to run the program/command.

To have this code work properly, you need a .env file containing an OpenAI key/Groq key, a JIRA token, and a Postmark token.
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

### CRON JOB SETUP

Download Ubuntu from the Microsoft store (or wherever you can download it from.) Once you give it admin permissions and it is downloaded, open it up and make sure it is working. It will likely make you create an account when first opening it up. Now, you should be able to see a Linux section in your file explorer. Double click on the Linux section. There, you should see an "Ubuntu" folder - double click on this. In this folder there will be many folders. Find the "home" folder and double click on it. In this folder, you should see a folder with your username - double click on that folder. Move the folder that contains the code you want to be run by cron into the folder you just navigated to (the username folder). So, now the folder with the code should have a file path such as "/home/<username>/<code_folder>".

Now, in order for this program to run you will also have to download a newer version of python on Ubuntu/Linux. For some reason, it does not come downloaded with the most recent version of Python, which causes problems when trying to run the program on Ubuntu. I found that the best way to download a newer version of python is through pyenv. Here is a useful link for downloading pyenv on Ubuntu(https://github.com/pyenv/pyenv#installation.) I don't remember the exact lines of code I used to download pyenv, but it looks pretty simple to download via "Brew". You could also always ask ChatGPT how to download pyenv as that is what I did the first time around (it will make you run many, long different lines of code.) An example of what ChatGPT tells you to run can be seen below:
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
 libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
 libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
curl https://pyenv.run | bash
echo -e '\n# Pyenv Configuration' >> ~/.bashrc
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
pyenv --version

I recommend following the instructions in the link instead of the multiple lines of code given by ChatGPT. Once pyenv is downloaded on Ubuntu, you can now download a newer version of python. To do this run:
pyenv install 3.12.4
pyenv global 3.12.4

The second line (the line with global in it), should set your preferred python version to the version you specified.
Now that you have downloaded a newer version of python, you will be able to write your cron job. First I will display an example of a cron job that I wrote for it to run the query_api.py file (which sends the emails containing blocked or old issues) and will then explain it in parts:
0 4 \* \* 1-5 cd /home/jaestrada/JQLv2 && /usr/bin/poetry env use /home/jaestrada/.pyenv/versions/3.12.4/bin/python3 && /usr/bin/poetry run python query_api.py >> /home/jaestrada/JQLv2/log.txt 2>&1

"0 4 \* \* 1-5": This part is how you specify when you want it to automatically send. So, this line is saying that it will send at 4am Monday-Friday.

"cd /home/jaestrada/JQLv2": this line makes changes into the directory of the project folder. Where ever you moved the folder with code to, you want to "cd" into that folder. If you followed the instructions from before then this line will be "cd /home/<username>/<code_folder>"

"&& /usr/bin/poetry env use /home/jaestrada/.pyenv/versions/3.12.4/bin/python3": The "&&" symbols just mean that this is the next line of code needed to be run. The rest of the line is telling poetry to use the new version of python that you had just downloaded from pyenv. When implementing this line yourself, it should look like "&& /usr/bin/poetry env use /home/<username>/.pyenv/versions/3.12.4/bin/python3".

"&& /usr/bin/poetry run python query_api.py": This line of code is what actually runs your desired code. This should stay the same unless you want to run a different file.

When putting all the above lines of code together, the (theoretical) template should be:
0 4 \* \* 1-5 cd /home/<username>/<code_folder> && /usr/bin/poetry env use /home/<username>/.pyenv/versions/3.12.4/bin/python3 && /usr/bin/poetry run python query_api.py
