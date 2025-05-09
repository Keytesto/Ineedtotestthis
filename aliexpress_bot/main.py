import hashlib
import hmac
import time
import requests
import urllib.parse
import os

# Load credentials
APP_KEY = os.environ.get("APP_KEY", "").strip()
APP_SECRET = os.environ.get("APP_SECRET", "").strip()
TRACKING_ID = os.environ.get("TRACKING_ID", "").strip()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()

# Debug
print("🔍 ENV DEBUG:")
print("APP_KEY:", repr(APP_KEY))
print("APP_SECRET:", repr(APP_SECRET))
print("TRACKING_ID:", repr(TRACKING_ID))

# ✅ Correct HMAC-SHA256 signature for AliExpress API v2.0
def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    base_string = ''.join(f"{k}{v}" for k, v in sorted_params)
    print("🔐 String to sign:", repr(base_string))
    signature = hmac.new(
        app_secret.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    print("✅ Signature:", signature)
    return signature

# Send message or image to Telegram
def send_to_telegram(message, image_url=None):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("⚠️ Telegram credentials not set.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto" if image_url else f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "caption" if image_url else "text": message
    }
    if image_url:
        data["photo"] = image_url

    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("❌ Failed to send Telegram message:", response.text)
    else:
        print("📨 Sent to Telegram successfully!")

# Make API request with fallback support
def make_request(params, endpoints):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    for endpoint in endpoints:
        try:
            url = f"{endpoint}?{urllib.parse.urlencode(params)}"
            print(f"🌐 Requesting: {url}")
            response = requests.get(url, headers=headers)

            if "application/json" in response.headers.get("Content-Type", ""):
                return response.json()
            else:
                print("⚠️ Unexpected content type:", response.headers.get("Content-Type"))

        except Exception as e:
            print(f"⚠️ Error during request: {e}")
    return None

# Fetch one featured product
def fetch_product():
    timestamp = str(int(time.time() * 1000))
    method = "aliexpress.affiliate.featuredpromo.products.get"

    params = {
        "app_key": APP_KEY,
        "method": method,
        "format": "json",
        "sign_method": "sha256",
        "timestamp": timestamp,
        "v": "2.0",
        "tracking_id": TRACKING_ID,
        "fields": "product_id,product_title,product_main_image_url,product_detail_url,sale_price",
        "target_currency": "USD",
        "target_language": "EN",
        "page_size": "1"
    }

    # Clean string conversion and signing
    params = {k: str(v) for k, v in params.items()}
    params["sign"] = generate_signature(params, APP_SECRET)

    endpoints = ["https://api-sg.aliexpress.com/sync"]
    data = make_request(params, endpoints)

    if not data:
        print("❌ No valid JSON response.")
        return None

    print("📦 Full API Response:", data)

    try:
        products = data["resp_result"]["result"]["products"]
        if not products:
            print("⚠️ No products returned.")
            return None

        product = products[0]
        return {
            "title": product["product_title"],
            "image_url": product["product_main_image_url"],
            "price": product["sale_price"],
            "url": product["product_detail_url"]
        }
    except Exception as e:
        print(f"❌ Failed to extract product: {e}")
        return None

# Main entry point
def run():
    product = fetch_product()
    if product:
        message = f"🔥 {product['title']}\n💰 Price: {product['price']}\n🔗 {product['url']}"
        send_to_telegram(message, product["image_url"])
    else:
        print("⚠️ No product found to send.")

if __name__ == "__main__":
    run()
