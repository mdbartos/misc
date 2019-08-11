import requests
from sanic import Sanic, response

app = Sanic()
NULL = b''

@app.route("/", methods=['POST'])
async def print_packet(request):
    json = request.json
    print(json)
    return response.raw(NULL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
