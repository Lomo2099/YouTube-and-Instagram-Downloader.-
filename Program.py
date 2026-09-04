import os
import shutil
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp

class YTDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Video Downloader")
        self.root.geometry("620x460")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=os.path.abspath("downloads"))
        self.format_var = tk.StringVar(value="video")
        self.use_chrome_cookies_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        header_frame = ttk.Frame(self.root, padding=15)
        header_frame.pack(fill=tk.X)
        ttk.Label(
            header_frame, 
            text="YouTube & Instagram Downloader", 
            font=("Helvetica", 16, "bold")
        ).pack(anchor=tk.W)

        form_frame = ttk.Frame(self.root, padding=15)
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Video / Reel URL:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(0, 2))
        url_entry = ttk.Entry(form_frame, textvariable=self.url_var, width=70)
        url_entry.pack(fill=tk.X, pady=(0, 15))
        url_entry.focus()

        ttk.Label(form_frame, text="Save Folder:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(0, 2))
        path_frame = ttk.Frame(form_frame)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Entry(path_frame, textvariable=self.output_dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(path_frame, text="Browse...", command=self._browse_folder).pack(side=tk.RIGHT)

        ttk.Label(form_frame, text="Download Format:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        opts_frame = ttk.Frame(form_frame)
        opts_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Radiobutton(opts_frame, text="Video (MP4)", variable=self.format_var, value="video").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(opts_frame, text="Audio Only (MP3)", variable=self.format_var, value="audio").pack(side=tk.LEFT)

        auth_frame = ttk.LabelFrame(form_frame, text=" Authentication ", padding=10)
        auth_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Checkbutton(
            auth_frame, 
            text="Use Chrome Cookies (Required for Instagram / Works while Chrome is open)", 
            variable=self.use_chrome_cookies_var
        ).pack(anchor=tk.W)

        self.download_btn = ttk.Button(form_frame, text="Download Media", command=self._start_download_thread)
        self.download_btn.pack(fill=tk.X, ipady=5)

        self.status_label = ttk.Label(self.root, text="Ready", font=("Helvetica", 9, "italic"), padding=10)
        self.status_label.pack(anchor=tk.W)

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if folder:
            self.output_dir_var.set(folder)

    def _update_status(self, text):
        self.status_label.config(text=text)

    def _start_download_thread(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a valid URL.")
            return

        self.download_btn.config(state=tk.DISABLED)
        self._update_status("Starting download... Please wait.")

        threading.Thread(target=self._run_download, args=(url,), daemon=True).start()

    def _run_download(self, url):
        output_path = self.output_dir_var.get()
        is_audio = self.format_var.get() == "audio"
        use_cookies = self.use_chrome_cookies_var.get()

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        if is_audio:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            ydl_opts['merge_output_format'] = 'mp4'

        temp_dir = None

        if use_cookies:
            flatpak_chrome = os.path.expanduser('~/.var/app/com.google.Chrome')
            if os.path.exists(flatpak_chrome):
                temp_dir = tempfile.mkdtemp()
                copied_chrome_path = os.path.join(temp_dir, 'com.google.Chrome')
                shutil.copytree(flatpak_chrome, copied_chrome_path, dirs_exist_ok=True)
                ydl_opts['cookiesfrombrowser'] = (f'chrome:{copied_chrome_path}/',)
            else:
                ydl_opts['cookiesfrombrowser'] = ('chrome',)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Download Complete!\nSaved to: {output_path}"))
            self.root.after(0, lambda: self._update_status("Download finished successfully."))
            self.root.after(0, lambda: self.url_var.set(""))

        except Exception as e:
            err_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Download Error", f"Failed to download:\n{err_msg}"))
            self.root.after(0, lambda: self._update_status("Download failed."))

        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))


if __name__ == "__main__":
    root = tk.Tk()
    app = YTDownloaderApp(root)
    root.mainloop()
