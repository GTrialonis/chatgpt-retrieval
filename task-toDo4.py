import sys
sys.path.append('/Users/georgiostrialonis/chatgpt_retrieval/chatgpt-retrieval')
# print('the sys path is: ',sys.path)  # for debugging
import subprocess # --- new line
import PySimpleGUI as sg
# import traceback
import json
from datetime import datetime
import requests
import threading
import os
from constants import apiKey

thread_finished = False
weather_info_shared = None


def threaded_search_weather(city):
    global weather_info_shared
    weather_info_shared = search_weather(city)


def load_tasks():
    try:
        with open("/Users/georgiostrialonis/task_list2.txt", "r") as file:
            content = file.read()
            return json.loads(content) if content else []
    except FileNotFoundError:
        return []

def load_archive_done_tasks():
    try:
        with open("/Users/georgiostrialonis/arch_tasks_done.txt", "r") as file:
            content2 = file.read()
            loaded_content = json.loads(content2) if content2 else []
            return loaded_content
    except FileNotFoundError:
        return []

def save_tasks():
    with open("/Users/georgiostrialonis/task_list2.txt", "w") as file:
        file.write(json.dumps(tasks))

def display_tasks():
    task_str = "\n".join(
        [
            f"{i+1}. {task['description']} - {task['status']}"
            for i, task in enumerate(tasks)
        ]
    )
    window["tasks_multiline"].update(task_str)


def clear_multiline_window():
    window["tasks_multiline"].update("")

def search_weather(city):
    apiUrl = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&units=metric"
    try:
        r = requests.get(url=apiUrl)

        if r.status_code == 200:
            data = r.json()

            description = data['weather'][0]['description']
            temperature = data['main']['temp']
            wind_speed = data['wind']['speed']
            humidity = data['main']['humidity']

            wind_speed_kmh = float(wind_speed) * 3.6  # Convert to km/h
            weather_info = f"Weather information:\n\nCity: {city}\nTemperature: {temperature} °C\nDescription: {description}\nHumidity: {humidity}%\nWind Speed: {wind_speed_kmh:.2f} km/h"
            return weather_info
        else:
            return "Error: Unable to fetch weather data."
    except requests.RequestException as e:
        return "Error: Request failed."
    except json.JSONDecodeError:
        print("Error: Response is not in JSON format.")
        return "Error: Invalid response format."

def delete_archive(archive_window):
    with open("/Users/georgiostrialonis/arch_tasks_done.txt", "w") as file:
        file.write(json.dumps([]))
    archive_window["-DONE-"].update("Archive Deleted permanently")
    archive_window["-DONE-"].update("")
### --------------------------------------------------------------
def display_notes(location=(600, 100)):
    notes_layout = [
        [sg.Text("Take notes below")],
        [sg.Multiline(size=(80, 15), font="Tahoma, 14", key="-NOTES-")],
        [sg.Button("SAVE", button_color=("White", "DarkBlue"), key="-SAVE-", disabled=True), sg.Button("CLEAR"), sg.Button("EXIT")]
    ]
    notes_window = sg.Window(
        "Window for taking notes", notes_layout, location=location, finalize=True
    )

    # Load and display the notes from the file and disable the 'SAVE' button
    try:
        with open('/Users/georgiostrialonis/notes-taken.txt', 'r') as file:
            notes_content = file.read()
            notes_window['-NOTES-'].update(notes_content)
            notes_window['-SAVE-'].update(disabled=True)  # Disable the SAVE button initially
    
    except FileNotFoundError:
        sg.popup('Error', 'File not found. Please check file path')

    # Event loop to process "events"
    while True:
        notes_event, notes_values = notes_window.read()

        #print(f"Event: {notes_event}")  # Debug print for any event

        if notes_event in (sg.WIN_CLOSED, 'EXIT'):  # If user closes window or clicks EXIT
            break

        elif notes_event == '-SAVE-':
            # Retrieve the text from the multiline input
            text_to_save = notes_values['-NOTES-'].rstrip() + '\n'

            # Save to the first file (overwrite the file)
            notes_file_path = '/Users/georgiostrialonis/notes-taken.txt'
            try:
                with open(notes_file_path, 'a') as file:
                    file.write(text_to_save)
            
            except Exception as e:
                print(f"Failed to save to {notes_file_path}: {e}")  # Print any exception

            # Save to the second file (append to the file)
            archive_file_path = '/Users/georgiostrialonis/chatgpt_retrieval/chatgpt-retrieval/data/archived_tasks.txt'
            try:
                with open(archive_file_path, 'a') as file:
                    file.write(text_to_save)
                    
            except Exception as e:
                print(f"Failed to append to {archive_file_path}: {e}")  # Print any exception

            # Show a popup message to confirm saving
            sg.popup('Saved!', 'Your notes have been saved successfully.')

            # Disable the SAVE button after saving
            notes_window['-SAVE-'].update(disabled=True)

        elif notes_event == 'CLEAR':
            # Clear the notes in the window and enable the 'SAVE' button
            notes_window['-NOTES-'].update('')
            notes_window['-SAVE-'].update(disabled=False)

    notes_window.close()

