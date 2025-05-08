import hashlib
import time
import requests
import urllib.parse
import os

# Set your AliExpress API credentials (app_key, app_secret, and tracking_id)
APP_KEY = os.environ.get("APP_KEY")  # Make sure to set this as a Railway variable
APP_SECRET = os.environ.get("APP_SECRET")  # Make sure to set this as a Railway variable
TRACKING_ID = os.environ.get("TRACKING_ID")  # Make sure to set this as a Railway variable
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # Make sure to set this as a Railway variable
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")  # Make sure to set this as a Railway variable

# Helper function to generate signature
def generate_signature(params, app_secret):
    # Sort parameters by name
    sorted_params = sorted(params.items())
    
    # Create the concatenated string for signature
    encoded_str = ''.join(f"{k}{v}" for k, v in sorted_params)
    
    # Debugging: Print parameters and the concatenated string for signature
    print("Sorted Parameters:", sorted_params)
    print("Concatenated String for Signature:", encoded_str)

    # Generate the final signature (app_secret + encoded_str + app_secret)
    sign_str = f"{app_secret}{encoded_str}{app_secret}"
    return hashlib.sha256(sign_str.encode("utf-8")).hexdigest().upper()

# Function to send message to Telegram
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
    
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("❌ Failed to send message:", response.json())

# Function to fetch product from AliExpress API
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
    
    # Debugging: Print the full URL and parameters with the signature
    print("Request URL:", f"https://api-sg.aliexpress.com/sync?{urllib.parse.urlencode(params)}")
    
    # Step 2: Build URL and make GET request
    url = f"https://api-sg.aliexpress.com/sync?{urllib.parse.urlencode(params)}"
    response = requests.get(url)
    data = response.json()
    
    print("📦 Full API Response:", data)  # Print the full response to debug the output

    # Step 3: Extract product details
    try:
        # Ensure that the API returns products and extract the relevant information
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

# Main function to run the bot
def run():
    product = fetch_product()
    if product:
        message = f"Title: {product['title']}\nPrice: ${product['price']}\nURL: {product['url']}"
        send_to_telegram(message, product["image_url"])
    else:
        print("⚠️ No product to send.")

# Run the bot
if __name__ == "__main__":
    run()
