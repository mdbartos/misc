from flask import Flask, request
from werkzeug.serving import WSGIRequestHandler
app = Flask(__name__)

@app.route("/<path>", methods=['GET', 'POST'])
def hello(path):
    data = request.get_data(as_text=True)
    print('Path: ', path)
    print('Data: ', data)
    return "Hello World!"

if __name__ == "__main__":
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host='0.0.0.0', port=50000)