### ---------------------------------------------------------------------

def display_archive(location=(300, 70)):
    archive_window_layout = [
        [sg.Text("Archived Tasks DONE")],
        [sg.Multiline(size=(90, 20), font="Tahoma, 14", key="-DONE-", background_color='LightYellow')],
        [sg.B("Delete One"), sg.B("Edit"), sg.B("Delete All DONE"), sg.B("EXIT")],
    ]

    archive_window = sg.Window(
        "Archived DONE tasks", archive_window_layout, location=location, finalize=True
    )

    # Add this block to update the task list immediately when the window opens
    done_task_str = "\n".join(
        [f"{i+1}. {done_task['description']}" for i, done_task in enumerate(archive)]
    )
    archive_window["-DONE-"].update(done_task_str)

    while True:
        event, values = archive_window.read()

        if event in (sg.WIN_CLOSED, "EXIT"):
            break

        elif event == "Delete All DONE":
            response = sg.popup_yes_no(
                "Are you sure you want to delete all archived tasks?", background_color="dark red"
            )
            if response == "Yes":
                delete_archive(archive_window)
                archive_window["-DONE-"].update("")
            else:
                sg.popup("Operation cancelled.")

        # Deleting a task from the archive
        if event == "Delete One":
            task_num_input = sg.popup_get_text("Which task to delete?")
            if task_num_input and task_num_input.isdigit():
                task_num_to_delete = int(task_num_input) - 1
                if 0 <= task_num_to_delete < len(archive):
                    del archive[task_num_to_delete]

                    # Save after deleting
                    with open("/Users/georgiostrialonis/arch_tasks_done.txt", "w") as f:
                        json.dump(archive, f)
                else:
                    sg.popup_error("Invalid task number. Try again!")

            # Convert list to a single string with new lines
            archived_task_deleted_string = "\n".join(
                [f"{idx+1}. {task['description']}" for idx, task in enumerate(archive)]
            )

            # Then update your GUI element with this new string
            archive_window["-DONE-"].update(archived_task_deleted_string)

        # Editing DONE tasks
        if event == "Edit":
            done_task_num_input = sg.popup_get_text("Which done task to edit? ")
            if done_task_num_input and done_task_num_input.isdigit():
                done_task_num_toEdit = int(done_task_num_input) - 1
                if 0 <= done_task_num_toEdit < len(archive):
                    new_task_done_description = sg.popup_get_text(
                        "Enter new description:",
                        default_text=archive[done_task_num_toEdit]["description"],
                    )
                    if new_task_done_description:
                        archive[done_task_num_toEdit][
                            "description"
                        ] = new_task_done_description
                        # Save edited archive
                        with open(
                            "/Users/georgiostrialonis/arch_tasks_done.txt", "w"
                        ) as f:
                            json.dump(archive, f)
                        # ------ OPTIONAL LINES ------
                        # Append the edited task line to script file 'chatGPT-interface.py'
                        # where the user interacts with the saved tasks.
                        # Remove these OPTIONAL LINES if no script file exists.
                        with open("/Users/georgiostrialonis/chatgpt_retrieval/chatgpt-retrieval/data/archived_tasks.txt", "a") as file:
                            file.write(new_task_done_description + "\n")

                    else:
                        sg.popup_error("Invalid task number. Try again!")
                else:
                    sg.popup_error("Invalid input. Please enter a valid number!")

            archived_task_strings = "\n".join(
                [f"{idx+1}. {task['description']}" for idx, task in enumerate(archive)]
            )

            # Then update your GUI element with this new string
            archive_window["-DONE-"].update(archived_task_strings)

    archive_window.close()

