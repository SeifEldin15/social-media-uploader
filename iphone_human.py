"""
SHADOW POSTER - iPHONE HUMAN BEHAVIOR ENGINE
This module is the anti-ban shield for the iPhone path.
Instagram, TikTok, and X on iOS watch for robotic tap/swipe
patterns. This class injects realistic imperfection into every
touch gesture so the automation looks like a real person using
their thumb.
"""

import time
import random
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException


class IPhoneHuman:
    def __init__(self, driver):
        # We receive the active Appium WebDriver session so we can
        # take full control of the iPhone's touchscreen.
        self.driver = driver

    # ==========================================
    # ⏱️ TIMING
    # ==========================================
    def sleep(self, min_time=1.5, max_time=4.0):
        """
        Randomized sleep to break up robotic timing patterns.
        iOS app telemetry logs precise inter-action intervals.
        Never be predictable.
        """
        duration = random.uniform(min_time, max_time)
        time.sleep(duration)

    # ==========================================
    # 👆 TAP
    # ==========================================
    def tap(self, x: int, y: int, jitter: int = 8):
        """
        Tap a screen coordinate with a small random jitter.
        Humans never tap the exact pixel-centre of a button.
        """
        actual_x = x + random.randint(-jitter, jitter)
        actual_y = y + random.randint(-jitter, jitter)
        self.driver.tap([(actual_x, actual_y)], duration=random.randint(80, 180))

    def tap_element(self, element):
        """
        Tap a found WebElement with slight coordinate jitter
        to avoid the 'always tap dead-centre' bot pattern.
        """
        rect = element.rect
        cx = rect['x'] + rect['width'] // 2 + random.randint(-5, 5)
        cy = rect['y'] + rect['height'] // 2 + random.randint(-5, 5)
        self.driver.tap([(cx, cy)], duration=random.randint(80, 180))

    # ==========================================
    # 👆👆 DOUBLE TAP
    # ==========================================
    def double_tap(self, element):
        """Double-tap an element (like-a-post gesture)."""
        rect = element.rect
        cx = rect['x'] + rect['width'] // 2
        cy = rect['y'] + rect['height'] // 2
        self.driver.tap([(cx, cy)], duration=80)
        time.sleep(random.uniform(0.08, 0.15))
        self.driver.tap([(cx, cy)], duration=80)

    # ==========================================
    # 📜 SWIPE / SCROLL
    # ==========================================
    def swipe_up(self, distance: int = None):
        """
        Swipe upward (scroll down the feed), like a thumb
        pushing content upward. Distance is randomized if not set.
        """
        if distance is None:
            distance = random.randint(400, 800)

        size = self.driver.get_window_size()
        w = size['width']
        h = size['height']

        # Start from the lower-middle of the screen
        start_x = w // 2 + random.randint(-30, 30)
        start_y = int(h * 0.7) + random.randint(-20, 20)
        end_y = start_y - distance

        # Clamp end_y so we don't swipe off the top
        end_y = max(end_y, int(h * 0.1))

        self.driver.swipe(start_x, start_y, start_x, end_y,
                          duration=random.randint(300, 600))

    def swipe_down(self, distance: int = None):
        """Swipe downward (scroll up the feed)."""
        if distance is None:
            distance = random.randint(200, 500)

        size = self.driver.get_window_size()
        w = size['width']
        h = size['height']

        start_x = w // 2 + random.randint(-30, 30)
        start_y = int(h * 0.3) + random.randint(-20, 20)
        end_y = start_y + distance
        end_y = min(end_y, int(h * 0.9))

        self.driver.swipe(start_x, start_y, start_x, end_y,
                          duration=random.randint(300, 600))

    def scroll_feed(self, duration_seconds: int = 15):
        """
        Simulates a human doom-scrolling the iOS app feed.
        Essential for account health — bots just post and leave.
        Humans browse.
        """
        print(f"🚶 Simulating human scrolling for {duration_seconds} seconds...")
        end_time = time.time() + duration_seconds

        while time.time() < end_time:
            self.swipe_up()
            read_time = random.uniform(1.5, 4.5)
            print(f"👀 Pausing to view post for {read_time:.1f}s...")
            time.sleep(read_time)

            # 30% chance to scroll back up slightly
            if random.random() > 0.7:
                self.swipe_down(distance=random.randint(100, 300))
                time.sleep(random.uniform(0.8, 1.8))

    # ==========================================
    # ⌨️ TYPING
    # ==========================================
    def human_type(self, element, text: str):
        """
        Types text into an element (tap to focus, then keyboard.type).
        Uses variable delays between characters to mimic thumb typing.
        """
        print(f"✍️ Typing like a human ({len(text)} chars)...")
        self.tap_element(element)
        self.sleep(0.3, 0.8)

        for char in text:
            element.send_keys(char)

            # Physical delay: time for a thumb to lift and land again
            time.sleep(random.uniform(0.04, 0.18))

            # Cognitive delay: pause at word boundaries and punctuation
            if char in (' ', '.', ',', '!', '?', '\n') and random.random() > 0.75:
                time.sleep(random.uniform(0.2, 0.7))

    # ==========================================
    # 🔍 ELEMENT FINDING HELPERS
    # ==========================================
    def find_element_safe(self, by, value, timeout=10):
        """
        Tries to find an element, returning None instead of raising
        if it doesn't exist. Saves try/except clutter in poster code.
        """
        from appium.webdriver.common.appiumby import AppiumBy
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception:
            return None

    def find_by_text(self, text: str, partial: bool = False, timeout: int = 10):
        """
        Find an iOS element by its visible label/text.
        Uses XCUITest's native accessibility label matching.
        """
        if partial:
            predicate = f'label CONTAINS "{text}" OR name CONTAINS "{text}" OR value CONTAINS "{text}"'
        else:
            predicate = f'label == "{text}" OR name == "{text}"'
        return self.find_element_safe(
            AppiumBy.IOS_PREDICATE_STRING, predicate, timeout=timeout
        )

    def find_by_accessibility(self, label: str, timeout: int = 10):
        """Find element by its accessibility identifier."""
        return self.find_element_safe(
            AppiumBy.ACCESSIBILITY_ID, label, timeout=timeout
        )
