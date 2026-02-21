import os
import json
import random
import requests
from datetime import datetime, timedelta

# --- CONFIGURATION ---
IMAGE_DIR = 'images'
HISTORY_FILE = 'history.json'
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# --- 30+ UNIVERSAL TITLES ---
TITLES = [
    "Nature's Silent Whisper", "The Green Escape", "Wild & Untamed", "Golden Hour Magic",
    "Forest Soul", "Mountain Highs", "Ocean Breezes", "Sun-Kissed Leaves",
    "The Path Less Traveled", "Earth's Artistry", "Morning Dew", "Serene Landscapes",
    "Into the Wild", "Nature's Palette", "Peaceful Horizons", "The Great Outdoors",
    "Hidden Gems", "Flora & Fauna", "Rhythm of the Rain", "Sunset Dreams",
    "Valley of Peace", "Wildflower Meadows", "The Sound of Silence", "Mist & Mystery",
    "Ancient Woods", "River Flows", "Sky Full of Wonders", "Nature's Healing Touch",
    "Deep in the Forest", "Peak Perfection", "Endless Summers", "Winter's Grace"
]

# --- 30+ UNIVERSAL CAPTIONS ---
CAPTIONS = [
    "Look deep into nature and you will understand everything better.",
    "Nature never goes out of style.", "Adopt the pace of nature: her secret is patience.",
    "The earth has music for those who listen.", "Find me where the wild things are.",
    "Keep your eyes on the stars and your feet on the ground.", "Nature is the art of God.",
    "In every walk with nature, one receives far more than he seeks.",
    "The mountains are calling and I must go.", "Stay close to nature's heart.",
    "A walk in nature walks the soul back home.", "Colors are the smiles of nature.",
    "Life is better in hiking boots.", "Let nature be your teacher.",
    "Fresh air, fresh mind.", "Nature: cheaper than therapy.",
    "Escape the ordinary, embrace the wild.", "Every sunset brings a promise of a new dawn.",
    "Nature's beauty is a gift.", "Collect moments, not things.",
    "The forest is calling.", "Let's find some beautiful place to get lost.",
    "Breathe in the wild.", "Simply breathe.", "Nature is my happy place.",
    "Mother Earth is beautiful.", "Leave nothing but footprints.",
    "To be at one with nature.", "Nature heals.", "Wild and free.",
    "Lost in the woods.", "The wilderness is where I belong."
]

INSTA_HASHTAGS = "#naturephotography #naturelovers #explorepage #instanature #wildlife #earthpix"
FB_HASHTAGS = "#nature #outdoors #photography #facebooknature #natureguide #greenlife"

def run_automation():
    # 1. Load History
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = {}

    today = datetime.now()
    updated_history = {}
    
    # 2. Logic: 15 din se adhik purani images ko delete karna
    for img_name, date_str in history.items():
        post_date = datetime.strptime(date_str, '%Y-%m-%d')
        if (today - post_date).days > 15:
            # Image file delete karein agar exist karti hai
            img_path = os.path.join(IMAGE_DIR, img_name)
            if os.path.exists(img_path):
                os.remove(img_path)
                print(f"Deleted old image: {img_name}")
        else:
            # Jo 15 din ke andar hain unhe history mein rakhein
            updated_history[img_name] = date_str

    # 3. Pick New Image
    all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    available_images = [img for img in all_images if img not in updated_history]

    if not available_images:
        print("No new images available to post.")
        # History save karke exit karein
        with open(HISTORY_FILE, 'w') as f:
            json.dump(updated_history, f)
        return

    selected_image = random.choice(available_images)
    image_path = os.path.join(IMAGE_DIR, selected_image)
    
    # 4. Prepare Metadata
    title = random.choice(TITLES)
    caption = random.choice(CAPTIONS)
    current_time = today.strftime("%A, %d %B %Y | %H:%M:%S")
    repo_name = os.getenv('GITHUB_REPOSITORY')
    image_url = f"https://raw.githubusercontent.com/{repo_name}/main/{image_path}"

    # 5. Telegram Post (Only Image + Timestamp)
    # DHYAN RAHE: File ke sabse upar yeh import zaroor ho: 
    # from datetime import datetime, timedelta

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        print("Sending to Telegram...")
        
        # Server time ko automatically Indian Standard Time (IST) mein convert karna
        ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        
        # Format: DD MONTH HH:MM:SS AM/PM YYYY aur sabko CAPITAL karna
        time_string = ist_now.strftime("%d %b %I:%M:%S %p %Y").upper()
        
        # Sirf bold date aur time, koi title/hashtag nahi
        telegram_caption = f"<b>{time_string}</b>"

        # Image bhejne ke liye correct variable (image_path) aur endpoint (sendPhoto)
        with open(image_path, 'rb') as photo_file:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            payload = {
                'chat_id': TELEGRAM_CHAT_ID, 
                'caption': telegram_caption,
                'parse_mode': 'HTML' # <b> tag se text ko bold karne ke liye zaroori hai
            }
            files = {'photo': photo_file}
            
            try:
                requests.post(url, data=payload, files=files)
                print("Telegram post successful!")
            except Exception as e:
                print(f"Telegram Error: {e}")
    else:
        print("Error: TELEGRAM_TOKEN ya TELEGRAM_CHAT_ID properly load nahi hua hai.")

    # 6. Webhook Post
    webhook_payload = {
        "image_link": image_url,
        "title": title,
        "caption": caption,
        "insta_hashtags": INSTA_HASHTAGS,
        "facebook_hashtags": FB_HASHTAGS,
        "posted_at": current_time
    }
    requests.post(WEBHOOK_URL, json=webhook_payload)

    # 7. Update History with new post
    updated_history[selected_image] = today.strftime('%Y-%m-%d')
    with open(HISTORY_FILE, 'w') as f:
        json.dump(updated_history, f)

if __name__ == "__main__":
    run_automation()
