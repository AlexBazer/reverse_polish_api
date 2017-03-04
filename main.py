import json
import zmq
import bottle
import time
import signal
from bottle import post, request, response

context = zmq.Context()


@post('/')
def main():
    data = request.json
    if not data or 'expressions' not in data:
        return response_error('Request should contain expressions list')

    expressions = data['expressions']
    define_timeout(1)

    try:
        socket = connect_to_worker()
        results = [
            dict(calculate(expression, socket), expression=expression)
            for expression in expressions
        ]
    except ZMQNotResponding:
        return response_error('Reverse polish notation calculator is not running')
    else:
        stop_timeout()

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
    total_time = (time.time() - start)*1000.0
    return {
        'result': result,
        'time': '{0:.3f}'.format(total_time)
    }

def response_error(msg):
    response.status = 400
    return {'status': 'ERROR', 'msg': msg}

class ZMQNotResponding(Exception):
    pass

def define_timeout(seconds):
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(seconds)

def stop_timeout():
    signal.alarm(0)

def raise_timeout(*args, **kwargs):
    """Used to handle not responding zmq server"""
    raise ZMQNotResponding('ZMQ server is not responding')

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000)