tasks = load_tasks()
archive = load_archive_done_tasks()

main_layout = [
    [sg.Text('Type your to-do-Task and hit "Add Task" to save')],
    [
        sg.Input(
            size=(50, 4), font=("Times New Roman", 14), key="task", do_not_clear=False
        )
    ],
    [
        sg.Button("Add Task"),
        sg.Button("Delete Task"),
        sg.Button("Display Tasks"),
        sg.Button("Mark as DONE"),
        sg.Button("Edit Task"),
        sg.Button("LangChain", button_color=('White', 'Green'), key="LangChain"),
    ],
    [sg.Multiline(size=(60, 13), font="Tahoma 14", key="tasks_multiline")],
    [
        sg.Button("Close"),
        sg.Button("Clear Multiline Window"),
        sg.Button("Archive DONE"),
        sg.Button("View Archive"),
        sg.Button("Get Weather", button_color=('Black', 'LightBlue')),
        sg.Button("NOTES", button_color=('White', 'Brown'))
    ],
]

window = sg.Window("Things I should do", main_layout, location=(50,50), finalize=True)
window.bind("<Return>", "Enter")


while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Close":
        save_tasks()
        break

    if event == "NOTES":
        display_notes()
# ***** ------------------- LANGCHAIN ------ ********
    if event == "LangChain":
        with open('/Users/georgiostrialonis/task-toDo4-error-log.txt', 'a') as f:
            f.write("LangChain button was clicked.\n")

    # Log information about the environment
        with open('/Users/georgiostrialonis/task-toDo4-logfile.txt', 'w') as f:
            f.write(f"Current Conda environment: {os.environ.get('CONDA_DEFAULT_ENV', 'No active environment')}\n")
        with open('/Users/georgiostrialonis/task-env_log.txt', 'w') as f:
            for key, value in os.environ.items():
                f.write(f"{key}: {value}\n")

    # Now launch chatGPT-interface.py
        process = subprocess.Popen(
    ['/bin/bash', '-c', 'python3 /Users/georgiostrialonis/chatgpt_retrieval/chatgpt-retrieval/chatGPT-interface.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
)
        # ---- This can also be removed. Used for debugging----
        stdout, stderr = process.communicate()
        with open('/Users/georgiostrialonis/task-toDo4-output-log.txt', 'wb') as f:
            f.write(stdout)
        with open('/Users/georgiostrialonis/task-toDo4-error-log.txt', 'wb') as f:
            f.write(stderr)
        # ----------------------------------------
    if event == "Get Weather":
        # Define the popup layout here, inside the 'Get Weather' event
        popup_layout = [
            [sg.Text("Weather Information")],
            [sg.Input(size=(40, 1), key="-CITY-", font=('Helvetica', 14)), sg.Button("Enter City")],
            [sg.Multiline(size=(50, 10), font=('Helvetica', 16), key="-WEATHER-")]
        ]
        popup_window = sg.Window("Weather Information", popup_layout, finalize=True)

        while True:
            popup_event, popup_values = popup_window.read(timeout=100)

            if popup_event in (sg.WIN_CLOSED, 'EXIT'):
                break

            if popup_event == 'Enter City':
                threading.Thread(target=threaded_search_weather, args=(popup_values['-CITY-'],), daemon=True).start()

            if weather_info_shared is not None:
                popup_window["-WEATHER-"].update(weather_info_shared)
                weather_info_shared = None

        popup_window.close()
# ---- End of weather extraction section --------------- 
        
    if event == "Clear Multiline Window":
        clear_multiline_window()

    if event == "Add Task" or event == "Enter":
        new_task = {"description": values["task"], "status": "not done"}
        tasks.append(new_task)
        save_tasks()
        display_tasks()
        window["task"].update("")

    if event == "Display Tasks":
        display_tasks()

    if event == "Edit Task":
        display_tasks()
        task_number_input = sg.popup_get_text(
            "Which task number would you like to edit?"
        )
        if task_number_input and task_number_input.isdigit():
            task_number_to_edit = int(task_number_input) - 1
            if 0 <= task_number_to_edit < len(tasks):
                new_description = sg.popup_get_text(
                    "Enter new description:",
                    default_text=tasks[task_number_to_edit]["description"],
                )
                if new_description:
                    tasks[task_number_to_edit]["description"] = new_description
                    save_tasks()
                    display_tasks()
                else:
                    sg.popup_error("Invalid task number. Please enter a valid number.")
            else:
                sg.popup_error("Invalid input. Please enter a valid number.")

    if event == "Mark as DONE":
        display_tasks()
        task_number_input = sg.popup_get_text(
            "Which task number to mark as DONE?", "Mark as DONE"
        )
        if task_number_input and task_number_input.isdigit():
            task_number = int(task_number_input) - 1
            if 0 <= task_number < len(tasks):
                tasks[task_number]["status"] = "DONE"
                save_tasks()
                display_tasks()
            else:
                sg.popup_error("Invalid task number. Please enter a valid number.")

    if event == "Archive DONE":
        # Load existing archived tasks
        archive = load_archive_done_tasks()

        # Prepare a dictionary to make it easier to look up tasks by their description
        archive_dict = {task["description"]: task for task in archive}

        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Find tasks marked as 'DONE' and append or update them in the archive
        for task in tasks:
            if "DONE" in task["status"]:
                new_description = f"{task['description']} OK {current_date}"
                # print(new_description)
                task["description"] = new_description  # Updating the task description
                archive_dict[new_description] = task  # This will add or update the task
                # ------- OPTIONAL LINES ----------
                # Add the newly archived task to script file 'chatGPT-interface.py'
                # for interaction with the user.
                # Else, delete these OPTIONAL lines.
                with open("/Users/georgiostrialonis/chatgpt_retrieval/chatgpt-retrieval/data/archived_tasks.txt", "a") as file:
                    file.write(new_description + "\n")
                # ------ END of OPTIONAL LINES ----

        # Convert back to list and save the archive
        archive = list(archive_dict.values())
        with open("/Users/georgiostrialonis/arch_tasks_done.txt", "w") as f:
            json.dump(archive, f)

        # Refresh the archive
        archive = load_archive_done_tasks()

    if event == "View Archive":
        display_archive()

    if event == "Delete Task":
        display_tasks()
        task_number_input = sg.popup_get_text(
            "Which task to delete (number?)", "Delete Task"
        )
        if task_number_input and task_number_input.isdigit():
            task_number = int(task_number_input) - 1
            if 0 <= task_number < len(tasks):
                del tasks[task_number]
                save_tasks()
                display_tasks()
            else:
                sg.popup_error("Invalid task number. Please enter a valid number.")
        else:
            sg.popup_error("Invalid input. Please enter a valid number.")

window.close()
