import PySimpleGUI as sg

import os.path

sg.theme('Light Grey1')

# First the window layout in 2 columns
file_list_column = [
    [
        sg.Text("Contacts list folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]


# For now will only show the name of the file that was chosen

Sender_column = [
    [sg.Text("Where to save WhatsApp sender login data?"), sg.In(size=(25, 1), enable_events=True, key="-Sender data-"), sg.FolderBrowse()],
    [sg.Text("Number of sender"), sg.In(size=(10, 1), enable_events=True, key="-NumSender-"), sg.Button('Register sender')],    
    [sg.Multiline(size=(80, 30), font='Arial 10', text_color='black', key='-MLINE-')],

    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
]


# ----- Full layout -----

layout = [
    [
        sg.Column(Sender_column),
        sg.VSeperator(),
        sg.Column(file_list_column)
        
        
    ]
]

window = sg.Window("WhatsApp Жарнама Жіберу бағдарламасы", layout)


# Run the Event Loop

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        print('folder',folder)
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(os.path.join(folder, f))
            # and f.lower().endswith((".png", ".gif"))
        ]

        window["-FILE LIST-"].update(fnames)
    
    if event == "Register sender":
        print('Register sender')

    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(filename)
            window["-IMAGE-"].update(filename=filename)
        except:
            pass


window.close()