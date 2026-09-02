import os
import json
import ccxt
from flask import Flask, request, jsonify

app = Flask(__name__)

# 从 Railway 环境变量读取配置
exchange_id = os.environ.get('EXCHANGE_ID', 'okx')
api_key = os.environ.get('EXCHANGE_API_KEY', '')
secret_key = os.environ.get('EXCHANGE_SECRET', '')
passphrase = os.environ.get('EXCHANGE_PASSPHRASE', '')
is_sandbox = os.environ.get('IS_SANDBOX', 'false').lower() == 'true'

# 初始化 CCXT 交易所对象
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': api_key,
    'secret': secret_key,
    'password': passphrase,
    'enableRateLimit': True,
})

# 若环境变量开启了模拟盘，则切换至沙盒环境
if is_sandbox:
    exchange.set_sandbox_mode(True)
    print("[系统提示] 当前运行在模拟盘环境 (Sandbox Mode)")

latest_msg = "服务器运行中，等待 TradingView 信号..."

@app.route('/', methods=['GET'])
def home():
    env_str = "【模拟盘】" if is_sandbox else "【实盘】"
    return f"<h1>TradingView 监控中 {env_str}</h1><p>最新状态: {latest_msg}</p>"

@app.route('/webhook', methods=['POST'])
def webhook():
    global latest_msg
    
    # 解析 JSON 数据
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            raw_data = request.get_data(as_text=True)
            data = json.loads(raw_data)
    except Exception:
        data = None

    if data and isinstance(data, dict):
        action = data.get("action")      # "buy" 或 "sell"
        symbol = data.get("symbol")      # 例如 "BTC/USDT"
        amount = data.get("amount")      # 例如 0.001

        latest_msg = f"收到信号 -> 动作: {action}, 币种: {symbol}, 数量: {amount}"
        print(f"[收到信号] {latest_msg}")

        # 调用 CCXT 下单
        try:
            amount = float(amount)
            if action == "buy":
                order = exchange.create_market_buy_order(symbol, amount)
                print(f"[下单成功] 订单ID: {order['id']}")
                latest_msg += f" | 下单成功! 订单号: {order['id']}"
            elif action == "sell":
                order = exchange.create_market_sell_order(symbol, amount)
                print(f"[下单成功] 订单ID: {order['id']}")
                latest_msg += f" | 下单成功! 订单号: {order['id']}"
            else:
                latest_msg += " | 未知动作，未执行下单"
        except Exception as e:
            print(f"[下单失败] 原因: {e}")
            latest_msg += f" | 下单失败: {e}"

        return jsonify({"status": "success", "message": "Processed"}), 200
    else:
        raw_text = request.get_data(as_text=True)
        latest_msg = f"收到纯文本（未能解析为JSON）: {raw_text}"
        print(f"[文本信号] {latest_msg}")
        return jsonify({"status": "success", "message": "Raw text received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)