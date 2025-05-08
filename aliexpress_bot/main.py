
import hashlib
import time
import requests
import urllib.parse
import os
from functools import wraps

# ✅ Logging decorator for status messages
def wrapper(func):
    from functools import wraps
    @wraps(func)
    def inner(*args, **kwargs):
        print(f"▶️ Starting: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"✅ Finished: {func.__name__}")
        return result
    return inner

# ✅ AliExpress API credentials (set via Railway environment variables)
APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")
TRACKING_ID = os.environ.get("TRACKING_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# ✅ Signature generation
def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    concatenated = ''.join(f"{k}{v}" for k, v in sorted_params)
    to_sign = f"{app_secret}{concatenated}{app_secret}"
    return hashlib.sha256(to_sign.encode("utf-8")).hexdigest().upper()

# ✅ Send message or photo to Telegram
@wrapper
def send_to_telegram(message, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "photo": image_url,
            "caption": message,
            "parse_mode": "Markdown"
        }
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        }

    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("❌ Failed to send message:", response.text)

# ✅ Fetch a hot product from AliExpress
@wrapper
def fetch_product():
    timestamp = int(time.time() * 1000)
    method = "aliexpress.affiliate.hotproduct.query"

    params = {
        "app_key": APP_KEY,
        "method": method,
        "format": "json",
        "sign_method": "sha256",
        "timestamp": str(timestamp),
        "v": "2.0",
        "tracking_id": TRACKING_ID,
        "fields": "product_id,product_title,product_main_image_url,product_detail_url,sale_price",
        "target_currency": "USD",
        "target_language": "EN",
        "page_size": "1",
    }

    params["sign"] = generate_signature(params, APP_SECRET)
    url = f"https://api-sg.aliexpress.com/sync?{urllib.parse.urlencode(params)}"

    try:
        response = requests.get(url)
        data = response.json()
        product = data["resp_result"]["result"]["products"][0]
        return {
            "title": product["product_title"],
            "image_url": product["product_main_image_url"],
            "price": product["sale_price"],
            "url": product["product_detail_url"]
        }
    except Exception as e:
        print(f"❌ Failed to fetch product: {e}")
        return None

# ✅ Main runner function
@wrapper
def run():
    product = fetch_product()
    if product:
        message = f"🔥 *{product['title']}*\n💲 Price: ${product['price']}\n🔗 [View Product]({product['url']})"
        send_to_telegram(message, product["image_url"])
    else:
        print("⚠️ No product fetched.")

# ✅ Entry point
if __name__ == "__main__":
    run()
