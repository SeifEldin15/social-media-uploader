"""
SHADOW POSTER - iPHONE INSTAGRAM MODULE
Controls the native Instagram iOS app via Appium/XCUITest.
This is significantly more stealth than the web version because
we are literally using the real app, indistinguishable from
a human tapping on their phone.

Bundle ID: com.burbn.instagram
"""

import time
import os
import random
from appium.webdriver.common.appiumby import AppiumBy
from iphone_human import IPhoneHuman


class IPhoneIGPoster:
    def __init__(self, driver, human: IPhoneHuman):
        self.driver = driver
        self.human = human

    def create_post(self, text: str, media_already_in_library: bool = True) -> bool:
        """
        Posts to Instagram using the native iOS app.

        Args:
            text: The caption to type.
            media_already_in_library: If True, the media has already been
                transferred to the iPhone's photo library by iphone_main.py.
                The bot will select the most recently added photo/video.
        """
        if not media_already_in_library:
            print("❌ iPhone IG Poster expects media to already be in the photo library.")
            return False

        try:
            # ==========================================
            # 🏃 PHASE 1: WARM UP
            # ==========================================
            print("🏠 Opening Instagram app and warming up...")

            # The app is already open (set by Appium capabilities).
            # Give it a moment to fully load.
            self.human.sleep(3, 5)

            # Dismiss any notification/permission prompts
            self._dismiss_popups()

            # Scroll the feed briefly so we look human
            self.human.scroll_feed(duration_seconds=12)

            # ==========================================
            # ✍️ PHASE 2: OPEN THE CREATOR
            # ==========================================
            print("➕ Opening the post creator...")

            # Tap the "+" (New Post) button in the bottom nav bar
            plus_btn = self.human.find_by_accessibility("New Post", timeout=10)
            if not plus_btn:
                # Fallback: some IG versions label it differently
                plus_btn = self.human.find_by_text("New post", partial=True, timeout=5)
            if not plus_btn:
                raise Exception("Could not find the '+' / New Post button in the IG nav bar.")

            self.human.tap_element(plus_btn)
            self.human.sleep(2, 4)

            # Dismiss any pop-up asking for photo library permissions
            self._dismiss_popups()

            # ==========================================
            # 📎 PHASE 3: SELECT MEDIA FROM LIBRARY
            # ==========================================
            print("🖼️ Selecting most recent photo/video from library...")

            # The IG media picker shows the most recent item at top-left.
            # We look for the first thumbnail cell in the picker grid.
            first_thumbnail = self.human.find_element_safe(
                AppiumBy.CLASS_NAME, "XCUIElementTypeImage", timeout=10
            )
            if first_thumbnail:
                self.human.tap_element(first_thumbnail)
            else:
                # Fallback: tap approximate top-left position of media grid
                size = self.driver.get_window_size()
                self.human.tap(int(size['width'] * 0.1), int(size['height'] * 0.45))

            self.human.sleep(1, 3)

            # ==========================================
            # ➡️ PHASE 4: NAVIGATE MODAL STEPS
            # ==========================================
            print("➡️ Tapping Next (Crop step)...")
            next_btn = self.human.find_by_accessibility("Next", timeout=8)
            if not next_btn:
                next_btn = self.human.find_by_text("Next", timeout=5)
            if not next_btn:
                raise Exception("Could not find 'Next' button after media selection.")
            self.human.tap_element(next_btn)
            self.human.sleep(2, 3)

            print("➡️ Tapping Next (Filter step)...")
            next_btn = self.human.find_by_accessibility("Next", timeout=8)
            if not next_btn:
                next_btn = self.human.find_by_text("Next", timeout=5)
            if next_btn:
                self.human.tap_element(next_btn)
            self.human.sleep(2, 3)

            # ==========================================
            # 🗣️ PHASE 5: TYPE CAPTION
            # ==========================================
            print("✍️ Typing the caption...")

            caption_field = self.human.find_by_accessibility("Write a caption...", timeout=8)
            if not caption_field:
                caption_field = self.human.find_by_text("Write a caption...", partial=True, timeout=5)
            if not caption_field:
                # Final fallback: find any text view / text field on the share screen
                caption_field = self.human.find_element_safe(
                    AppiumBy.CLASS_NAME, "XCUIElementTypeTextView", timeout=5
                )
            if not caption_field:
                raise Exception("Could not find the caption field on the share screen.")

            self.human.human_type(caption_field, text)
            self.human.sleep(1, 3)

            # Dismiss the keyboard
            try:
                self.driver.hide_keyboard()
            except Exception:
                pass

            # ==========================================
            # 🚀 PHASE 6: SHARE
            # ==========================================
            print("🚀 Tapping Share...")
            share_btn = self.human.find_by_accessibility("Share", timeout=8)
            if not share_btn:
                share_btn = self.human.find_by_text("Share", timeout=5)
            if not share_btn:
                raise Exception("Could not find the 'Share' button.")

            self.human.tap_element(share_btn)

            # ==========================================
            # 🕵️ PHASE 7: VERIFY SUCCESS
            # ==========================================
            print("⏳ Waiting for post to go live (videos take longer)...")
            success = False

            # IG shows a "Your post has been shared." confirmation or returns to the feed.
            # We wait up to 2 minutes for either signal.
            deadline = time.time() + 120
            while time.time() < deadline:
                # Check for the success text
                success_text = self.human.find_by_text("Your post has been shared.", timeout=3)
                if success_text:
                    print("✅ Success confirmation detected!")
                    success = True
                    break

                # Check if the Share button has disappeared (also means success)
                share_still_there = self.human.find_by_accessibility("Share", timeout=2)
                if not share_still_there:
                    print("✅ Share button gone. Assuming success.")
                    success = True
                    break

                time.sleep(3)

            if not success:
                self._take_screenshot("logs/failed_iphone_ig_post.png")
                raise Exception("Timed out waiting for IG to confirm the post.")

            # Dismiss any success modals
            self._dismiss_popups()

            # ==========================================
            # 🧊 PHASE 8: COOL DOWN
            # ==========================================
            print("🧊 Cooling down...")
            self.human.sleep(3, 6)
            self.human.scroll_feed(duration_seconds=15)

            return True

        except Exception as e:
            print(f"❌ iPhone IG post failed: {e}")
            self._take_screenshot("logs/failed_iphone_ig_post.png")
            return False

    def _dismiss_popups(self):
        """
        Dismisses common iOS and Instagram pop-ups (permissions,
        notifications, 'Turn On Notifications', etc.).
        """
        popup_labels = [
            "Allow",          # Photo library / camera permissions
            "OK",             # Generic system alerts
            "Not Now",        # IG notification prompts
            "Continue",       # Onboarding
            "Close",
        ]
        for label in popup_labels:
            btn = self.human.find_by_text(label, timeout=2)
            if btn:
                print(f"   Dismissing popup: '{label}'")
                self.human.tap_element(btn)
                self.human.sleep(0.5, 1.2)

    def _take_screenshot(self, path: str):
        """Save a screenshot to help debug failures."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.driver.save_screenshot(path)
            print(f"📸 Screenshot saved to {path}")
        except Exception as e:
            print(f"   (Could not save screenshot: {e})")
