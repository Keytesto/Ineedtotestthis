import hashlib
import time
import requests
import urllib.parse
import os

# Load AliExpress & Telegram credentials from environment variables
APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")
TRACKING_ID = os.environ.get("TRACKING_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# 🔍 Debug: Show raw env variables
print("🔍 ENV DEBUG:")
print("APP_KEY:", repr(APP_KEY))
print("APP_SECRET:", repr(APP_SECRET))
print("TRACKING_ID:", repr(TRACKING_ID))

# ✅ Generate signature for API request
def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    concatenated = ''.join(f"{k}{v}" for k, v in sorted_params)
    to_sign = f"{app_secret}{concatenated}{app_secret}"
    print("🔐 String to sign:", repr(to_sign))
    signature = hashlib.sha256(to_sign.encode("utf-8")).hexdigest().upper()
    print("✅ Signature:", signature)
    return signature

# 📨 Send message or image to Telegram
def send_to_telegram(message, image_url=None):
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

# 🔍 Fetch a hot product from AliExpress
def fetch_product():
    timestamp = int(time.time() * 1000)

    # ✅ All values converted to string
    params = {
        "app_key": APP_KEY,
        "format": "json",
        "sign_method": "SHA256",  # UPPERCASE (important)
        "timestamp": str(timestamp),
        "v": "2.0",
        "tracking_id": TRACKING_ID,
        "fields": "product_id,product_title,product_main_image_url,product_detail_url,sale_price",
        "target_currency": "USD",
        "target_language": "EN",
        "page_size": "1"
    }

    # Ensure all values are strings (extra safety)
    params = {k: str(v) for k, v in params.items()}

    # ✅ Generate and add signature
    params["sign"] = generate_signature(params, APP_SECRET)

    # ✅ Use new OpenAPI endpoint format (no `method` in query)
    method_path = "aliexpress.affiliate.hotproduct.query"
    url = f"https://gw.api.alibaba.com/openapi/param2/2/portals.open/{method_path}/{APP_KEY}?{urllib.parse.urlencode(params)}"

    print("🌐 Final Request URL:", url)

    # Request AliExpress API
    response = requests.get(url)
    print("📦 Raw Response:", response.text)

    try:
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
