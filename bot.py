from flask import Flask, request
import requests, time, hmac, hashlib, json, os

API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
app = Flask(__name__)

def coinex_sign(body_dict, tonce):
    body_json = json.dumps(body_dict, separators=(",", ":"), sort_keys=True)
    sign_str = body_json + str(tonce) + SECRET_KEY
    signature = hmac.new(
        SECRET_KEY.encode(),
        sign_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return body_json, signature

def coinex_order(symbol, side, amount):
    url = "https://api.coinex.com/v2/spot/order"
    tonce = int(time.time() * 1000)
    body = {
        "market": symbol,
        "side": side,
        "type": "market",
        "amount": str(amount)
    }
    body_json, signature = coinex_sign(body, tonce)
    headers = {
        "Content-Type": "application/json",
        "Access-ID": API_KEY,
        "Authorization": signature,
        "Tonce": str(tonce)
    }
    return requests.post(url, headers=headers, data=body_json).json()

@app.route("/coinexbot", methods=["POST"])
def coinexbot():
    data = request.json
    signal = data.get("signal")
    symbol = data.get("symbol", "BTCUSDT")
    qty = data.get("qty", 0.001)

    if signal == "BUY":
        return coinex_order(symbol, "buy", qty)
    if signal == "SELL":
        return coinex_order(symbol, "sell", qty)

    return {"error": "invalid signal"}

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
