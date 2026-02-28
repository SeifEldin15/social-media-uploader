"""
SHADOW POSTER - CONTENT MANAGER
This module acts as the system's memory. It safely reads the content.csv file to find
out what we need to post today, and updates the file when a post succeeds 
so we don't accidentally spam the timeline with duplicates.
"""

import csv
import os

class ContentManager:
    def __init__(self):
        # ==========================================
        # 📍 PHASE 1: LOCATING THE DATABASE
        # ==========================================
        # We look for 'content.csv' right in the main folder where you run main.py
        # Using os.getcwd() ensures it always finds it no matter where you launch the terminal from.
        self.csv_path = os.path.join(os.getcwd(), "content.csv")

    def get_next_post(self, platform_name: str = None):
        """
        Scans the CSV top-to-bottom for the first row that matches our platform 
        (or any platform if None) AND has a status of 'pending'.
        """
        # Pre-flight check: Did we accidentally delete or rename the CSV?
        if not os.path.exists(self.csv_path):
            print(f"⚠️ Where is {self.csv_path}? I can't post without my instructions!")
            return None

        # ==========================================
        # 📖 PHASE 2: READING THE DATA
        # ==========================================
        # We open the file in 'r' (read) mode with utf-8 encoding. 
        # (UTF-8 is absolutely crucial here, otherwise any emojis in your marketing copy will crash the script).
        with open(self.csv_path, mode='r', encoding='utf-8') as file:
            
            # DictReader is python magic. It maps your top row (id, platform, caption...) to dictionary keys.
            reader = csv.DictReader(file)
            for row in reader:
                # We clean the text with .strip() and .lower() so a stray space like " Pending " 
                # or a capital "X" doesn't break our strict logic.
                status = row.get('status', '').strip().lower()
                platform = row.get('platform', '').strip().lower()
                
                if status == 'pending' and (platform_name is None or platform == platform_name):
                    # Boom. We found our target. Return this exact row as a dictionary.
                    return row 
                    
        # If the loop finishes and we found nothing...
        print(f"📭 No pending posts found for {platform_name}.")
        return None

    def mark_post_as_complete(self, post_id: str):
        """
        Once a post goes live on X or LinkedIn, we have to permanently change its 
        status in the CSV from 'pending' to 'completed'. 
        """
        rows = []
        updated = False
        
        # ==========================================
        # 💾 PHASE 3: THE SAFE REWRITE
        # ==========================================
        # Step A: Read everything into memory first. 
        # (Never try to read and write to a CSV at the exact same time. It corrupts the file.)
        with open(self.csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames # Save the column headers for later
            for row in reader:
                
                # If this is the specific post we just uploaded...
                if row.get('id') == str(post_id):
                    row['status'] = 'completed' # Change the status!
                    updated = True
                    
                # Keep a copy of every row (changed or unchanged) in our list
                rows.append(row)
                
        # Step B: Overwrite the physical file with our updated list
        if updated:
            # 'w' mode deletes the old file contents and writes the fresh data
            with open(self.csv_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()   # Put the column names back at the top
                writer.writerows(rows) # Dump all our rows back in
            print(f"📝 Marked post #{post_id} as completed in the database.")