# 🌑 SHADOW POSTER - SETUP & USAGE GUIDE

Welcome to your automated social media posting engine. This system is designed to mimic human behavior (erratic scrolling, variable typing speeds) to bypass bot detection on X, Instagram, and TikTok.

---

## 🚀 1. Prerequisites
Ensure you have the following installed:
- **Python 3.10+**
- **Playwright Browsers**: Run `playwright install chrome` in your terminal.
- **Dependencies**: `pip install playwright playwright-stealth`

---

## 🔑 2. Initial Setup (Login Phase)
Before you can post, you must save your login sessions so the bot doesn't need your password every time.

1. Run the UI: `python ui.py`
2. Under **"Configure Accounts"**, click the button for the platform you want (X, Instagram, or TikTok).
3. A browser window will open. **Manually log in** to your account.
4. Once you are on the Home Feed and see your posts, **close the browser window**.
5. The session is now saved in `X_Profile/`, `IG_Profile/`, or `TikTok_Profile/`.

---

## 📋 3. Adding Content
The bot reads from `content.csv`. Open this file and add your posts:

- **platform**: `x`, `ig`, or `tiktok`
- **caption**: Your post text (use quotes if it contains commas).
- **media_path**: Path to your video/image (e.g., `media/sample.mp4`).
- **status**: Must be `pending` for the bot to pick it up.

---

## 🤖 4. Running the Bot
Launch the control panel: `python ui.py`

- **🚀 Next in Queue**: Processes the very next `pending` item in the CSV regardless of platform.
- **📸 Next IG Post**: Specifically looks for the next Instagram post and skips others.
- **🐦 Next X Post**: Specifically looks for the next X post.
- **🎵 Next TikTok Post**: Specifically looks for the next TikTok post.

---

## ⚠️ Important Tips
1. **Media folder**: Keep your videos and images in the `media/` folder.
2. **Anti-Ban**: The bot scrolls and "reads" posts before uploading. If it looks like it's doing nothing for 10-30 seconds, it's just pretending to be a human!
3. **Logs**: If a post fails, check the `logs/` folder for a screenshot of what the bot saw.

---
*Happy Posting!* 🚀🌑
