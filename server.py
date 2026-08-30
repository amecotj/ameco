from flask import Flask, request

app = Flask(__name__)

# 用一个全局变量存最新收到的消息
last_message = "还没收到过 TradingView 的信号，快去点测试报警吧！"

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    global last_message
    if request.method == 'POST':
        # 把 TradingView 发来的数据打印并存起来
        data = request.get_json(force=True, silent=True) or request.get_data(as_text=True)
        print("收到 TradingView 报警:", data, flush=True)
        last_message = f"成功收到！内容是: {data}"
        return "success", 200
    else:
        # 只要你在浏览器里打开这个网址，就能直接看到最新收到的数据
        return f"<h1>TradingView 监控中</h1><p>{last_message}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)