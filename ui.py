"""
SHADOW POSTER - UI
Graphical interface for launching the poster and configuring accounts.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os

# Add custom path to access login script
sys.path.append(os.path.join(os.path.dirname(__file__), "Login scripts"))
from login_helper import save_session
import main

class PrintRedirector:
    """Redirects print statements to the Tkinter text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)
        # We also print to regular terminal just in case
        try:
            self.original_stdout.write(text)
        except Exception:
            pass

    def flush(self):
        try:
            self.original_stdout.flush()
        except:
            pass


class ShadowPosterUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shadow Poster Control Panel")
        self.root.geometry("600x450")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main Frame setup
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---------------------
        # TOP CONTROLS
        # ---------------------
        ttk.Label(main_frame, text="Shadow Poster", font=("Helvetica", 16, "bold")).pack(pady=(0, 15))
        
        # Grid layout for buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))

        # Auto Posting Options
        ttk.Label(btn_frame, text="Run Auto-Poster:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10)
        ttk.Button(btn_frame, text="🚀 Next in Queue", command=lambda: self.run_poster(None)).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="📸 Next IG Post", command=lambda: self.run_poster('ig')).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="🐦 Next X Post", command=lambda: self.run_poster('x')).grid(row=3, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="🎵 Next TikTok Post", command=lambda: self.run_poster('tiktok')).grid(row=4, column=0, padx=10, pady=5)
        
        # Spacer
        ttk.Frame(btn_frame, width=30).grid(row=0, column=1)

        # Configuration Options
        ttk.Label(btn_frame, text="Configure Accounts:", font=("Helvetica", 10, "bold")).grid(row=0, column=2, sticky="w", padx=10)
        ttk.Button(btn_frame, text="Log into X (Twitter)", command=lambda: self.run_login('1')).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="Log into Instagram", command=lambda: self.run_login('2')).grid(row=2, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="Log into TikTok", command=lambda: self.run_login('3')).grid(row=3, column=2, padx=10, pady=5)

        # ---------------------
        # CONSOLE OUTPUT
        # ---------------------
        ttk.Label(main_frame, text="System Logs:").pack(anchor="w")
        self.console = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.console.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Redirect standard output
        sys.stdout = PrintRedirector(self.console)
        sys.stderr = sys.stdout # Redirect errors here too

        print("System Initialized. Ready for commands.")

    def run_poster(self, target_platform=None):
        plat_msg = "Next in Queue" if not target_platform else target_platform.upper()
        print(f"\n--- Starting Auto-Poster [{plat_msg}] ---")
        # Run in thread so UI doesn't freeze
        threading.Thread(target=self._run_poster_thread, args=(target_platform,), daemon=True).start()
        
    def _run_poster_thread(self, target_platform):
        try:
            main.main(target_platform)
            print("--- Bot finished ---")
        except Exception as e:
            print(f"❌ Critical Error: {e}")

    def run_login(self, choice):
        if choice == '1': platform = "X (Twitter)"
        elif choice == '2': platform = "Instagram"
        elif choice == '3': platform = "TikTok"
        else: platform = "Unknown"
        
        print(f"\n--- Initiating Configuration for {platform} ---")
        threading.Thread(target=self._run_login_thread, args=(choice,), daemon=True).start()

    def _run_login_thread(self, choice):
        try:
            save_session(choice=choice, is_ui=True)
            print("--- Configuration saved successfully! ---")
        except Exception as e:
            print(f"❌ Configuration Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShadowPosterUI(root)
    
    # Reset sys.stdout on exit to prevent errors
    def on_closing():
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
