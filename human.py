"""
SHADOW POSTER - HUMAN BEHAVIOR ENGINE
This module is the anti-ban shield. Social media platforms use highly advanced 
JS event listeners to track mouse movements, scroll speeds, and keystroke intervals.
This class injects chaos and imperfection into the bot to mimic a real person.
"""

import time
import random

class Human:
    def __init__(self, page):
        # We pass the active Playwright page into this class so the Human 
        # can take control of the mouse and keyboard on whatever tab is open.
        self.page = page

    def sleep(self, min_time=2, max_time=5):
        """
        Randomized sleep to break up robotic timing patterns.
        Instead of always waiting exactly 3.0 seconds (a massive red flag), 
        it waits 3.14 seconds, or 4.82 seconds, etc.
        """
        time.sleep(random.uniform(min_time, max_time))

    def scroll_feed(self, duration_seconds=40):
        """
        Simulates a human doom-scrolling the timeline. 
        This is crucial for account health; bots just post and leave. Humans browse.
        """
        print(f"🚶‍♂️ Simulating human scrolling for {duration_seconds} seconds...")
        end_time = time.time() + duration_seconds
        
        # ==========================================
        # 🔄 THE DOOM-SCROLL LOOP
        # ==========================================
        while time.time() < end_time:
            # 1. Scroll down a random amount (simulating a thumb swipe)
            scroll_amount = random.randint(300, 900)
            self.page.mouse.wheel(0, scroll_amount)
            
            # 2. Pause to "read" the post or look at an image
            read_time = random.uniform(1.5, 4.5)
            print(f"👀 Pausing to view post for {read_time:.1f}s...")
            time.sleep(read_time)
            
            # 3. The "Wait, what was that?" maneuver
            # 30% chance to scroll back up slightly, like a real person re-reading 
            # something they just scrolled past. This destroys bot-detection algorithms.
            if random.random() > 0.7:
                self.page.mouse.wheel(0, -random.randint(100, 400))
                time.sleep(random.uniform(1.0, 2.0))

    def human_type(self, selector, text):
        """
        Types out text with variable keystroke delays and micro-pauses.
        Never use page.fill() for social media! It pastes the text instantly.
        """
        print("✍️ Typing like a human...")
        
        # Click the text box to focus it
        self.page.click(selector)
        
        # ==========================================
        # ⌨️ THE CHAOTIC KEYBOARD
        # ==========================================
        for char in text:
            # 1. Type the single character
            self.page.keyboard.type(char)
            
            # 2. The Physical Delay
            # We sleep the thread between 0.05s (50ms) and 0.15s (150ms).
            # This perfectly mimics the physical travel time of a finger hitting keys.
            time.sleep(random.uniform(0.05, 0.15))
            
            # 3. The Cognitive Delay
            # If we hit a space or punctuation, there is a chance the "human" 
            # pauses to formulate their next thought.
            if char in [' ', '.', ',', '!', '?'] and random.random() > 0.8:
                pause_time = random.uniform(0.3, 0.8)
                time.sleep(pause_time)