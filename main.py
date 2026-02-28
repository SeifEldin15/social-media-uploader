"""
This is the master controller. It reads the content queue, loads the 
stealth browser profile, and executes the posting sequence.
"""

import os
import time

from playwright.sync_api import sync_playwright # imports modules from playwright modules
from playwright_stealth import stealth_sync
from core.x_poster import XPoster               # imports the XPoster function from the x_poster.py script
from core.human import Human                    # imports the Human function from the human.py script
from core.content_manager import ContentManager # imports the content manager from content_manager.py

# ==========================================
# GLOBAL CONFIGURATION
# ==========================================
# Point exactly to where our cookies are stored
PROFILE_PATH = os.path.join(os.getcwd(), "X_Profile")

# Tells X.com "I am a standard Windows PC running regular Chrome"
REAL_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

def get_stealth_args():
    """
    It removed the automation flags from the automated Chrome browser. 
    These launch arguments strip away the automation fingerprints that Playwright leaves behind.
    """
    return [
        "--disable-blink-features=AutomationControlled", # Hides navigator.webdriver (Crucial!)
        "--disable-infobars",                            # Hides the "Automated Test Software" banner
        "--start-maximized",                             # Humans don't browse in tiny 800x600 windows
        "--disable-dev-shm-usage",                       # Prevents memory crashes on heavy media uploads
        "--no-sandbox",                                  # Required for some OS environments
        "--disable-setuid-sandbox",
        "--disable-web-security",                        # Relaxes strict CORS policies 
        "--dns-result-order=ipv4first",                  # Speeds up network requests
        "--disable-features=IsolateOrigins,site-per-process" # Saves RAM by disabling site isolation
    ]

def main():
    print("🚀 Firing up the X engine (Stealth Mode)...")
    
    # ==========================================
    # PHASE 1: THE DATA FETCH
    # ==========================================
    # We do this FIRST. There is no reason to launch a heavy, RAM-hungry 
    # browser if we don't even have a post scheduled. 
    cm = ContentManager()
    job = cm.get_next_post("x")
    
    # The kill switch: If content.csv is empty or has no 'pending' rows, we exit instantly.
    if not job:
        print("🛑 Nothing to do because content.csv is empty or has no pending posts. Shutting down gracefully.")
        return

    # Just a nice UI touch to show what we're working on
    print(f"📋 Found Job #{job['id']}: '{job['caption'][:20]}...'")
    
    # ==========================================
    # PHASE 1.5: BULLETPROOF FILE PATHING
    # ==========================================
    # 1. Grab the raw string from the CSV (e.g., 'media/campaign_1.jpg')
    raw_image_string = job['image_path'].strip() if job.get('image_path') else None
    
    # We define a placeholder for the final, absolute path.
    absolute_image_path = None

    if raw_image_string:
        # 2. Convert to Absolute Path
        absolute_image_path = os.path.join(os.getcwd(), raw_image_string)
        
        # 3. The Pre-Flight Check
        # If the marketing image was accidentally deleted or misspelled in the CSV, abort.
        if not os.path.exists(absolute_image_path):
            print(f"❌ CRITICAL ERROR: Could not find the image file!")
            print(f"   I looked exactly here: {absolute_image_path}")
            print(f"   Check your media/ folder and content.csv spelling. Aborting.")
            return # Kills the script safely

    # ==========================================
    # PHASE 2: BROWSER IGNITION
    # ==========================================
    with sync_playwright() as p:
        
        # We launch the persistent context using the X_Profile folder we built with login_helper.py
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_PATH,
            headless=False,                                       # Set to True later if you want it entirely invisible
            channel="chrome",                                     # Use the real Google Chrome installation
            user_agent=REAL_USER_AGENT,                           # STEALTH 1: Apply the Fake ID
            ignore_default_args=["--enable-automation"],          # STEALTH 2: Remove Playwright's default snitch flag
            args=get_stealth_args()                               # STEALTH 3: Inject the Invisibility Cloak
        )
        
        # Grab the active tab
        page = context.pages[0]
        
        # STEALTH 4: Apply Javascript Stealth Patches
        stealth_sync(page)
        
        # ==========================================
        # PHASE 3: EXECUTION
        # ==========================================
        # Instantiate our random-behavior engine to make the mouse/keyboard look human
        brian_bot = Human(page)
        
        # Load up the X-specific logic and pass our human behavior engine into it
        poster = XPoster(page, brian_bot)
        
        # Fire the actual sequence! Note we are passing absolute_image_path here.
        success = poster.create_post(
            text=job['caption'], 
            image_path=absolute_image_path 
        )
        
        # ==========================================
        # PHASE 4: DATABASE UPDATE
        # ==========================================
        # Only mark the CSV as 'completed' if Playwright confirms the post actually went live.
        if success:
            print("✅ Successfully Posted.")
            cm.mark_post_as_complete(job['id'])
            
        # Shut down the browser to flush cookies and free up system memory
        context.close()

if __name__ == "__main__":
    main()