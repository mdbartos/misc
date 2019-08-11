import requests
from sanic import Sanic, response

app = Sanic()
NULL = b''

protocol = 'http'
host = 'localhost'
port = 8001

@app.route("/", methods=['POST'])
async def forward_packet(request):
    json = request.json
    dest = '{protocol}://{host}:{port}/'.format(protocol=protocol,
                                                host=host, port=port)
    requests.post(dest, json=json)
    return response.raw(NULL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
