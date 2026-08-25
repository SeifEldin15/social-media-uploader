"""
SHADOW POSTER - iPHONE MASTER CONTROLLER
This is the iPhone equivalent of main.py.
It orchestrates:
  1. Reading the next pending job from content.csv
  2. Transferring the media file from this PC to the iPhone's photo library
  3. Starting the Appium session (connecting to the phone via USB)
  4. Running the correct iPhone poster module (IG / TikTok / X)
  5. Marking the job as completed

PREREQUISITES (one-time setup):
  - Appium installed: npm install -g appium
  - XCUITest driver: appium driver install xcuitest
  - Appium server running: appium --port 4723
  - iPhone connected via USB, trusted on this PC
  - pymobiledevice3 installed: pip install pymobiledevice3
"""

import os
import sys
import time
import subprocess
import threading

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from content_manager import ContentManager
from iphone_human import IPhoneHuman

# ==========================================
# GLOBAL CONFIGURATION
# ==========================================
APPIUM_URL = "http://localhost:4723"

# iOS bundle IDs for each platform's native app
BUNDLE_IDS = {
    'ig':     'com.burbn.instagram',
    'tiktok': 'com.zhiliaoapp.musically',
    'x':      'com.atebits.Tweetie2',
}

# ==========================================
# UTILITY: DETECT CONNECTED iPHONE UDID
# ==========================================
def detect_iphone_udid() -> str | None:
    """
    Tries to auto-detect the UDID of the first connected iPhone.
    Uses pymobiledevice3 (pure Python, works on Windows without iTunes CLI tools).
    Falls back to the 'idevice_id' binary from libimobiledevice if installed.
    """
    # Method 1: pymobiledevice3 (preferred, Windows-compatible, pure Python)
    try:
        from pymobiledevice3.usbmux import select_devices_by_connection_type
        devices = select_devices_by_connection_type('USB')
        if devices:
            udid = devices[0].serial
            print(f"📱 iPhone detected via pymobiledevice3 — UDID: {udid}")
            return udid
    except ImportError:
        print("⚠️ pymobiledevice3 not installed. Trying fallback...")
    except Exception as e:
        print(f"⚠️ pymobiledevice3 detection failed: {e}")

    # Method 2: idevice_id binary (requires libimobiledevice on PATH)
    try:
        result = subprocess.run(
            ["idevice_id", "-l"],
            capture_output=True, text=True, timeout=10
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        if lines:
            udid = lines[0]
            print(f"📱 iPhone detected via idevice_id — UDID: {udid}")
            return udid
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"⚠️ idevice_id detection failed: {e}")

    print("❌ No iPhone detected. Is it plugged in and trusted?")
    return None

# ==========================================
# UTILITY: TRANSFER MEDIA TO iPHONE
# ==========================================
def transfer_media_to_iphone(udid: str, local_path: str) -> bool:
    """
    Copies a media file from this Windows PC to the iPhone's
    Photos app (Camera Roll) using pymobiledevice3.
    
    The iOS poster scripts then pick the most recently added item
    from the photo library, which will be this file.

    Returns True on success, False on failure.
    """
    if not local_path or not os.path.exists(local_path):
        print(f"⚠️ No media file to transfer: {local_path}")
        return False

    print(f"📤 Transferring '{os.path.basename(local_path)}' to iPhone photo library...")

    # Method 1: pymobiledevice3 photo library upload
    try:
        from pymobiledevice3.lockdown import create_using_usbmux
        from pymobiledevice3.services.afc import AfcService

        lockdown = create_using_usbmux(serial=udid)

        # Use the MediaDomain AFC service to write directly into the DCIM folder
        with AfcService(lockdown, service_name='com.apple.afc') as afc:
            # Read our local file
            with open(local_path, 'rb') as f:
                data = f.read()
            
            filename = os.path.basename(local_path)
            remote_path = f'DCIM/100APPLE/{filename}'
            
            # Make sure the target directory exists
            try:
                afc.makedirs('DCIM/100APPLE')
            except Exception:
                pass  # Directory may already exist

            afc.set_file_contents(remote_path, data)
            print(f"✅ Media transferred to iPhone: {remote_path}")
            
            # Give iOS a moment to index the new file in Photos
            time.sleep(3)
            return True

    except ImportError:
        print("⚠️ pymobiledevice3 not installed. Cannot auto-transfer media.")
        print("   Install it: pip install pymobiledevice3")
    except Exception as e:
        print(f"⚠️ pymobiledevice3 transfer failed: {e}")

    # Method 2: idevicescreenshot / ideviceinstaller CLI (if available)
    # This is a weaker fallback — we just warn the user.
    print("⚠️ Automatic media transfer failed.")
    print("   Please manually AirDrop or copy the file to your iPhone's Photos app,")
    print(f"   then press any key in the terminal to continue.")
    try:
        input("   → Press ENTER once the media is on the iPhone... ")
        return True
    except EOFError:
        # Running non-interactively (e.g. from the UI)
        print("❌ Cannot prompt for manual transfer in UI mode. Aborting.")
        return False

