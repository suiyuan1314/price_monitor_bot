import requests
import json
import time
import datetime
def fetch_binance_book_ticker(symbol):
    """
    using requests query Binance bookTicker data。
    Args:
        symbol: pair (e.g.: "SCRUSDT")
    """
    url = f"https://api1.binance.com/api/v3/ticker/bookTicker?symbol={symbol}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"query Binance API fail: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"parse Binance JSON fail: {e}")
        return None
def fetch_gate_book_ticker(symbol):
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    url = f"https://api.gateio.ws/api/v4/spot/order_book?currency_pair={symbol}"
    try:
        response = requests.request('GET', url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"query Gate API fail: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"parse Gate JSON fail: {e}")
        return None
def calculate_average_sell_price(buy_1_price, buy_1_quantity, buy_2_price, buy_2_quantity, total_quantity):
    """
    Args:
        buy_1_price
        buy_1_quantity
        buy_2_price
        buy_2_quantity
        total_quantity
    """
    if buy_1_quantity >= total_quantity:
        return buy_1_price
    total_available_quantity = buy_1_quantity + buy_2_quantity
    if total_available_quantity < total_quantity:
        return buy_2_price
    remaining_quantity = total_quantity - buy_1_quantity
    weighted_average_price = (buy_1_price * buy_1_quantity + buy_2_price * remaining_quantity) / total_quantity
    return weighted_average_price
# Function to send a notification to DingTalk
def send_dingtalk_notification(title, message, token):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": message
        }
    }
    try:
        response = requests.post(f"https://oapi.dingtalk.com/robot/send?access_token={token}", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print("Notification sent successfully")
        else:
            print(f"Failed to send notification. HTTP Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while sending notification: {e}")
        traceback.print_exc()
if __name__ == "__main__":
    while True:
        bn_book_ticker_data = fetch_binance_book_ticker("SCRUSDT")
        gate_book_ticker_data = fetch_gate_book_ticker("SCR_USDT")
        if bn_book_ticker_data and gate_book_ticker_data:
            print(bn_book_ticker_data["askPrice"])
            print(gate_book_ticker_data["bids"])
            bn_ask_one_price = float(bn_book_ticker_data["askPrice"])
            gt_bid_one_price = float(gate_book_ticker_data["bids"][0][0])
            gt_bid_two_price = float(gate_book_ticker_data["bids"][1][0])
            gt_bid_one_amt = float(gate_book_ticker_data["bids"][0][1])
            gt_bid_two_amt = float(gate_book_ticker_data["bids"][1][1])
            gt_bid_avg_price = calculate_average_sell_price(gt_bid_one_price, gt_bid_one_amt, gt_bid_two_price, gt_bid_two_amt, 200)
            print(gt_bid_avg_price)
            diff_price = gt_bid_avg_price - bn_ask_one_price
            diff_ratio = diff_price / bn_ask_one_price
            if diff_ratio >= 0.12:
                send_dingtalk_notification(f"Gate/Biniance Scroll {diff_price}={gt_bid_avg_price}-{bn_ask_one_price} exceed limit", f"[](info)Gate/Biniance Scroll price diff exceed limit \n - price diff:{diff_price} \n - BN:{bn_ask_one_price} \n - Gate first:{gt_bid_one_price}, {gt_bid_one_amt} \n - Gate second:{gt_bid_two_price}, {gt_bid_two_amt}", "")
            time.sleep(5)
​​​
