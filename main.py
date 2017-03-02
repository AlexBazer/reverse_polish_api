import json
import zmq
import bottle
import time
from bottle import post, request, response

context = zmq.Context()


@post('/')
def main():
    data = request.json
    if not data or 'expressions' not in data:
        return response_error('Request should contain expressions list')

    expressions = data['expressions']
    socket = connect_to_worker()
    results = [
        dict(calculate(expression, socket), expression=expression)
        for expression in expressions
    ]

    status = 'OK'
    if all('ERROR' in result['result'] for result in results):
        status = 'ERROR'
        response.status = 400

    return {'status': status, 'results': results}

def connect_to_worker():
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    return socket

def calculate(expression, socket):
    start = time.time()
    socket.send(bytes(expression))
    result = socket.recv()
    return {
        'result': result,
        'time': int((time.time() - start)*1000000)
    }

def response_error(msg):
    response.status = 400
    return {'status': 'ERROR', 'msg': msg}

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000)
