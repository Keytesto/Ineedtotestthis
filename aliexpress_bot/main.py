import hashlib
import hmac
import time
import requests
import os

# Load credentials
APP_KEY = os.environ.get("APP_KEY", "").strip()
APP_SECRET = os.environ.get("APP_SECRET", "").strip()
TRACKING_ID = os.environ.get("TRACKING_ID", "").strip()

# Signature generation
def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    base_string = ''.join(f"{k}{v}" for k, v in sorted_params)
    string_to_sign = f"{app_secret}{base_string}{app_secret}"
    signature = hmac.new(
        app_secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    return signature

# Send the API request with minimal params to test
def test_simple_request():
    timestamp = str(int(time.time() * 1000))

    params = {
        "app_key": APP_KEY,
        "method": "aliexpress.affiliate.featuredpromo.products.get",
        "format": "json",
        "sign_method": "sha256",
        "timestamp": timestamp,
        "v": "2.0",
        "tracking_id": TRACKING_ID,
        "page_size": 1
    }

    # Generate the signature
    params["sign"] = generate_signature(params, APP_SECRET)

    # Try the request to get featured products
    endpoint = "https://api-sg.aliexpress.com/sync"
    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        print("Response JSON:", response.json())  # Print the response to debug
    else:
        print("Failed to get response, status code:", response.status_code)

# Run the test request
if __name__ == "__main__":
    test_simple_request()
