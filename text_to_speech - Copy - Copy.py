from tkinter import *
import pyttsx3
import pygame
import docx2txt
import os
import PyPDF2
from tkinter import filedialog, messagebox
import pyaudio
import wave

pygame.mixer.init()
engine = pyttsx3.init()

root = Tk()
root.geometry("500x500")
root.title("Text To Speech")

def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/", title = "select a File", filetypes = (("Text files", "*.txt."),("pdf files", "*.pdf."), ("all files", "*.*")))  
    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(filename)
        page = len(reader.pages)
        for i in range (page):
            pp = reader.pages[i]
            bb="Content On Page:" +str(i+1)
            
            text.insert(END,bb)
            
    
            text.insert(END,pp.extract_text())

    elif filename.endswith(".docx"):
        do = docx2txt.process(filename)
        text.insert(END, do)

    elif filename.endswith(".txt"):
        tx = open(filename)
        tx_read = tx.read()
        text.insert(END, tx_read)
    else:
        messagebox.showwarning("Warning", "This can support only pdf, docx and txt files.")
        
def read_stop():
    if read_stop_button['text']=='Read':
        read_stop_button.config(text='Stop')
        #engine.setProperty('rate', 10)
        #engine.setProperty('rate', 50)
        #engine.setProperty('rate', 100)
        #engine.setProperty('rate', 165)
        
    

        engine.save_to_file(text.get('1.0', END), "temp.wav")
        engine.runAndWait()
    
        pygame.mixer.init()
        pygame.mixer.music.load("temp.wav")
        pygame.mixer.music.play()
    else:
        read_stop_button.config(text='Read')
        pygame.mixer.music.stop()
        '''while pygame.mixer.music.get_busy(): pass
        pygame.mixer.music.unload()
        os.remove('temp.wav')'''
    
def pause_unpause():
    if pause_unpause_button['text']=='Pause':
        pause_unpause_button.config(text='Unpause')
        pygame.mixer.music.pause()
    else:
        pause_unpause_button.config(text='Pause')
        pygame.mixer.music.unpause()
    
def exit():
    root.destroy()

def clear():
    text.delete('1.0', END)
    while pygame.mixer.music.get_busy(): pass
    pygame.mixer.music.unload()
    os.remove('temp.wav')

voices = engine.getProperty('voices')
def male():
    engine.setProperty('voice', voices[0].id)

def female():
    engine.setProperty('voice', voices[1].id)

def loop_on():
    p = pyaudio.PyAudio()
    audio_file="temp.wav"
    wf = wave.open(audio_file, 'rb')

    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )

    while True:
        data=wf.readframes(1024)
        if not data:
            wf.rewind()
            data=wf.readframes(1024)
        stream.write(data)
def loop_off():
    stream.stop_stream()
    stream.close()
    wf.close()
    p.terminate()
    
#Playback speed

#def playback_speed():
    
sc = Scrollbar(root, orient='vertical')
sc.pack(side=RIGHT, fill=Y )

text = Text(root, width=165, height=30,wrap=CHAR, yscrollcommand=sc.set)
text.pack(side=TOP)

sc.config(command = text.yview)

add_button = Button(root, text="Add File", command=browseFiles)
add_button.place(x=400,y=500)

read_stop_button = Button(root, text="Read", command=read_stop)
read_stop_button.place(x=500,y=500)

pause_unpause_button = Button(root, text="Pause", command=pause_unpause)
pause_unpause_button.place(x=600,y=500)

exit_button = Button(root, text="Clear", command=clear)
exit_button.place(x=400,y=600)

clear_button = Button(root, text="Exit", command=exit)
clear_button.place(x=500,y=600)
#Label and radio button
v = StringVar(root, "Male")
label1 = Label(root, text = "Voice : ").place (x = 705, y = 600)
r1 = Radiobutton(root, text = "Male", variable = v, value="Male", command=male).place(x = 750, y = 600)
r2 = Radiobutton(root, text = "Female", variable = v, value="Female", command=female).place(x =750, y = 620)

#Label and radio button for audio loop
ra = StringVar(root, "Off")
label = Label(root, text = "Audio_Loop :").place (x = 850, y = 600)
r3 = Radiobutton(root, text = "On", variable = ra, value = "On", command = loop_on).place (x = 930, y = 600)
r4 = Radiobutton(root, text = "Off", variable = ra, value = "Off", command = loop_off).place (x = 930, y = 620)

#combo box
b = StringVar()
b.set("Normal")
label2 = Label(root, text = "Playback Speed : ").place (x = 700, y = 500)
combo = OptionMenu(root, b,"0.25x", "0.5x", "0.75x", "Normal", "1.25x", "1.5", "1.75x", "2x").place(x = 800, y = 495)

mainloop()
