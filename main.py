import PySimpleGUI as sg

import os.path


from selenium import webdriver
from csv import reader
import time
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.common.action_chains import ActionChains

import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

import time
import datetime
import os,csv
import argparse
import platform
import logging
import itertools


from utilities import *

current_dir = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
logdir = os.path.join(current_dir, 'logs')
if not os.path.exists(logdir):
    os.makedirs(logdir)
logfile = os.path.join(logdir,'app.log')

f_handler = logging.FileHandler(logfile)


# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)


### settings

driver_path = os.path.join(current_dir,'driver','chromedriver')
UserDataDir = os.path.join(current_dir, 'data','User_Data')

sg.theme('Light Grey1')

# SenderList=[]
if not os.path.exists(UserDataDir):
    os.makedirs(UserDataDir)
    SenderList=[]
else:
    SenderList = os.listdir(UserDataDir)
driver=None



# First the window layout in 2 columns
file_list_column = [
    [
        sg.Text("Contacts list folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(20, 20), key="-FILE LIST-"
        )
    ],
]


# For now will only show the name of the file that was chosen

Sender_column = [
    [sg.In(size=(10, 1), enable_events=True, key="-SenderName-"), sg.Button('Register sender')],  
    [sg.Text("{} sender registered".format(len(SenderList))) ],
    [  sg.Listbox( values=[], enable_events=True, size=(40, 5), key="-SenderList-" ) ],
    #  sg.Text(text=ExistingSenderList, key='-ExistingSenderList-') ],  
    [ sg.Text("Message per registered sender"), sg.In(size=(10,1), enable_events=True, key='-TaskPerNumber-') ],
    [sg.Text("Contact"), sg.In(size=(10, 1), enable_events=True), sg.FileBrowse(key="-ContactPath-")],
    # [sg.Multiline(size=(30, 10), font=("Arial",11), text_color='black', key='-MLINE-') ],
    [sg.Text("Message file"), sg.In(size=(10, 1), enable_events=True), sg.FileBrowse(key="-messagepath-")],
    [sg.Text(size=(12,1), key='-STATUS-')],
    [sg.Button('Start')]
]

# ----- Full layout -----

layout = [
    [
        sg.Column(Sender_column,vertical_alignment='rigth', justification='right'),
        # sg.VSeperator(),
        # sg.Column(file_list_column)        
    ]
]

window = sg.Window("WhatsApp Жарнама Жіберу бағдарламасы", layout,resizable=True, finalize=True, location=(0,0))
window['-SenderList-'].update(SenderList)

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
        
        index=len(SenderList)
        options = webdriver.ChromeOptions()
        UserDataDirPath=os.path.join(UserDataDir,values["-SenderName-"])
        options.add_argument('--user-data-dir={}'.format(UserDataDirPath))

        driver = webdriver.Chrome(driver_path,chrome_options=options)
        driver.get("https://web.whatsapp.com/")
        time.sleep(5)
        SenderList.append(values["-SenderName-"])
        window['-SenderList-'].update(SenderList)
        window.Refresh()
        print('Register sender',SenderList)
    elif event == 'Start':
        print('started')
        contacts = loadTxt2list(values['-ContactPath-'])
        print('{} contacts loaded'.format(len(contacts)))
        import io
        with io.open(values['-messagepath-'],'r',encoding='utf8') as f:
            message = f.read()

        # messages = loadTxt2list(values['-messagepath-'])
        # message = ' '.join(messages)
        
        n=0
        ThisSenderSent=0
        TotalSent=0
        iterator=itertools.cycle(SenderList)
        Sender = next(iterator)
        while TotalSent<len(contacts):
            options = webdriver.ChromeOptions()
            UserDataDirPath=os.path.join(UserDataDir,Sender)
            options.add_argument('--user-data-dir={}'.format(UserDataDirPath))

            driver = webdriver.Chrome(driver_path,chrome_options=options)
            driver.get("https://web.whatsapp.com/")

            if TotalSent==0:
                print('opening first time')
                time.sleep(15)
            else:
                time.sleep(7)
            
            for PhoneNumber in contacts:
                if SendMessage(driver,PhoneNumber,message):
                    ThisSenderSent+=1
                    TotalSent+=1
                if ThisSenderSent>= int(values['-TaskPerNumber-']):
                    driver.quit()
                    # driver=None
                    Sender = next(iterator)
                    
                    UserDataDirPath = UserDataDirPath=os.path.join(UserDataDir,Sender)
                    options.add_argument('--user-data-dir={}'.format(UserDataDirPath))

                    driver = webdriver.Chrome(driver_path,chrome_options=options)
                    # driver.get("https://web.whatsapp.com/")
                    ThisSenderSent=0
                    time.sleep(10)

                print('Sender: {}, ThisSenderSent: {}'.format(Sender,ThisSenderSent))   
            status = "{}/{} номерге жіберілді".format(TotalSent,len(contacts))
            window['-STATUS-'].update(status)

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