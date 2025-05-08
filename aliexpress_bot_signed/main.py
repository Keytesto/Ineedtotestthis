import hashlib
import time
import requests
import urllib.parse

# === CONFIGURATION ===
APP_KEY = "YOUR_APP_KEY"
APP_SECRET = "YOUR_APP_SECRET"
TRACKING_ID = "YOUR_TRACKING_ID"
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHANNEL = "YOUR_TELEGRAM_CHANNEL_ID"  # e.g. -1001234567890


def generate_signature(params, app_secret):
    """
    Generate SHA256 signature for AliExpress Advanced API.
    """
    # Sort parameters alphabetically and prepare for signature
    sorted_params = sorted(params.items())
    encoded_str = ''.join(f"{k}{v}" for k, v in sorted_params)
    
    # Signature format: app_secret + encoded_str + app_secret
    sign_str = f"{app_secret}{encoded_str}{app_secret}"
    
    # Return the hashed signature (SHA-256)
    return hashlib.sha256(sign_str.encode("utf-8")).hexdigest().upper()


def fetch_product():
    """
    Fetch hot product using AliExpress Advanced API.
    """
    # Get the current timestamp in milliseconds
    timestamp = int(time.time() * 1000)
    
    # Method and API parameters
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
        "page_size": 1,
    }

    # Step 1: Generate signature
    params["sign"] = generate_signature(params, APP_SECRET)
    
    # Step 2: Build URL and make GET request
    url = f"https://api-sg.aliexpress.com/sync?{urllib.parse.urlencode(params)}"
    response = requests.get(url)
    data = response.json()
    
    print("📦 AliExpress Response:", data)

    # Step 3: Extract product details
    try:
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


def send_to_telegram(product):
    """
    Send product info to Telegram channel.
    """
    message = f"🔥 {product['title']}\n💰 Price: {product['price']}\n🔗 [View Product]({product['url']})"
    
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "caption": message,
        "photo": product["image_url"],
        "parse_mode": "Markdown"
    }
    
    resp = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", data=payload)
    print("📤 Telegram Response:", resp.text)


if __name__ == "__main__":
    product = fetch_product()
    if product:
        send_to_telegram(product)
    else:
        print("⚠️ No product to send.")
