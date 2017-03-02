import json
import zmq
import bottle
from bottle import post, request, response

context = zmq.Context()


@post('/')
def main():
    data = request.json
    if not data or 'expressions' not in data:
        return response_error('Request should contain expressions list')

    expressions = data['expressions']
    socket = connect_to_worker()

    return {'status': 'OK', 'result': [
        calculate(expression, socket) for expression in expressions
    ]}

def connect_to_worker():
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    return socket

def calculate(expression, socket):
    socket.send(bytes(expression))
    return socket.recv()


def response_error(msg):
    response.status = 400
    return {'status': 'ERROR', 'msg': msg}

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000)
