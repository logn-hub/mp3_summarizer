import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread

class Watcher:
    def __init__(self, directory_to_watch):
        self.observer = Observer()
        self.DIRECTORY_TO_WATCH = directory_to_watch

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_created(event):
        if event.is_directory:
            return None
        elif event.src_path.endswith(".mp3"):
            print(f"find! - {event.src_path}")
            Handler.process_file(event.src_path)

    @staticmethod
    def process_file(file_path):
        try:
            result = subprocess.run(["python", "summarize_audio.py", file_path], check=True, capture_output=True, text=True)
            print(f"Processing output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error during processing: {e.stderr}")

def select_directory():
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    if directory:
        messagebox.showinfo("Selected Directory", f"You selected: {directory}")
        return directory
    else:
        messagebox.showwarning("No Directory Selected", "No directory was selected. Exiting.")
        return None

def start_watcher(directory):
    w = Watcher(directory)
    w.run()

if __name__ == '__main__':
    selected_directory = select_directory()
    if selected_directory:
        watcher_thread = Thread(target=start_watcher, args=(selected_directory,))
        watcher_thread.start()
