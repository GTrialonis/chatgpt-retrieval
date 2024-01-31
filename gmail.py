# https://python.langchain.com/en/latest/modules/agents/toolkits/examples/gmail.html

# Step 1: Create a json file and download the same in the working folder: https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application

# Step 2: pip3 install google-api-python-client, google-auth-oauthlib, google-auth-httplib2, beautifulsoup4, langchain

# Step 3: Add Users for testing this app In Authconsent Screen
# Issues resolved: https://stackoverflow.com/questions/65184355/error-403-access-denied-from-google-authentication-web-api-despite-google-acc

# Step 4: Enable it by visiting https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=26982114008


from langchain.agents.agent_toolkits import GmailToolkit
import PySimpleGUI as sg
import os
from constants import gmail_apiKey

# Assuming credentials.json is in the same directory as gmail.py
dir_path = os.path.dirname(os.path.realpath(__file__))
credentials_path = os.path.join(dir_path, 'credentials.json')
toolkit = GmailToolkit(credentials_file=credentials_path)
# toolkit = GmailToolkit() 

# Set up the environment variable for OpenAI API key
os.environ['OPENAI_API_KEY'] = gmail_apiKey

from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType

# Initialize the agent
llm = OpenAI(temperature=0)

agent = initialize_agent(
    tools=toolkit.get_tools(),
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
)

# GUI for composing and sending an email
layout = [
    [sg.Text("Recipient:", size=(10, 1), justification='right', font="Tahoma, 14"), sg.InputText(key='-TO-', size=(40, 1), font="Tahoma, 14")],
    [sg.Text("Subject:", size=(10, 1), justification='right', font="Tahoma, 14"), sg.InputText(key='-SUBJECT-', size=(40, 1), font="Tahoma, 14")],
    [sg.Text("Body:", size=(10, 1), justification='right', font="Tahoma, 14"), sg.Multiline(key='-BODY-', size=(40, 10), font="Tahoma, 14")],
    [sg.Button('Send', key='-SEND-', font="Tahoma, 14"), sg.Button('EXIT', font="Tahoma, 14"), sg.B('Clear Body', font='Tahoma, 14', button_color=("Brown", "White"))],
    [sg.Multiline(key='-ERRORS-', size=(52, 5), background_color=("Black"),text_color='white', font="Tahoma, 13", disabled=True, autoscroll=True)],
    [sg.Button("Clear Errors")]
]

window = sg.Window('Send or Search Mail', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'EXIT':
        break
    elif event == '-SEND-':
        try:
            recipient = values['-TO-']
            subject = values['-SUBJECT-']
            body = values['-BODY-']
            if recipient == "" and subject == "":
                email_command = f"{body}"
            else:
                email_command = f"Compose an email and send it to: {recipient}, subject: {subject}, body: {body}"
            agent.run(email_command)
        except Exception as e:
            error_message = f"Failed to send email: {str(e)}"
            window['-ERRORS-'].update(error_message)
    elif event == 'Clear Body':
        window["-BODY-"].update("")
    elif event == 'Clear Errors':
        window["-ERRORS-"].update("")

# No need to explicitly close the window as it will close when the loop breaks

#     "Create a gmail draft for me to edit of a letter from the perspective of a sentient parrot"
#     " who is looking to collaborate on some research with her"
#     " estranged friend, a cat. Under no circumstances may you send the message, however."
# )

# print(agent.run("Could you search in my Inbox for the latest five emails and give me their Subjects only?"))

# agent.run(
#     "Create an email Draft for me with Subject 'Get Well soon' to my friend John where I give my apologies for not visiting him at hospital as I was out of the country. Wish him well.")

# agent.run("Compose an email and send it to: gtrialonis@gmail.com, subject: Test 2, body: This is a test Poppy.")
        

# agent.run("Compose an email and send it to"
#           " gtrialonis@gmail.com"
#           " subject: Test 1"
#           " body: This is a test George.")