# ==========================================
# UTILITY: START APPIUM SESSION
# ==========================================
def create_appium_session(udid: str, platform: str, ios_version: str = None):
    """
    Creates and returns an Appium WebDriver session connected
    to the iPhone app specified by the platform string.

    Args:
        udid: The iPhone's UDID.
        platform: 'ig', 'tiktok', or 'x'.
        ios_version: iOS version string e.g. "17.5". Auto-detected if None.
    """
    try:
        from appium import webdriver
        from appium.options import XCUITestOptions
    except ImportError:
        raise RuntimeError(
            "Appium Python client not installed! Run: pip install Appium-Python-Client"
        )

    bundle_id = BUNDLE_IDS.get(platform)
    if not bundle_id:
        raise ValueError(f"Unknown platform '{platform}' for iPhone posting.")

    # Auto-detect iOS version if not provided
    if not ios_version:
        try:
            from pymobiledevice3.lockdown import create_using_usbmux
            lockdown = create_using_usbmux(serial=udid)
            ios_version = lockdown.product_version
            print(f"📱 Auto-detected iOS version: {ios_version}")
        except Exception:
            ios_version = "17.0"
            print(f"⚠️ Could not detect iOS version, defaulting to {ios_version}")

    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = "iPhone"
    options.udid = udid
    options.platform_version = ios_version
    options.bundle_id = bundle_id
    options.automation_name = "XCUITest"
    options.no_reset = True         # CRITICAL: keeps the app logged in between runs
    options.full_reset = False      # Never clear app data
    options.new_command_timeout = 300  # 5 min timeout for slow uploads

    print(f"🔌 Connecting Appium to app: {bundle_id} on UDID: {udid}...")
    driver = webdriver.Remote(APPIUM_URL, options=options)
    print("✅ Appium session established.")
    return driver

# ==========================================
# MAIN ENTRY POINT
# ==========================================
def main(target_platform: str = None, username: str = "default", udid: str = None, ios_version: str = None):
    """
    Main iPhone posting controller.

    Args:
        target_platform: 'ig', 'tiktok', or 'x'. If None, uses the next pending job.
        username: The account username (matches profiles in content.csv).
        udid: iPhone UDID. Auto-detected if None.
        ios_version: iOS version string. Auto-detected if None.
    """
    print(f"📱 iPhone Poster starting for {'ALL' if not target_platform else target_platform.upper()} (User: {username})...")

    # ==========================================
    # PHASE 1: FETCH THE JOB
    # ==========================================
    cm = ContentManager()
    job = cm.get_next_post(target_platform, username)

    if not job:
        print(f"🛑 No pending jobs for '{target_platform}' (user: {username}). Shutting down.")
        return

    platform = job.get('platform', '').strip().lower()
    print(f"📋 Found job #{job['id']} [{platform.upper()}]: '{job.get('caption', '')[:30]}...'")

    # ==========================================
    # PHASE 2: DETECT iPHONE
    # ==========================================
    if not udid:
        udid = detect_iphone_udid()
    if not udid:
        print("❌ Cannot continue without an iPhone UDID.")
        return

    # ==========================================
    # PHASE 3: MEDIA FILE PATHING
    # ==========================================
    raw_media = job.get('image_path', '').strip() if job.get('image_path') else None
    absolute_media_path = None
    has_media = False

    if raw_media:
        absolute_media_path = os.path.join(os.getcwd(), raw_media)
        if not os.path.exists(absolute_media_path):
            print(f"❌ CRITICAL: Media file not found at: {absolute_media_path}")
            print("   Check your media/ folder and content.csv. Aborting.")
            return
        has_media = True

    # ==========================================
    # PHASE 4: TRANSFER MEDIA TO iPHONE
    # ==========================================
    if has_media:
        transfer_ok = transfer_media_to_iphone(udid, absolute_media_path)
        if not transfer_ok:
            print("❌ Media transfer failed. Cannot post without media on the device.")
            return
    
    # ==========================================
    # PHASE 5: START APPIUM SESSION
    # ==========================================
    driver = None
    try:
        driver = create_appium_session(udid, platform, ios_version)
        human = IPhoneHuman(driver)

        # ==========================================
        # PHASE 6: RUN THE CORRECT POSTER
        # ==========================================
        success = False

        if platform == 'ig':
            from iphone_ig_poster import IPhoneIGPoster
            poster = IPhoneIGPoster(driver, human)
            success = poster.create_post(
                text=job['caption'],
                media_already_in_library=has_media
            )

        elif platform == 'tiktok':
            from iphone_tiktok_poster import IPhoneTikTokPoster
            poster = IPhoneTikTokPoster(driver, human)
            success = poster.create_post(
                text=job['caption'],
                media_already_in_library=has_media
            )

        elif platform == 'x':
            from iphone_x_poster import IPhoneXPoster
            poster = IPhoneXPoster(driver, human)
            success = poster.create_post(
                text=job['caption'],
                has_media=has_media
            )

        else:
            print(f"❌ Unknown platform '{platform}' for iPhone posting.")

        # ==========================================
        # PHASE 7: MARK COMPLETE
        # ==========================================
        if success:
            print("✅ iPhone post successful!")
            cm.mark_post_as_complete(job['id'])
        else:
            print("❌ iPhone post failed. Job left as 'pending' for retry.")

    except Exception as e:
        print(f"❌ Critical iPhone posting error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Always clean up the Appium session
        if driver:
            try:
                driver.quit()
                print("🔌 Appium session closed.")
            except Exception:
                pass

if __name__ == "__main__":
    main()
