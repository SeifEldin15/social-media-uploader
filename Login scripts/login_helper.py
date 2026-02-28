import os
from playwright.sync_api import sync_playwright

# ==========================================
# THE FAKE ID
# ==========================================
# By default, Playwright tells the website it is "HeadlessChrome".
# This string forces the browser to announce itself as a completely standard, 
# boring Windows 10 desktop user running regular Google Chrome.
REAL_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

def get_stealth_args():
    """
    These flags rip out the tracking metrics that X.com uses to detect bots.
    """
    return [
        # THE MOST IMPORTANT LINE: Hides the `navigator.webdriver` property in JS.
        # Without this, X.com instantly knows you are a robot.
        "--disable-blink-features=AutomationControlled", 
        
        # Stops the browser from showing the "Chrome is being controlled by automated software" banner.
        "--disable-infobars",
        
        # Forces the window to open full screen, which looks more human.
        "--start-maximized",
        
        # Bypasses the OS shared memory space (prevents crashes on lower-end servers/machines).
        "--disable-dev-shm-usage",
        
        # Disables the Chrome sandbox. Necessary for some OS environments when running automated.
        "--no-sandbox",
        "--disable-setuid-sandbox",
        
        # Relaxes strict web security policies that sometimes block automated cross-origin requests.
        "--disable-web-security",
        
        # Speeds up DNS resolution by prioritizing IPv4.
        "--dns-result-order=ipv4first",
        
        # Disables site isolation. Saves RAM and stops Chrome from launching too many background processes.
        "--disable-features=IsolateOrigins,site-per-process"
    ]

def save_session(choice=None, is_ui=False):
    # ==========================================
    # PLATFORM SELECTION
    # ==========================================
    if choice is None:
        print("Which platform do you want to log into?")
        print("1: X (Twitter)")
        print("2: Instagram")
        choice = input("Enter 1 or 2: ").strip()

    if choice == '1':
        platform_name = "X"
        profile_folder = "X_Profile"
        login_url = "https://x.com/login"
    elif choice == '2':
        platform_name = "Instagram"
        profile_folder = "IG_Profile"
        login_url = "https://www.instagram.com/accounts/login/"
    else:
        print("Invalid choice. Exiting.")
        return

    # ==========================================
    # DIRECTORY SETUP
    # ==========================================
    # Build the profile folder right where this script is executed from
    # (assuming it's run from the root directory)
    session_dir = os.path.join(os.getcwd(), profile_folder)

    # If the folder doesn't exist yet, build it. This is where the SQLite databases, 
    # cookies, and local storage will be permanently saved.
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)

    print(f"Opening Secure Browser for Session Storage...")
    print(f"Saving cookies/data to: {session_dir}")

    # ==========================================
    # BROWSER LAUNCH (THE STEALTH WAY)
    # ==========================================
    with sync_playwright() as p:
        
        # launch_persistent_context is the magic bullet. It acts like a normal browser profile 
        # (like your personal Chrome profile) rather than a temporary, amnesiac bot session.
        browser = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            
            # headless=False means we actually draw the browser UI on your screen so you can type.
            headless=False,
            
            # Forces Playwright to use the real Google Chrome installed on your PC, not its bundled Chromium.
            channel="chrome", 
            
            # Injecting our Fake ID from the top of the script.
            user_agent=REAL_USER_AGENT,                           
            
            # Overriding Playwright's default behavior that adds the `--enable-automation` flag.
            ignore_default_args=["--enable-automation"],          
            
            # Injecting our Invisibility Cloak list of arguments.
            args=get_stealth_args()                               
        )
        
        # Grab the first tab that opens automatically.
        page = browser.pages[0]
        
        # ==========================================
        # NAVIGATION & MANUAL OVERRIDE
        # ==========================================
        # Go directly to the platform login page. We set a long timeout (60s) just in case your internet lags.
        try:
            page.goto(login_url, timeout=60000)
        except Exception as e:
            print(f"[!] Network timeout: {e}. Browser is still open though.")

        print("\n" + "="*50)
        print(f" ACTION REQUIRED FOR {platform_name.upper()} ")
        print("1. Enter your Username & Password.")
        print("2. Solve any Captchas/2FA.")
        print("3. Check 'Remember Me'.")
        print(f"4. Wait until you see your {platform_name} Home Feed.")
        print("="*50 + "\n")

        # This halts the Python script dead in its tracks.
        if is_ui:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showinfo(
                "Action Required",
                f"Please log into {platform_name} in the newly opened browser.\n\n"
                f"Press OK *AFTER* you see your home feed.",
                parent=root
            )
            root.destroy()
        else:
            input("PRESS ENTER HERE ONCE YOU ARE FULLY LOGGED IN >> ")

        # ==========================================
        # 💾 TEARDOWN & SAVE
        # ==========================================
        # By gracefully closing the browser, Playwright ensures all the cookies are flushed to the disk 
        # inside your x_session folder.
        print("Closing browser and saving session state...")
        browser.close()
        print(f"Session saved! You can now run your main bots using the '{session_dir}' folder.")

if __name__ == "__main__":
    save_session()