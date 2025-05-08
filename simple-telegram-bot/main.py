import time
import os
import requests

# Get environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")  # Example: @mychannel

# Dummy product list
dummy_products = [
    {
        "title": "Wireless Earbuds - Super Bass!",
        "price": "$12.99",
        "affiliate_link": "https://s.click.aliexpress.com/deep_link_dummy"
    },
    {
        "title": "USB-C Fast Charging Cable",
        "price": "$2.49",
        "affiliate_link": "https://s.click.aliexpress.com/deep_link_dummy"
    }
]

def post_to_telegram(product):
    message = f"🔥 {product['title']}\n\nPrice: {product['price']}\n[Buy Now]({product['affiliate_link']})"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(telegram_url, data=payload)
    print("Sent to Telegram:", response.status_code, response.text)

def main():
    for product in dummy_products:
        post_to_telegram(product)
        time.sleep(2)  # Short pause between posts

if __name__ == "__main__":
    main()
