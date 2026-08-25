"""
SHADOW POSTER - UI
Graphical interface for launching the poster and configuring accounts.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
import time

# Add custom path to access login script
sys.path.append(os.path.join(os.path.dirname(__file__), "Login scripts"))
from login_helper import save_session
import main
import iphone_main

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
        self.root.geometry("900x520")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main Frame setup
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---------------------
        # TOP CONTROLS
        # ---------------------
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(top_frame, text="Shadow Poster", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        
        user_frame = ttk.Frame(top_frame)
        user_frame.pack(side=tk.RIGHT)
        ttk.Label(user_frame, text="Active User: ").pack(side=tk.LEFT)
        self.username_var = tk.StringVar(value="default")
        self.username_entry = ttk.Entry(user_frame, textvariable=self.username_var, width=15)
        self.username_entry.pack(side=tk.LEFT)

        # iPhone UDID row (below the title bar)
        udid_frame = ttk.Frame(main_frame)
        udid_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(udid_frame, text="iPhone UDID:").pack(side=tk.LEFT, padx=(0, 4))
        self.udid_var = tk.StringVar(value="")
        self.udid_entry = ttk.Entry(udid_frame, textvariable=self.udid_var, width=40)
        self.udid_entry.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(udid_frame, text="🔍 Auto-Detect", command=self.run_detect_iphone).pack(side=tk.LEFT)
        
        # Grid layout for buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))

        # Auto Posting Options (Desktop/Browser)
        ttk.Label(btn_frame, text="🖥️ Desktop Browser:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10)
        ttk.Button(btn_frame, text="🚀 Next in Queue", command=lambda: self.run_poster(None)).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="📸 Next IG Post", command=lambda: self.run_poster('ig')).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="🐦 Next X Post", command=lambda: self.run_poster('x')).grid(row=3, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="🎵 Next TikTok Post", command=lambda: self.run_poster('tiktok')).grid(row=4, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="🌟 Post All Pending", command=self.run_post_all).grid(row=5, column=0, padx=10, pady=5)

        # Spacer 1
        ttk.Frame(btn_frame, width=20).grid(row=0, column=1)

        # iPhone Posting Options (Native iOS Apps via Appium)
        ttk.Label(btn_frame, text="📱 iPhone (Native Apps):", font=("Helvetica", 10, "bold")).grid(row=0, column=2, sticky="w", padx=10)
        ttk.Button(btn_frame, text="📸 iPhone IG Post",     command=lambda: self.run_iphone_poster('ig')).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="🐦 iPhone X Post",      command=lambda: self.run_iphone_poster('x')).grid(row=2, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="🎵 iPhone TikTok Post", command=lambda: self.run_iphone_poster('tiktok')).grid(row=3, column=2, padx=10, pady=5)

        # Spacer 2
        ttk.Frame(btn_frame, width=20).grid(row=0, column=3)

        # Configuration Options
        ttk.Label(btn_frame, text="⚙️ Configure Accounts:", font=("Helvetica", 10, "bold")).grid(row=0, column=4, sticky="w", padx=10)
        ttk.Button(btn_frame, text="Log into X (Twitter)", command=lambda: self.run_login('1')).grid(row=1, column=4, padx=10, pady=5)
        ttk.Button(btn_frame, text="Log into Instagram",   command=lambda: self.run_login('2')).grid(row=2, column=4, padx=10, pady=5)
        ttk.Button(btn_frame, text="Log into TikTok",      command=lambda: self.run_login('3')).grid(row=3, column=4, padx=10, pady=5)

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
        username = self.username_var.get().strip()
        if not username:
            print("❌ Error: Please enter a username first.")
            return
        plat_msg = "Next in Queue" if not target_platform else target_platform.upper()
        print(f"\n--- Starting Auto-Poster [{plat_msg}] for User [{username}] ---")
        # Run in thread so UI doesn't freeze
        threading.Thread(target=self._run_poster_thread, args=(target_platform, username), daemon=True).start()
        
    def _run_poster_thread(self, target_platform, username):
        try:
            main.main(target_platform, username)
            print("--- Bot finished ---")
        except Exception as e:
            print(f"❌ Critical Error: {e}")

    def run_iphone_poster(self, target_platform: str):
        """Launch the iPhone native-app poster in a background thread."""
        username = self.username_var.get().strip()
        udid = self.udid_var.get().strip() or None
        if not username:
            print("❌ Error: Please enter a username first.")
            return
        print(f"\n--- Starting iPhone Auto-Poster [{target_platform.upper()}] for User [{username}] ---")
        if not udid:
            print("   (No UDID entered — will attempt auto-detection)")
        threading.Thread(
            target=self._run_iphone_poster_thread,
            args=(target_platform, username, udid),
            daemon=True
        ).start()

    def _run_iphone_poster_thread(self, target_platform, username, udid):
        try:
            iphone_main.main(target_platform, username, udid=udid)
            print("--- iPhone Bot finished ---")
        except Exception as e:
            print(f"❌ iPhone Critical Error: {e}")

    def run_detect_iphone(self):
        """Auto-detect connected iPhone and populate the UDID field."""
        print("\n--- Detecting connected iPhone... ---")
        threading.Thread(target=self._run_detect_iphone_thread, daemon=True).start()

    def _run_detect_iphone_thread(self):
        try:
            udid = iphone_main.detect_iphone_udid()
            if udid:
                self.udid_var.set(udid)
                print(f"✅ iPhone UDID populated: {udid}")
            else:
                print("❌ No iPhone found. Check USB connection and 'Trust This Computer'.")
        except Exception as e:
            print(f"❌ Detection Error: {e}")

    def run_post_all(self):
        username = self.username_var.get().strip()
        if not username:
            print("❌ Error: Please enter a username first.")
            return
        print(f"\n--- Starting Auto-Poster [ALL PENDING] for User [{username}] ---")
        threading.Thread(target=self._run_post_all_thread, args=(username,), daemon=True).start()

    def _run_post_all_thread(self, username):
        try:
            from content_manager import ContentManager
            cm = ContentManager()
            while True:
                job = cm.get_next_post(None, username)
                if not job:
                    print(f"✅ Completed processing all pending posts for {username}!")
                    break
                
                print(f"\n>>> Processing Batch Post: ID {job['id']} for {job['platform'].upper()} (User: {username})...")
                main.main(None, username)
                time.sleep(3) # Small delay to give resources a break before opening the next browser
                
            print("--- Bot batch finish ---")
        except Exception as e:
            print(f"❌ Critical Error: {e}")

    def run_login(self, choice):
        username = self.username_var.get().strip()
        if not username:
            print("❌ Error: Please enter a username first.")
            return
        if choice == '1': platform = "X (Twitter)"
        elif choice == '2': platform = "Instagram"
        elif choice == '3': platform = "TikTok"
        else: platform = "Unknown"
        
        print(f"\n--- Initiating Configuration for {platform} (User: {username}) ---")
        threading.Thread(target=self._run_login_thread, args=(choice, username), daemon=True).start()

    def _run_login_thread(self, choice, username):
        try:
            save_session(choice=choice, is_ui=True, username=username)
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
