"""
SHADOW POSTER - iPHONE TIKTOK MODULE
Controls the native TikTok iOS app via Appium/XCUITest.
TikTok's anti-bot is one of the most aggressive in the industry
on mobile. We rely heavily on the IPhoneHuman behavior engine
and use native XCUITest gestures that are indistinguishable from
real finger input.

Bundle ID: com.zhiliaoapp.musically
"""

import time
import os
import random
from appium.webdriver.common.appiumby import AppiumBy
from iphone_human import IPhoneHuman


class IPhoneTikTokPoster:
    def __init__(self, driver, human: IPhoneHuman):
        self.driver = driver
        self.human = human

    def create_post(self, text: str, media_already_in_library: bool = True) -> bool:
        """
        Posts a video to TikTok using the native iOS app.

        Args:
            text: The caption/description to type.
            media_already_in_library: Media must be pre-transferred to
                the iPhone photo library by iphone_main.py.
        """
        if not media_already_in_library:
            print("❌ iPhone TikTok Poster expects media to be in the photo library.")
            return False

        try:
            # ==========================================
            # 🏃 PHASE 1: WARM UP
            # ==========================================
            print("🏠 Opening TikTok and warming up...")
            self.human.sleep(4, 7)
            self._dismiss_popups()

            # Scroll the For You Page to look like a real viewer
            self.human.scroll_feed(duration_seconds=15)

            # ==========================================
            # ✍️ PHASE 2: OPEN THE CREATOR
            # ==========================================
            print("➕ Tapping the Create button (+)...")

            # TikTok's "+" is a prominent button at the bottom center.
            plus_btn = self.human.find_by_accessibility("Create video", timeout=8)
            if not plus_btn:
                plus_btn = self.human.find_by_text("Create", partial=True, timeout=5)
            if not plus_btn:
                # Fallback: tap the bottom-center of the screen
                size = self.driver.get_window_size()
                self.human.tap(size['width'] // 2, int(size['height'] * 0.93))
            else:
                self.human.tap_element(plus_btn)

            self.human.sleep(2, 4)
            self._dismiss_popups()

            # ==========================================
            # 📎 PHASE 3: SWITCH TO UPLOAD MODE
            # ==========================================
            print("📤 Switching to Upload mode...")

            # TikTok defaults to the camera. We need to tap "Upload" to access
            # existing videos from the photo library.
            upload_btn = self.human.find_by_accessibility("Upload", timeout=8)
            if not upload_btn:
                upload_btn = self.human.find_by_text("Upload", timeout=5)
            if not upload_btn:
                raise Exception("Could not find the 'Upload' button in the TikTok creator.")

            self.human.tap_element(upload_btn)
            self.human.sleep(2, 4)

            # ==========================================
            # 🎥 PHASE 4: SELECT THE VIDEO
            # ==========================================
            print("🎥 Selecting most recent video from library...")
            self._dismiss_popups()

            # The video picker shows recent items at the top. Tap the first one.
            first_video = self.human.find_element_safe(
                AppiumBy.CLASS_NAME, "XCUIElementTypeImage", timeout=10
            )
            if first_video:
                self.human.tap_element(first_video)
            else:
                size = self.driver.get_window_size()
                self.human.tap(int(size['width'] * 0.1), int(size['height'] * 0.3))

            self.human.sleep(2, 4)

            # Tap "Next" to proceed from the video picker
            next_btn = self.human.find_by_accessibility("Next", timeout=8)
            if not next_btn:
                next_btn = self.human.find_by_text("Next", timeout=5)
            if next_btn:
                self.human.tap_element(next_btn)
            self.human.sleep(2, 4)

            # TikTok may show a trimming/preview screen — tap Next again
            next_btn = self.human.find_by_accessibility("Next", timeout=5)
            if next_btn:
                self.human.tap_element(next_btn)
            self.human.sleep(3, 5)

            # ==========================================
            # 🗣️ PHASE 5: TYPE THE CAPTION
            # ==========================================
            print("✍️ Typing caption...")

            # TikTok's caption field is often labeled "Describe your video"
            caption_field = self.human.find_by_text("Describe your video", partial=True, timeout=8)
            if not caption_field:
                caption_field = self.human.find_element_safe(
                    AppiumBy.CLASS_NAME, "XCUIElementTypeTextView", timeout=5
                )
            if not caption_field:
                caption_field = self.human.find_element_safe(
                    AppiumBy.CLASS_NAME, "XCUIElementTypeTextField", timeout=5
                )
            if not caption_field:
                raise Exception("Could not find TikTok's caption/description field.")

            self.human.human_type(caption_field, text)
            self.human.sleep(1, 3)

            # Dismiss keyboard
            try:
                self.driver.hide_keyboard()
            except Exception:
                pass

            # ==========================================
            # 🚀 PHASE 6: POST
            # ==========================================
            print("🚀 Tapping Post...")
            post_btn = self.human.find_by_accessibility("Post", timeout=8)
            if not post_btn:
                post_btn = self.human.find_by_text("Post", timeout=5)
            if not post_btn:
                raise Exception("Could not find TikTok 'Post' button.")

            self.human.tap_element(post_btn)

            # ==========================================
            # 🕵️ PHASE 7: VERIFY SUCCESS
            # ==========================================
            print("⏳ Waiting for TikTok to confirm the post...")
            success = False
            deadline = time.time() + 120

            while time.time() < deadline:
                # TikTok shows a success toast or navigates back to the FYP
                success_indicators = [
                    "Your video is being uploaded",
                    "Video uploaded",
                    "Your video has been posted",
                    "Uploading",
                ]
                for indicator in success_indicators:
                    el = self.human.find_by_text(indicator, partial=True, timeout=2)
                    if el:
                        print(f"✅ Upload indicator found: '{indicator}'")
                        success = True
                        break

                if success:
                    break

                # Also check if the Post button has disappeared (means we moved on)
                post_still_there = self.human.find_by_accessibility("Post", timeout=2)
                if not post_still_there:
                    print("✅ 'Post' button gone. Assuming success.")
                    success = True
                    break

                time.sleep(3)

            if not success:
                self._take_screenshot("logs/failed_iphone_tiktok_post.png")
                raise Exception("Timed out waiting for TikTok to confirm the upload.")

            # ==========================================
            # 🧊 PHASE 8: COOL DOWN
            # ==========================================
            print("🧊 Cooling down on the FYP...")
            self.human.sleep(4, 7)
            self.human.scroll_feed(duration_seconds=20)

            return True

        except Exception as e:
            print(f"❌ iPhone TikTok post failed: {e}")
            self._take_screenshot("logs/failed_iphone_tiktok_post.png")
            return False

    def _dismiss_popups(self):
        """Dismisses common iOS permission and TikTok onboarding pop-ups."""
        popup_labels = [
            "Allow",
            "OK",
            "Not Now",
            "Continue",
            "Close",
            "Allow Access to All Photos",
            "Allow Access to Camera",
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
