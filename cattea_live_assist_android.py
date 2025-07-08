
import os
import time
from datetime import datetime

# Constants
FOLDER_PATH = "/storage/emulated/0/CatteaScreenshots"
SCREENSHOT_INTERVAL = 10  # seconds
MAX_FOLDER_SIZE = 1 * 1024 * 1024 * 1024  # 1 GB

def take_screenshot(is_cattea):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_cattea_{timestamp}.png" if is_cattea else f"screenshot_other_{timestamp}.png"
    filepath = os.path.join(FOLDER_PATH, filename)

    try:
        os.system(f"screencap -p '{filepath}'")
        print(f"📸 Saved screenshot: {filename}")
    except Exception as e:
        print(f"❌ Failed to take screenshot: {e}")

def get_folder_size():
    total_size = 0
    for dirpath, _, filenames in os.walk(FOLDER_PATH):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def cleanup_old_screenshots():
    files = []
    for filename in os.listdir(FOLDER_PATH):
        if filename.startswith("screenshot_other_") and filename.endswith(".png"):
            filepath = os.path.join(FOLDER_PATH, filename)
            files.append((filepath, os.path.getctime(filepath)))

    files.sort(key=lambda x: x[1])  # Oldest first

    current_size = get_folder_size()
    while current_size > MAX_FOLDER_SIZE and files:
        oldest_file, _ = files.pop(0)
        try:
            os.remove(oldest_file)
            current_size -= os.path.getsize(oldest_file)
            print(f"🗑️ Deleted: {oldest_file}")
        except Exception as e:
            print(f"⚠️ Error deleting {oldest_file}: {e}")

def main():
    os.makedirs(FOLDER_PATH, exist_ok=True)
    print("🚀 Cattea Live Screenshot Bot Started...")

    while True:
        is_cattea = True  # Placeholder for actual detection logic
        take_screenshot(is_cattea)
        cleanup_old_screenshots()
        time.sleep(SCREENSHOT_INTERVAL)

if __name__ == "__main__":
    main()
