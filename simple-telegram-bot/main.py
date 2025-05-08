import requests
import time
import os

# ==== 🔧 LOAD FROM ENV ====
ALIEXPRESS_APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
ALIEXPRESS_APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
TRACKING_ID = os.getenv("TRACKING_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
FETCH_INTERVAL_SECONDS = 3600  # 1 hour

# ==== 🔍 Fetch product from AliExpress ====
def fetch_product():
    url = "https://api-sg.aliexpress.com/sync"
    params = {
        "app_key": ALIEXPRESS_APP_KEY,
        "method": "aliexpress.affiliate.product.query",
        "sign_method": "sha256",
        "timestamp": int(time.time() * 1000),
        "page_size": 1,
        "fields": "product_title,product_main_image_url,product_detail_url,sale_price,discount",
        "target_currency": "USD",
        "target_language": "EN",
        "tracking_id": TRACKING_ID
    }

    response = requests.get(url, params=params)
    try:
        product = response.json()['resp_result']['result']['products'][0]
        return {
            "title": product["product_title"],
            "image": product["product_main_image_url"],
            "url": product["product_detail_url"],
            "price": product["sale_price"]
        }
    except Exception as e:
        print("❌ Failed to fetch product:", e)
        return None

# ==== 🖼 Send image and caption to Telegram ====
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

# ==== 🔁 Main loop ====
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
