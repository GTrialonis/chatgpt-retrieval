import os
import sys
import PySimpleGUI as sg
import pyperclip
from datetime import datetime

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

import constants
os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Function to simulate interaction with ChatGPT
def interact_with_chatgpt(query, chat_history):
    # Create the chain with the selected model each time
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model=selected_model),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )
    result = chain({"question": query, "chat_history": chat_history}) # GPT's answer
    return result["answer"]

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = True  # Originally it was "False"
query = None

if len(sys.argv) > 1:
    query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
    print("Reusing index...\n")
    vectorstore = Chroma(
        persist_directory="persist", embedding_function=OpenAIEmbeddings()
    )
    index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
    # loader = TextLoader("data/data.txt")  # Use this line if you only need data.txt
    loader = TextLoader("data/data.txt")
    #loader = DirectoryLoader("data/")
    
    if PERSIST:
        index = VectorstoreIndexCreator(
            vectorstore_kwargs={"persist_directory": "persist"}
        ).from_loaders([loader])
    else:
        index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-4-1106-preview"),
    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []

# Define the theme
sg.theme('Default1')

# Get current date
current_date = datetime.now().strftime("%Y-%m-%d")

# Define the layout
layout = [
    [sg.Text(current_date, key='-DATE-', pad=(5, 10), font=("Helvetica", 12))],
    [sg.Text('Select chatGPT model', font=("Helvetica", 12)), sg.Combo(['gpt-4-1106-preview', 'gpt-4', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-1106', 'gpt-3.5-turbo'], key='-MODEL-', default_value='gpt-4-1106-preview', enable_events=False)],
    [sg.Multiline(key='-OUTPUT-', size=(120, 15), autoscroll=True, disabled=True, font=("Helvetica", 14)),
     sg.Column([
         [sg.Button('Copy', key='-COPY-', size=(4, 1))],
         [sg.Button('Save', key='-SAVE-', size=(4, 1))],
         [sg.Button('Exit', key='-EXIT-', size=(4, 1))],
         [sg.Button('Clear', key='-CLEAR-', size=(4, 1), button_color=('white', 'brown'))]

     ])],
    [sg.InputText(key='-PROMPT-', size=(105, 1), do_not_clear=False, enable_events=True, font=("Helvetica", 12))],
    [sg.Button('Send', bind_return_key=True)]
]

# Create the window
window = sg.Window('ChatGPT Interface', layout, return_keyboard_events=True, finalize=True)
# Bind the Enter key to an action, here we use '-ENTER-' as the event key
window.bind('<Return>', '-ENTER-')
# Force focus on the input field
window['-PROMPT-'].TKEntry.focus_force()

# This will hold the conversation history
chat_history = []

# Event loop
while True:
    event, values = window.read()

    # Set focus to the input field at the start of each loop iteration
    window['-PROMPT-'].set_focus()

    # If user closes window or clicks exit
    if event in (None, '-EXIT-', sg.WIN_CLOSED):
        break
    if event == '-CLEAR-':
        window['-OUTPUT-'].update('')

    # When the user presses the 'Send' button or the Enter key
    if event in ('Send', '-ENTER-') and values['-PROMPT-']:
        # Retrieve the selected model from the dropdown
        selected_model = values['-MODEL-']

        # Map the selection to the actual model names used by OpenAI
        model_map = {
            'gpt-4-1106-preview': 'gpt-4-1106-preview',
            'gpt-4': 'gpt-4',
            'gpt-3.5-turbo-16k': 'gpt-3.5-turbo-16k',
            'gpt-3.5-turbo-1106': 'gpt-3.5-turbo-1106',
            'gpt-3.5-turbo': 'gpt-3.5-turbo'
}
        actual_model = model_map.get(selected_model, 'default-model-if-none-selected')

        # Get the user's input
        prompt = values['-PROMPT-']
        # Send the prompt to the ChatGPT interaction function
        response = interact_with_chatgpt(prompt, chat_history)
        # Append the response to the chat history
        chat_history.append((prompt, response))
        # Update the output Multiline with the response
        window['-OUTPUT-'].update(f'You: {prompt}\n\nChatGPT: {response}\n\n', append=True)
        # Clear the input field after sending the message
        window['-PROMPT-'].update('')
        # Force focus back to the input field
        window['-PROMPT-'].TKEntry.focus_force()
        

    # Copy chat responses to clipboard
    if event == '-COPY-':
        responses = values['-OUTPUT-']
        pyperclip.copy(responses)

    # Save chat responses to a file
    if event == '-SAVE-':
        responses = values['-OUTPUT-']
        with open('chat_responses.txt', 'w') as file:
            file.write(responses)
        sg.popup('Responses saved!', keep_on_top=True)

# Finish up by removing from the screen
window.close()
