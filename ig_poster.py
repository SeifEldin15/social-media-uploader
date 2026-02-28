"""
SHADOW POSTER - INSTAGRAM MODULE
This script handles the physical interaction with Instagram.com.
It actively mimics erratic human behavior to avoid detection.
"""

import time
from playwright.sync_api import Page

class IGPoster:
    def __init__(self, page: Page, human):
        self.page = page
        self.human = human

    def create_post(self, text: str, media_path: str = None) -> bool:
        if not media_path:
            print("❌ Instagram requires media (image or video) to post!")
            return False

        try:
            # ==========================================
            # 🏃‍♂️ PHASE 1: THE WARM UP
            # ==========================================
            print("🏠 Navigating to Instagram feed for warm-up...")
            self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            
            # Give React a second to render the actual feed
            self.human.sleep(2, 4) 
            self.human.scroll_feed(duration_seconds=5) # Reduced from 30 seconds so it doesn't look stuck

            # ==========================================
            # ✍️ PHASE 2: OPENING THE COMPOSER (MODAL)
            # ==========================================
            # Click the Create button on the sidebar.
            creation_clicked = False
            
            # Strategy 1: The standard Create text on the sidebar
            try:
                self.page.locator("span", has_text="Create").first.click(timeout=3000)
                creation_clicked = True
            except:
                pass
                
            # Strategy 2: The New Post SVG icon
            if not creation_clicked:
                try:
                    self.page.locator("svg[aria-label='New post']").first.click(timeout=3000)
                    creation_clicked = True
                except:
                    pass

            # Strategy 3: Just look for any matching element
            if not creation_clicked:
                self.page.click("text=Create", timeout=3000)
                
            self.human.sleep(2, 4)
            
            # Instagram sometimes shows a 'Post' / 'Live' sub-menu, if it does, click 'Post'
            try:
                self.page.locator("span", has_text="Post").first.click(timeout=3000)
                self.human.sleep(1, 3)
            except:
                pass # The sub-menu didn't appear, that's fine.

            # ==========================================
            # 📎 PHASE 3: HANDLING MEDIA
            # ==========================================
            print(f"📎 Attaching media: {media_path}")
            # Find the hidden file input. It accepts images and videos.
            file_input = self.page.locator('input[type="file"]')
            file_input.set_input_files(media_path)
            
            # Wait for the media to visually render in the crop modal 
            self.human.sleep(3, 5) 
            
            # ==========================================
            # ➡️ PHASE 4: NAVIGATING THE MODAL STEPS
            # ==========================================
            print("➡️ Clicking Next (Crop Step)...")
            self.page.click("text=Next")
            self.human.sleep(2, 3)

            print("➡️ Clicking Next (Filters Step)...")
            self.page.click("text=Next")
            self.human.sleep(2, 3)

            # ==========================================
            # 🗣️ PHASE 5: TYPING THE CAPTION
            # ==========================================
            print("✍️ Typing caption...")
            # Instagram's caption box is a div acting as a textbox
            caption_box = self.page.locator('div[aria-label="Write a caption..."]')
            
            # Click it first to focus
            self.human.sleep(1, 2)
            try:
                caption_box.click(timeout=3000)
            except:
                self.page.mouse.click(0,0) # fall back

            self.human.sleep(1, 2)
            
            self.human.human_type('div[aria-label="Write a caption..."]', text)
            self.human.sleep(2, 4)
            
            # ==========================================
            # 🚀 PHASE 6: THE STEALTH POST METHOD
            # ==========================================
            print("🚀 Clicking Share...")
            self.page.click("text=Share")
            
            # ==========================================
            # 🕵️‍♂️ PHASE 7: VERIFICATION
            # ==========================================
            print("⏳ Waiting for upload to complete (Videos can take a while)...")
            try:
                # Wait for the text confirmation "Your post has been shared."
                self.page.wait_for_selector("text=Your post has been shared.", timeout=120000)
                print("✅ Success confirmation detected!")
            except:
                print("⚠️ Could not detect success text, checking for modal closure...")
                # It might have succeeded but we missed the success text, or it failed.
                # Just take a screenshot to be safe.
                self.page.screenshot(path="logs/possible_ig_post_issue.png")
                # Alternatively, check if the "Share" button is still there. If it is, it failed.
                if self.page.locator("text=Share").is_visible():
                     raise Exception("Share button is still visible! The post likely failed.")
                else:
                     print("✅ Share button gone. Assuming success.")

            # Close the success modal (There's usually an X button)
            try:
                self.page.click("svg[aria-label='Close']", timeout=3000)
            except:
                pass

            # ==========================================
            # 🧊 PHASE 8: THE COOL DOWN
            # ==========================================
            print("🧊 Cooling down session...")
            self.human.sleep(2, 4)
            self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            self.human.scroll_feed(duration_seconds=20)

            return True

        except Exception as e:
            print(f"❌ Failed to post on Instagram: {e}")
            import os
            if not os.path.exists("logs"):
                 os.makedirs("logs")
            try:
                self.page.screenshot(path="logs/failed_ig_post.png")
            except:
                pass
            return False
