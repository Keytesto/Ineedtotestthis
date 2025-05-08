import hashlib
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

# Signature generation
def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    concatenated = ''.join(f"{k}{v}" for k, v in sorted_params)
    to_sign = f"{app_secret}{concatenated}{app_secret}"
    print("🔐 String to sign:", repr(to_sign))
    signature = hashlib.sha256(to_sign.encode("utf-8")).hexdigest().upper()
    print("✅ Signature:", signature)
    return signature

# Telegram sender
def send_to_telegram(message, image_url=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto" if image_url else f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "photo" if image_url else "text": image_url if image_url else message,
        "caption" if image_url else "text": message
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("❌ Failed to send message:", response.json())

# Fetch product
def fetch_product():
    timestamp = str(int(time.time() * 1000))  # ✅ Use only str version

    method = "aliexpress.affiliate.hotproduct.query"
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

    params = {k: str(v) for k, v in params.items()}  # ✅ Ensure string values
    params["sign"] = generate_signature(params, APP_SECRET)

    # ✅ Switched to official working endpoint
    url = f"https://api.aliexpress.com/sync?{urllib.parse.urlencode(params)}"
    print("🌐 Final Request URL:", url)

    response = requests.get(url)
    print("📦 Raw Response:", response.text)

    try:
        data = response.json()
        print("📦 Parsed JSON:", data)

        products = data["resp_result"]["result"]["products"]
        if not products:
            print("⚠️ No products found.")
            return None

        product = products[0]
        return {
            "title": product["product_title"],
            "image_url": product["product_main_image_url"],
            "price": product["sale_price"],
            "url": product["product_detail_url"]
        }
    except Exception as e:
        print(f"❌ Failed to fetch product: {e}")
        return None

# Run bot
def run():
    product = fetch_product()
    if product:
        message = f"Title: {product['title']}\nPrice: ${product['price']}\nURL: {product['url']}"
        send_to_telegram(message, product["image_url"])
    else:
        print("⚠️ No product to send.")

if __name__ == "__main__":
    run()
