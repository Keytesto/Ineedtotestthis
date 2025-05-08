import hashlib
import time
import requests
import urllib.parse
import os

# Set your AliExpress API credentials (should be set in Railway environment variables)
APP_KEY = os.environ.get("APP_KEY", "").strip()
APP_SECRET = os.environ.get("APP_SECRET", "").strip()
TRACKING_ID = os.environ.get("TRACKING_ID", "").strip()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
# Load AliExpress & Telegram credentials from environment variables
APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")
TRACKING_ID = os.environ.get("TRACKING_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# ✅ Corrected signature generation
# ✅ Generate signature for API request
def generate_signature(params, app_secret):
    # Sort parameters by name
    sorted_params = sorted(params.items())

    # Concatenate as key + value (no separators, no encoding)
    concatenated = ''.join(f"{k}{v}" for k, v in sorted_params)

    # Debug logs for signature
    print("Sorted Parameters:", sorted_params)
    print("Concatenated String for Signature:", concatenated)

    # Sign with SHA256 and wrap with secret
    to_sign = f"{app_secret}{concatenated}{app_secret}"
    print("String to Sign:", to_sign)  # Added for debugging

    signature = hashlib.sha256(to_sign.encode("utf-8")).hexdigest().upper()
    print("Generated Signature:", signature)  # Added for debugging

    return signature

# 📨 Telegram sender
# 📨 Send message or image to Telegram
def send_to_telegram(message, image_url=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message
    }
    if image_url:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "photo": image_url,
            "caption": message
        }
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message
        }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("❌ Failed to send message:", response.json())

# 🔍 Fetch product
# 🔍 Fetch a hot product from AliExpress
def fetch_product():
    timestamp = str(int(time.time() * 1000))
    timestamp = int(time.time() * 1000)
    method = "aliexpress.affiliate.hotproduct.query"

    # All params must be strings
    # ✅ All values converted to string
    params = {
        "app_key": APP_KEY,
        "method": method,
        "format": "json",
        "sign_method": "sha256",
        "timestamp": timestamp,
        "timestamp": str(timestamp),
        "v": "2.0",
        "tracking_id": TRACKING_ID,
        "fields": "product_id,product_title,product_main_image_url,product_detail_url,sale_price",
@@ -65,14 +66,18 @@
        "page_size": "1"
    }

    # Generate signature and add to params
    # Ensure all values are strings (extra safety)
    params = {k: str(v) for k, v in params.items()}

    # ✅ Generate and add signature
    params["sign"] = generate_signature(params, APP_SECRET)

    # Correct API endpoint (POST request)
    url = "https://api-sg.aliexpress.com/open/api/param2/2/portals.open/aliexpress.affiliate.hotproduct.query"
    # ✅ Use correct endpoint (api-sg works, but you can also try api.aliexpress.com)
    url = f"https://api-sg.aliexpress.com/sync?{urllib.parse.urlencode(params)}"
    print("Request URL:", url)

    response = requests.post(url, data=params)
    # Request AliExpress API
    response = requests.get(url)
    data = response.json()
    print("📦 Full API Response:", data)

@@ -88,14 +93,14 @@
        print(f"❌ Failed to fetch product: {e}")
        return None

# ▶️ Run the bot
# ▶️ Run the Telegram bot
def run():
    product = fetch_product()
    if product:
        message = f"Title: {product['title']}\nPrice: ${product['price']}\nURL: {product['url']}"
        send_to_telegram(message, product["image_url"])
    else:
        print("⚠️ No product to send.")

if __name__ == "__main__":
    run()
