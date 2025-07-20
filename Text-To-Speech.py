import os
import threading
import pyttsx3
import PyPDF2
import docx2txt
import pygame
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar
import customtkinter as ctk

# --- Initialize ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Text To Speech")
root.geometry("900x600")

engine = pyttsx3.init()
voices = engine.getProperty('voices')

current_page = 0
pdf_reader = None
audio_file = "temp_audio.wav"
is_playing = False
is_paused = False

# --- Load File ---
def load_file():
    global pdf_reader, current_page
    file_path = filedialog.askopenfilename(filetypes=[
        ("PDF Files", "*.pdf"),
        ("Word Files", "*.docx"),
        ("Text Files", "*.txt")
    ])
    if not file_path:
        return
    textbox.delete("1.0", "end")
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            current_page = 0
            display_pdf_page()
    elif file_path.endswith(".docx"):
        text = docx2txt.process(file_path)
        textbox.insert("1.0", text)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            textbox.insert("1.0", f.read())

def display_pdf_page():
    if pdf_reader:
        total_pages = len(pdf_reader.pages)
        if 0 <= current_page < total_pages:
            page_text = pdf_reader.pages[current_page].extract_text()
            textbox.delete("1.0", "end")
            textbox.insert("1.0", page_text)
            page_label.configure(text=f"Page: {current_page + 1} / {total_pages}")

def next_page():
    global current_page
    if pdf_reader and current_page < len(pdf_reader.pages) - 1:
        current_page += 1
        display_pdf_page()

def prev_page():
    global current_page
    if pdf_reader and current_page > 0:
        current_page -= 1
        display_pdf_page()

# --- Voice Settings ---
def set_voice_and_speed():
    voice_choice = voice_var.get()
    engine.setProperty('voice', voices[0].id if voice_choice == "Male" else voices[1].id)
    rate_choice = playback_var.get()
    rates = {"0.5x": 100, "0.75x": 150, "Normal": 200, "1.5x": 250, "2.0x": 300}
    engine.setProperty('rate', rates.get(rate_choice, 200))

# --- Convert Text to Audio File ---
def convert_to_audio_file():
    content = textbox.get("1.0", "end").strip()
    if not content:
        messagebox.showinfo("No text", "Load or type some text first!")
        return False
    set_voice_and_speed()
    engine.save_to_file(content, audio_file)
    engine.runAndWait()
    return True

# --- Audio Controls ---
def play_audio():
    global is_playing, is_paused
    if is_playing:
        return
    def _play():
        global is_playing
        if convert_to_audio_file():
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            is_playing = True
    threading.Thread(target=_play, daemon=True).start()

def pause_resume_audio():
    global is_paused
    if not is_playing:
        return
    if not is_paused:
        pygame.mixer.music.pause()
        pause_button.configure(text="Resume")
        is_paused = True
    else:
        pygame.mixer.music.unpause()
        pause_button.configure(text="Pause")
        is_paused = False

def stop_audio():
    global is_playing, is_paused
    if is_playing:
        pygame.mixer.music.stop()
        is_playing = False
        is_paused = False
        pause_button.configure(text="Pause")

# --- Other Functions ---
def clear_text():
    textbox.delete("1.0", "end")

def save_audio():
    content = textbox.get("1.0", "end").strip()
    if not content:
        messagebox.showinfo("No text", "No text to save as audio!")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
    if save_path:
        set_voice_and_speed()
        engine.save_to_file(content, save_path)
        engine.runAndWait()
        messagebox.showinfo("Saved", f"Audio saved as {save_path}")

def switch_theme(choice):
    ctk.set_appearance_mode(choice)

def exit_app():
    stop_audio()
    root.destroy()

# --- UI Layout ---
top_frame = ctk.CTkFrame(root)
top_frame.pack(pady=10)

voice_var = StringVar(value="Male")
playback_var = StringVar(value="Normal")
theme_var = StringVar(value="System")

ctk.CTkButton(top_frame, text="Add File", command=load_file).pack(side="left", padx=5)
ctk.CTkOptionMenu(top_frame, variable=voice_var, values=["Male", "Female"]).pack(side="left", padx=5)
ctk.CTkOptionMenu(top_frame, variable=playback_var, values=["0.5x", "0.75x", "Normal", "1.5x", "2.0x"]).pack(side="left", padx=5)
ctk.CTkOptionMenu(top_frame, variable=theme_var, values=["Light", "Dark", "System"], command=switch_theme).pack(side="left", padx=5)

textbox = ctk.CTkTextbox(root, height=300, width=800, font=("Arial", 12))
textbox.pack(pady=10)

page_control_frame = ctk.CTkFrame(root)
page_control_frame.pack(pady=5)
ctk.CTkButton(page_control_frame, text="Previous Page", command=prev_page).pack(side="left", padx=10)
page_label = ctk.CTkLabel(page_control_frame, text="Page: 0 / 0")
page_label.pack(side="left", padx=10)
ctk.CTkButton(page_control_frame, text="Next Page", command=next_page).pack(side="left", padx=10)

control_frame = ctk.CTkFrame(root)
control_frame.pack(pady=10)

ctk.CTkButton(control_frame, text="Play", command=play_audio).pack(side="left", padx=10)
pause_button = ctk.CTkButton(control_frame, text="Pause", command=pause_resume_audio)
pause_button.pack(side="left", padx=10)
ctk.CTkButton(control_frame, text="Stop", command=stop_audio).pack(side="left", padx=10)
ctk.CTkButton(control_frame, text="Save as Audio", command=save_audio).pack(side="left", padx=10)
ctk.CTkButton(control_frame, text="Clear", command=clear_text).pack(side="left", padx=10)
ctk.CTkButton(control_frame, text="Exit", command=exit_app).pack(side="left", padx=10)

progress_bar = ctk.CTkProgressBar(root)
progress_bar.set(0)
progress_bar.pack(fill="x", padx=20, pady=10)

root.mainloop()
