### MAKE SURE YOU HAVE THE THREE NECESSARY API keys to run each python script individually or in combination. Also make sure the PATHS in each script are correct for your system.

### From chatgpt-retrieval choose the 'chatGPT-interface.py', a stand-alone script, to interact with your files, with the files in the data folder and with the Internet. If you don't need the Gmail button then delete it and also the lines for the gmail API key. But you do need and OpenAI API key to run this script.

## chatgpt.py <-- You can interact as above but only on your IDE terminal or system terminal

### I included 'task-toDo4 which you can run individually. If you don't want to use the 'Get Weather' button, delete it and the lines related to the API key.
### -----------------------------------------------------------

Simple script to use ChatGPT on your own files.

Here's the [YouTube Video](https://youtu.be/9AXP7tCI9PI).

## Installation

Install [Langchain](https://github.com/hwchase17/langchain) and other required packages.
```
pip install langchain openai chromadb tiktoken unstructured
```
Modify `constants.py.default` to use your own [OpenAI API key](https://platform.openai.com/account/api-keys), and rename it to `constants.py`.

Place your own data into `data/data.txt`.

## Example usage
Test reading `data/data.txt` file.
```
> python chatgpt.py "what is my dog's name"
Your dog's name is Sunny.
```

Test reading `data/cat.pdf` file.
```
> python chatgpt.py "what is my cat's name"
Your cat's name is Muffy.
```
