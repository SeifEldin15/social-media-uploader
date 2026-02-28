"""
SHADOW POSTER - TIKTOK MODULE
This script handles the physical interaction with TikTok.com.
TikTok's anti-bot is aggressive, so we rely heavily on the Human behavior engine.
"""

import time
import os
from playwright.sync_api import Page

class TikTokPoster:
    def __init__(self, page: Page, human):
        self.page = page
        self.human = human

    def create_post(self, text: str, media_path: str = None) -> bool:
        if not media_path:
            print("❌ TikTok requires a video to post!")
            return False
            
        if not media_path.lower().endswith('.mp4'):
            print("❌ TikTok highly recommends .mp4 files. Proceeding anyway, but it might fail.")

        try:
            # ==========================================
            # 🏃‍♂️ PHASE 1: THE WARM UP
            # ==========================================
            print("🏠 Navigating to TikTok for warm-up...")
            self.page.goto("https://www.tiktok.com/", wait_until="domcontentloaded")
            
            # Big pause here needed because TikTok loves to show captchas or login modals 
            # if we jump too fast to the upload center.
            self.human.sleep(4, 7) 
            self.human.scroll_feed(duration_seconds=10)

            # ==========================================
            # ✍️ PHASE 2: OPENING THE UPLOAD CENTER
            # ==========================================
            print("🎥 Opening TikTok Upload Center...")
            # 'networkidle' fails on TikTok because they constantly stream analytics.
            # Using 'domcontentloaded' prevents the 30000ms timeout error.
            self.page.goto("https://www.tiktok.com/creator-center/upload", wait_until="domcontentloaded", timeout=60000)
            self.human.sleep(5, 8)

            # Switch to iframe if necessary (TikTok's upload center is heavily dynamic)
            # Sometimes it is an iframe, sometimes it is direct DOM. We check DOM first.
            
            # ==========================================
            # 📎 PHASE 3: HANDLING MEDIA
            # ==========================================
            print(f"📎 Attaching media: {media_path}")
            
            # Wait for either the iframe or the file input
            file_uploaded = False
            try:
                # Direct DOM method (newer TikTok layout)
                self.page.locator('input[type="file"]').first.set_input_files(media_path, timeout=8000)
                file_uploaded = True
            except:
                print("⚠️ Direct DOM failed. Searching specific iframes...")
                try:
                    frame_locator = self.page.frame_locator('iframe[data-tt="Upload_index_iframe"]')
                    frame_locator.locator('input[type="file"]').first.set_input_files(media_path, timeout=8000)
                    file_uploaded = True
                except:
                    pass
                
                if not file_uploaded:
                    print("⚠️ Searching all frames for input... TikTok may have disguised the iframe.")
                    for f in self.page.frames:
                        try:
                            if f.locator('input[type="file"]').count() > 0:
                                f.locator('input[type="file"]').first.set_input_files(media_path, timeout=5000)
                                file_uploaded = True
                                break
                        except:
                            pass

            if not file_uploaded:
                raise Exception("Could not locate the file upload input anywhere. Page structure changed or captcha present.")

            print("⏳ Uploading video to TikTok's servers... this takes a while.")
            # Videos take time to process on their end.
            self.human.sleep(15, 25) 
            
            # ==========================================
            # 🗣️ PHASE 4: TYPING THE CAPTION
            # ==========================================
            print("✍️ Typing caption...")
            
            caption_entered = False
            caption_selector = '.public-DraftEditor-content, div[contenteditable="true"]'
            
            try:
                # Direct DOM
                self.page.locator(caption_selector).first.click(timeout=8000)
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Backspace")
                self.human.sleep(1, 2)
                self.human.human_type(caption_selector, text)
                caption_entered = True
            except:
                print("⚠️ Direct DOM caption failed. Searching iframes...")
                try:
                    frame_locator = self.page.frame_locator('iframe[data-tt="Upload_index_iframe"]')
                    frame_locator.locator(caption_selector).first.click(timeout=8000)
                    self.page.keyboard.press("Control+A")
                    self.page.keyboard.press("Backspace")
                    self.human.sleep(1, 2)
                    for char in text:
                        self.page.keyboard.type(char)
                        import random
                        time.sleep(random.uniform(0.05, 0.15))
                    caption_entered = True
                except:
                    pass
                    
                if not caption_entered:
                    for f in self.page.frames:
                        try:
                            if f.locator(caption_selector).count() > 0:
                                f.locator(caption_selector).first.click(timeout=5000)
                                self.page.keyboard.press("Control+A")
                                self.page.keyboard.press("Backspace")
                                self.human.sleep(1, 2)
                                for char in text:
                                    self.page.keyboard.type(char)
                                    import random
                                    time.sleep(random.uniform(0.05, 0.15))
                                caption_entered = True
                                break
                        except:
                            pass

            self.human.sleep(2, 4)
            
            # ==========================================
            # 🚀 PHASE 5: THE STEALTH POST METHOD
            # ==========================================
            print("🚀 Clicking Post...")
            
            post_clicked = False
            post_selector = 'button:has-text("Post"):not([disabled])'
            
            try:
                 # Direct DOM posting
                 self.page.locator(post_selector).first.click(timeout=5000)
                 post_clicked = True
            except:
                try:
                    # iFrame posting
                    frame_locator = self.page.frame_locator('iframe[data-tt="Upload_index_iframe"]')
                    frame_locator.locator(post_selector).first.click(timeout=5000)
                    post_clicked = True
                except:
                    pass
                    
                if not post_clicked:
                    for f in self.page.frames:
                        try:
                            if f.locator(post_selector).count() > 0:
                                f.locator(post_selector).first.click(timeout=5000)
                                post_clicked = True
                                break
                        except:
                            pass
            
            # ==========================================
            # 🕵️‍♂️ PHASE 6: VERIFICATION
            # ==========================================
            print("⏳ Waiting for success confirmation...")
            try:
                # TikTok usually shows a toast notification or redirects to a success screen
                self.page.wait_for_selector("text=Manage your posts", timeout=60000)
                print("✅ Success confirmation detected!")
            except:
                print("⚠️ Could not detect explicit success text. Taking screenshot.")
                if not os.path.exists("logs"):
                     os.makedirs("logs")
                self.page.screenshot(path="logs/possible_tiktok_post_issue.png")

            # ==========================================
            # 🧊 PHASE 7: THE COOL DOWN
            # ==========================================
            print("🧊 Cooling down session...")
            self.human.sleep(3, 5)

            return True

        except Exception as e:
            print(f"❌ Failed to post on TikTok: {e}")
            if not os.path.exists("logs"):
                 os.makedirs("logs")
            try:
                self.page.screenshot(path="logs/failed_tiktok_post.png")
            except:
                pass
            return False
