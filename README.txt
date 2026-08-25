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

## 📱 5. iPhone Native App Posting (via Appium)

Post through the REAL Instagram, TikTok, and X iOS apps on a
physically connected iPhone — completely indistinguishable from
a human tapping the screen.

### Prerequisites (One-Time Setup)

**Step A — Install Node.js**
Download from https://nodejs.org/ (LTS version).

**Step B — Install Appium and the XCUITest driver**
Run these in a terminal:
  npm install -g appium
  appium driver install xcuitest

**Step C — Install Python dependencies**
  pip install Appium-Python-Client pymobiledevice3

**Step D — Connect your iPhone**
1. Plug the iPhone into your PC via USB.
2. Unlock the iPhone and tap "Trust This Computer" when prompted.
3. Make sure iTunes (or Apple Mobile Device Support) is installed
   so Windows can communicate with the iPhone.

**Step E — Start the Appium server** (every time you want to post)
Open a terminal and run:
  appium --port 4723
Leave this terminal open while posting.

### Finding Your UDID (Optional)
The UI has an "Auto-Detect" button next to the UDID field — just
click it and your iPhone's UDID will be filled in automatically.
If auto-detection fails, find your UDID manually:
- Open iTunes → click your device → right-click the serial number
  and select "Copy UDID".
- Paste it into the "iPhone UDID" field in the UI.

### Posting from the UI
1. Start the Appium server (`appium --port 4723`) in a terminal.
2. Open the UI: `python ui.py`
3. Enter your Active User and iPhone UDID (or click Auto-Detect).
4. Add a post to content.csv with `platform=ig` / `tiktok` / `x`.
5. Click the matching button in the "iPhone (Native Apps)" column.

The bot will:
  - Auto-transfer your media file to the iPhone's photo library
  - Open the native app (Instagram/TikTok/X) via Appium
  - Navigate the UI exactly like a human thumb would
  - Type the caption with realistic timing
  - Tap Post/Share and wait for confirmation
  - Mark the job complete in content.csv

### Notes
- The iPhone must stay unlocked and trusted during the session.
- Keep Appium server running in the background while posting.
- The first run on a fresh device may take a few extra minutes
  as Appium installs its WebDriverAgent helper app on the iPhone.
- If a post fails, check the `logs/` folder for a screenshot of
  exactly what the app looked like when it failed.

---
*Happy Posting!* 🚀🌑
