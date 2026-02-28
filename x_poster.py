"""
SHADOW POSTER - X MODULE
This script handles the actual physical interaction with X.com. 
It actively mimics erratic human behavior to avoid the ban hammer.
"""

import time
from playwright.sync_api import Page

class XPoster:
    def __init__(self, page: Page, human):
        self.page = page
        self.human = human

    def create_post(self, text: str, image_path: str = None) -> bool:
        try:
            # ==========================================
            # 🏃‍♂️ PHASE 1: THE WARM UP
            # ==========================================
            print("🏠 Navigating to Home feed for warm-up...")
            # FIX: Changed from networkidle to domcontentloaded
            self.page.goto("https://x.com/home", wait_until="domcontentloaded")
            
            # Give the Javascript a second to render the actual tweets
            self.human.sleep(2, 4) 
            self.human.scroll_feed(duration_seconds=40)

            # ==========================================
            # ✍️ PHASE 2: OPENING THE COMPOSER
            # ==========================================
            print("🐦 Opening composer...")
            # FIX: Changed from networkidle to domcontentloaded
            self.page.goto("https://x.com/compose/tweet", wait_until="domcontentloaded")
            self.human.sleep(2, 4)
            
            # ==========================================
            # 📎 PHASE 3: HANDLING MEDIA
            # ==========================================
            if image_path:
                print(f"📎 Attaching media...")
                self.page.wait_for_selector('input[data-testid="fileInput"]', state="attached")
                self.page.set_input_files('input[data-testid="fileInput"]', image_path)
                
                # Wait for the image to visually render in the composer box
                self.page.wait_for_selector('button[aria-label="Remove"]', timeout=15000)
                self.human.sleep(3, 5) 

            # ==========================================
            # 🗣️ PHASE 4: TYPING THE CAPTION
            # ==========================================
            self.page.wait_for_selector('div[data-testid="tweetTextarea_0"]')
            self.human.human_type('div[data-testid="tweetTextarea_0"]', text)
            self.human.sleep(1, 3)
            
            # ==========================================
            # 🚀 PHASE 5: THE STEALTH POST METHOD
            # ==========================================
            print("🚀 Sending via Ctrl+Enter...")
            self.page.keyboard.press("Control+Enter")
            
            # ==========================================
            # 🕵️‍♂️ PHASE 6: VERIFICATION
            # ==========================================
            try:
                self.page.wait_for_selector('div[data-testid="toast"]', timeout=10000)
                print("✅ Toast notification detected!")
            except:
                print("⚠️ No toast detected, checking if text box is empty...")
                box_text = self.page.locator('div[data-testid="tweetTextarea_0"]').text_content()
                if not box_text: 
                    print("✅ Text box is empty. Assuming success.")
                else:
                    raise Exception("Text still remains in box! The post likely failed.")

            # ==========================================
            # 🧊 PHASE 7: THE COOL DOWN
            # ==========================================
            print("🧊 Cooling down session...")
            # FIX: Changed from networkidle to domcontentloaded
            self.page.goto("https://x.com/home", wait_until="domcontentloaded")
            self.human.sleep(2, 4)
            self.human.scroll_feed(duration_seconds=40)

            return True

        except Exception as e:
            print(f"❌ Failed to post: {e}")
            self.page.screenshot(path="logs/failed_x_post.png")
            return False