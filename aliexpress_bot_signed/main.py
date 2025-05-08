
import requests
import time
import os
import hashlib
import hmac
import urllib.parse

# ==== 🔧 Load from Railway Environment Variables ====
APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
TRACKING_ID = os.getenv("TRACKING_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
FETCH_INTERVAL_SECONDS = 3600  # Every 1 hour

# ==== 🔐 Generate signature for AliExpress ====
def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    query_string = ''.join(f"{k}{v}" for k, v in sorted_params)
    raw_string = app_secret + query_string + app_secret
    hash_obj = hashlib.sha256()
    hash_obj.update(raw_string.encode('utf-8'))
    return hash_obj.hexdigest().upper()

# ==== 🛍️ Fetch a product ====
def fetch_product():
    method = "aliexpress.affiliate.product.query"
    timestamp = int(time.time() * 1000)

    params = {
        "app_key": APP_KEY,
        "method": method,
        "timestamp": timestamp,
        "sign_method": "sha256",
        "format": "json",
        "v": "2.0",
        "page_size": 1,
        "fields": "product_title,product_main_image_url,product_detail_url,sale_price,discount",
        "target_currency": "USD",
        "target_language": "EN",
        "tracking_id": TRACKING_ID
    }

    # Generate signature
    sign = generate_signature(params, APP_SECRET)
    params["sign"] = sign

    url = "https://api-sg.aliexpress.com/sync"
    response = requests.get(url, params=params)

    try:
        data = response.json()
        print("📦 AliExpress Response:", data)
        product = data['resp_result']['result']['products'][0]
        return {
            "title": product["product_title"],
            "image": product["product_main_image_url"],
            "url": product["product_detail_url"],
            "price": product["sale_price"]
        }
    except Exception as e:
        print("❌ Failed to fetch product:", e)
        return None

# ==== 🖼 Send product to Telegram ====
def send_to_telegram(product):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    caption = f"<b>{product['title']}</b>\n\n💲Price: {product['price']}\n<a href='{product['url']}'>🔗 Buy Now</a>"

    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "photo": product["image"],
        "caption": caption,
        "parse_mode": "HTML"
    }

    response = requests.post(url, data=payload)
    print("📤 Sent to Telegram:", response.text)

# ==== 🔁 Main Loop ====
def main():
    while True:
        product = fetch_product()
        if product:
            send_to_telegram(product)
        else:
            print("⚠️ No product to send.")
        time.sleep(FETCH_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
