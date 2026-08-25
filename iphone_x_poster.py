"""
SHADOW POSTER - iPHONE X (TWITTER) MODULE
Controls the native X iOS app via Appium/XCUITest.
Posting through the native iOS X app is extremely stealthy
because the session fingerprint is identical to a real phone user.

Bundle ID: com.atebits.Tweetie2
"""

import time
import os
import random
from appium.webdriver.common.appiumby import AppiumBy
from iphone_human import IPhoneHuman


class IPhoneXPoster:
    def __init__(self, driver, human: IPhoneHuman):
        self.driver = driver
        self.human = human

    def create_post(self, text: str, has_media: bool = False) -> bool:
        """
        Posts a tweet/post to X using the native iOS app.

        Args:
            text: The text content to post.
            has_media: If True, media was pre-transferred to the photo
                library and will be attached from there.
        """
        try:
            # ==========================================
            # 🏃 PHASE 1: WARM UP
            # ==========================================
            print("🏠 Opening X app and warming up...")
            self.human.sleep(3, 5)
            self._dismiss_popups()

            # Scroll the timeline briefly
            self.human.scroll_feed(duration_seconds=10)

            # ==========================================
            # ✍️ PHASE 2: OPEN THE COMPOSER
            # ==========================================
            print("✏️ Opening the post composer...")

            # The compose button is typically a quill/pencil icon or a "+"
            compose_btn = self.human.find_by_accessibility("New Post", timeout=8)
            if not compose_btn:
                compose_btn = self.human.find_by_accessibility("Compose", timeout=5)
            if not compose_btn:
                compose_btn = self.human.find_by_text("Post", partial=False, timeout=5)
            if not compose_btn:
                raise Exception("Could not find the compose / new post button in X.")

            self.human.tap_element(compose_btn)
            self.human.sleep(2, 4)
            self._dismiss_popups()

            # ==========================================
            # 🗣️ PHASE 3: TYPE THE POST TEXT
            # ==========================================
            print("✍️ Typing post text...")

            # X's text input field is usually labeled "What's happening?" 
            text_field = self.human.find_by_text("What's happening?", partial=True, timeout=8)
            if not text_field:
                text_field = self.human.find_element_safe(
                    AppiumBy.CLASS_NAME, "XCUIElementTypeTextView", timeout=5
                )
            if not text_field:
                raise Exception("Could not find the X post text field.")

            self.human.human_type(text_field, text)
            self.human.sleep(1, 3)

            # ==========================================
            # 📎 PHASE 4: ATTACH MEDIA (IF ANY)
            # ==========================================
            if has_media:
                print("🖼️ Attaching media from photo library...")

                # Tap the photo/image icon in the toolbar
                photo_icon = self.human.find_by_accessibility("Photo", timeout=8)
                if not photo_icon:
                    photo_icon = self.human.find_by_accessibility("Image", timeout=5)
                if photo_icon:
                    self.human.tap_element(photo_icon)
                    self.human.sleep(1, 3)
                    self._dismiss_popups()  # Photo library access permission

                    # Select the most recent item
                    first_media = self.human.find_element_safe(
                        AppiumBy.CLASS_NAME, "XCUIElementTypeImage", timeout=10
                    )
                    if first_media:
                        self.human.tap_element(first_media)
                        self.human.sleep(1, 3)
                    
                    # Dismiss keyboard if it re-appeared
                    try:
                        self.driver.hide_keyboard()
                    except Exception:
                        pass
                else:
                    print("⚠️ Could not find photo attachment button. Posting without media.")

            # Dismiss keyboard before posting
            try:
                self.driver.hide_keyboard()
            except Exception:
                pass
            self.human.sleep(0.5, 1.5)

            # ==========================================
            # 🚀 PHASE 5: POST
            # ==========================================
            print("🚀 Tapping Post...")

            # The "Post" submit button is in the top-right of the composer
            post_btn = self.human.find_by_accessibility("Post", timeout=8)
            if not post_btn:
                post_btn = self.human.find_by_text("Post", timeout=5)
            if not post_btn:
                raise Exception("Could not find the 'Post' submit button in X.")

            self.human.tap_element(post_btn)

            # ==========================================
            # 🕵️ PHASE 6: VERIFY SUCCESS
            # ==========================================
            print("⏳ Waiting for X to confirm the post...")
            success = False
            deadline = time.time() + 60

            while time.time() < deadline:
                # X shows a "Your post was sent." toast notification
                sent_indicators = [
                    "Your post was sent.",
                    "Tweet sent",
                    "Your post was sent",
                ]
                for indicator in sent_indicators:
                    el = self.human.find_by_text(indicator, partial=True, timeout=2)
                    if el:
                        print(f"✅ Confirmation found: '{indicator}'")
                        success = True
                        break

                if success:
                    break

                # If the composer has closed (no longer seeing text field), that means success
                text_still_there = self.human.find_by_text("What's happening?", partial=True, timeout=2)
                if not text_still_there:
                    # Double-check we are not on a different screen unrelated to posting
                    post_btn_still_there = self.human.find_by_accessibility("Post", timeout=2)
                    if not post_btn_still_there:
                        print("✅ Composer closed. Assuming post was sent.")
                        success = True
                        break

                time.sleep(2)

            if not success:
                self._take_screenshot("logs/failed_iphone_x_post.png")
                raise Exception("Timed out waiting for X to confirm the post.")

            # ==========================================
            # 🧊 PHASE 7: COOL DOWN
            # ==========================================
            print("🧊 Cooling down on the timeline...")
            self.human.sleep(3, 5)
            self.human.scroll_feed(duration_seconds=12)

            return True

        except Exception as e:
            print(f"❌ iPhone X post failed: {e}")
            self._take_screenshot("logs/failed_iphone_x_post.png")
            return False

    def _dismiss_popups(self):
        """Dismisses iOS system prompts and X onboarding dialogs."""
        popup_labels = [
            "Allow",
            "OK",
            "Not Now",
            "Continue",
            "Close",
            "Allow Access to All Photos",
        ]
        for label in popup_labels:
            btn = self.human.find_by_text(label, timeout=2)
            if btn:
                print(f"   Dismissing popup: '{label}'")
                self.human.tap_element(btn)
                self.human.sleep(0.5, 1.2)

    def _take_screenshot(self, path: str):
        """Save a debug screenshot."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.driver.save_screenshot(path)
            print(f"📸 Screenshot saved to {path}")
        except Exception as e:
            print(f"   (Could not save screenshot: {e})")
