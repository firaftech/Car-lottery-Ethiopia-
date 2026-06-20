import requests
from flask import Flask, make_response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TARGET_URL = "https://firaftech.github.io/Lottery-Ethiopia-Arabic-/"
proxy_index = 0
proxy_list = []

def get_fresh_proxies():
    print("📡 Fetching clean proxy routing list...")
    try:
        # Pulls an updated, live HTTP proxy pool
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000"
        res = requests.get(url, timeout=7)
        lines = [f"http://{p}" for p in res.text.strip().split("\r\n") if p]
        return lines if lines else []
    except Exception as e:
        print(f"⚠️ Proxy API error: {e}")
        return []

@app.route('/get_page_with_new_ip')
def get_page():
    global proxy_index, proxy_list
    
    # Replenish pool if empty or exhausted
    if not proxy_list or proxy_index >= len(proxy_list):
        proxy_list = get_fresh_proxies()
        proxy_index = 0
        if not proxy_list:
            return "<h3 style='color:orange;text-align:center;'>Refreshing proxy connection channels... Pull to refresh.</h3>", 202

    # Rotate strictly to the next entry in the list
    selected_proxy = proxy_list[proxy_index]
    proxy_index += 1
    
    proxy_display = selected_proxy.split("//")[1]
    print(f"🔄 [ROTATION ACTIVE] Tunneling request via: {proxy_display}")

    try:
        proxies = {"http": selected_proxy, "https": selected_proxy}
        
        # Emulate a standard mobile browser completely so scripts evaluate through the proxy
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }
        
        # Execute the network request strictly over the isolated proxy tunnel
        response = requests.get(TARGET_URL, proxies=proxies, headers=headers, timeout=12)
        
        # Inject base rule so images and layout paths resolve accurately
        modified_content = f'<base href="https://firaftech.github.io/Lottery-Ethiopia-Arabic-/">' + response.text
        
        resp = make_response(modified_content)
        resp.headers['Content-Type'] = 'text/html; charset=utf-8'
        
        # Enforce severe cache destruction rules so Chrome updates the display instantly
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, proxy-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        
        # Strip iframe presentation blocks
        resp.headers.pop('X-Frame-Options', None)
        resp.headers.pop('Content-Security-Policy', None)
        
        return resp
        
    except Exception as e:
        print(f"❌ Connection dropped by proxy {proxy_display}. Skipping to next available IP address...")
        # Instantly skip over the dead proxy and jump to the next one automatically
        return get_page()

if __name__ == '__main__':
    # Run server without multi-threading to maintain strict sequential IP selection
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=False)
