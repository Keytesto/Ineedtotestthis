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

# ✅ Signature generation
def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    base_string = ''.join(f"{k}{v}" for k, v in sorted_params)
    string_to_sign = f"{app_secret}{base_string}{app_secret}"
    print("🔐 String to sign:", repr(string_to_sign))
    signature = hmac.new(
        app_secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    print("✅ Signature:", signature)
    return signature

# ✅ Send to Telegram
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

# ✅ API Request
def make_request(params, endpoints):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    for endpoint in endpoints:
        try:
            url = f"{endpoint}?{urllib.parse.urlencode(params)}"
            print(f"🌐 Trying endpoint: {url}")
            response = requests.get(url, headers=headers)
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            try:
                return response.json()
            except:
                print("⚠️ Response not JSON")
        except Exception as e:
            print(f"⚠️ Request failed: {e}")
    return None

# ✅ Fetch product from aliexpress.affiliate.product.query
def fetch_product():
    timestamp = str(int(time.time() * 1000))

    method = "aliexpress.affiliate.product.query"
    params = {
        "app_key": APP_KEY,
        "method": method,
        "format": "json",
        "sign_method": "sha256",
        "timestamp": timestamp,
        "v": "2.0",
        "tracking_id": TRACKING_ID,
        "keywords": "gadgets",
        "fields": "product_id,product_title,product_main_image_url,product_detail_url,sale_price",
        "target_currency": "USD",
        "target_language": "EN",
        "page_size": "1",
        "page_no": "1"
    }

    params = {k: str(v) for k, v in params.items()}
    params["sign"] = generate_signature(params, APP_SECRET)

    endpoints = ["https://api-sg.aliexpress.com/sync"]
    data = make_request(params, endpoints)

    if not data:
        print("❌ No valid JSON response.")
        return None

    try:
        products = data["resp_result"]["result"]["products"]
        if not products:
            print("⚠️ No products returned.")
            return None

        product = products[0]
        return {
            "title": product.get("product_title", "N/A"),
            "image_url": product.get("product_main_image_url", ""),
            "price": product.get("sale_price", "N/A"),
            "url": product.get("product_detail_url", "")
        }
    except Exception as e:
        print(f"❌ Failed to parse product data: {e}")
        return None

# ✅ Main
def run():
    product = fetch_product()
    if product:
        message = f"🛒 *{product['title']}*\n💵 Price: ${product['price']}\n🔗 [Buy Now]({product['url']})"
        send_to_telegram(message, product["image_url"])
    else:
        print("⚠️ No product found.")

if __name__ == "__main__":
    run()
