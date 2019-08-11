from collections import deque
import requests
from sanic import Sanic, response

app = Sanic()
NULL = b''

queue = deque([], maxlen=10)

@app.route("/", methods=['POST'])
async def print_packet(request):
    json = request.json
    if 'value' in json:
        queue.append(json['value'])
    print(queue)
    return response.raw(NULL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
