### MAKE SURE YOU HAVE THE TREE NECESSARY API keys to run each python script individually or in combination. Also make sure the PATHS in each script are correct for your system.

### From chatgpt-retrieval choose the 'chatGPT-interface.py', a stand-alone script, to interact with your files, with the files in the data folder and with the Internet.

## chatgpt.py <-- You can interact as above but only on your IDE terminal or system terminal

### This project combines with another script, which is not included here, the 'task-toDo4.py'
### ------------------------------------------------------------

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
