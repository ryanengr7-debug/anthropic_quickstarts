import requests

def check_anthropic_key(api_key):
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        # "model": "claude-3-haiku-20240307",
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 5,
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ API key is valid and working.")
        elif response.status_code == 401:
            print("❌ Invalid API key.")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")


if __name__ == "__main__":
    api_key = input("Enter your Anthropic API key: ").strip()
    check_anthropic_key(api_key)