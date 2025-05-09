import hashlib
import time
import requests
import os

# Load credentials
APP_KEY = os.environ.get("APP_KEY", "").strip()
APP_SECRET = os.environ.get("APP_SECRET", "").strip()
TRACKING_ID = os.environ.get("TRACKING_ID", "").strip()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()

def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    base_string = ''.join(f"{k}{v}" for k, v in sorted_params)
    string_to_sign = f"{app_secret}{base_string}{app_secret}"
    signature = hashlib.md5(string_to_sign.encode('utf-8')).hexdigest().upper()
    return signature

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
        print("Failed to send message:", response.json())

def fetch_product():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    method = "aliexpress.affiliate.productdetail.get"
    params = {
        "app_key": APP_KEY,
        "method": method,
        "format": "json",
        "sign_method": "md5",
        "timestamp": timestamp,
        "v": "2.0",
        "product_ids": "1005006979768567",
        "target_currency": "USD",
        "target_language": "EN",
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_signature(params, APP_SECRET)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    response = requests.post("http://gw.api.taobao.com/router/rest", data=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            product = data["resp_result"]["result"]["products"][0]
            return {
                "title": product["product_title"],
                "image_url": product["product_main_image_url"],
                "price": product["sale_price"],
                "url": product["product_detail_url"]
            }
        except (KeyError, IndexError):
            print("Failed to extract product details.")
            return None
    else:
        print("API request failed with status code:", response.status_code)
        return None

def run():
    product = fetch_product()
    if product:
        message = f"Title: {product['title']}\nPrice: ${product['price']}\nURL: {product['url']}"
        send_to_telegram(message, product["image_url"])
    else:
        print("No product to send.")

if __name__ == "__main__":
    run()
