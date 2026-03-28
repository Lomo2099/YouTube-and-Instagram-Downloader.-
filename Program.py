import customtkinter as ctk
import yt_dlp
import threading
import os
from tkinter import messagebox

# Set the appearance of the app
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Media Downloader Pro")
        self.geometry("600x400")

        # --- UI Elements ---
        self.label = ctk.CTkLabel(self, text="YouTube & Instagram Downloader", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)

        # URL Entry
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste your link here...", width=450)
        self.url_entry.pack(pady=10)

        # Radio buttons for Format Selection
        self.format_var = ctk.StringVar(value="mp4")
        self.radio_frame = ctk.CTkFrame(self)
        self.radio_frame.pack(pady=10)

        self.mp4_radio = ctk.CTkRadioButton(self.radio_frame, text="Video (MP4)", variable=self.format_var, value="mp4")
        self.mp4_radio.grid(row=0, column=0, padx=20, pady=10)

        self.mp3_radio = ctk.CTkRadioButton(self.radio_frame, text="Audio (MP3)", variable=self.format_var, value="mp3")
        self.mp3_radio.grid(row=0, column=1, padx=20, pady=10)

        # Download Button
        self.download_btn = ctk.CTkButton(self, text="Download Now", command=self.start_download_thread)
        self.download_btn.pack(pady=20)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", text_color="gray")
        self.status_label.pack(pady=10)

    def update_status(self, text, color="white"):
        self.status_label.configure(text=f"Status: {text}", text_color=color)

    def start_download_thread(self):
        # We use threading so the GUI stays responsive during the download
        link = self.url_entry.get().strip()
        if not link:
            messagebox.showwarning("Empty URL", "Please paste a link first!")
            return

        self.download_btn.configure(state="disabled")
        self.update_status("Initializing...", "yellow")

        thread = threading.Thread(target=self.download_media, args=(link, self.format_var.get()))
        thread.start()

    def download_media(self, link, choice):
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            # Add a progress hook to update the status label
            'progress_hooks': [self.progress_hook],
        }

        if choice == 'mp4':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
        else:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            self.update_status("Download Complete!", "green")
            messagebox.showinfo("Success", "Media downloaded successfully!")
        except Exception as e:
            self.update_status("Error Occurred", "red")
            messagebox.showerror("Error", str(e))
        finally:
            self.download_btn.configure(state="normal")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            self.update_status(f"Downloading... {p}", "cyan")
        elif d['status'] == 'finished':
            self.update_status("Processing file...", "orange")

if __name__ == "__main__":
    app = App()
    app.mainloop()
