import json
import zmq
import time
import signal
import logging
from bottle import Bottle, run, post, request, response

context = zmq.Context()
logging.basicConfig(filename='reverse_polish.log', level=logging.DEBUG)

app = application = Bottle()


@app.post('/calculate/')
def main():
    data = request.json
    if not data or 'expressions' not in data:
        return response_error('Request should contain expressions list')

    expressions = data['expressions']

    # Define timeout to cache NO response from ZMQ server
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
    """Define ZMQ connection and return socket to work with"""
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    return socket

def calculate(expression, socket):
    """Make request to ZMQ worker for calculation, logs results and times and returns them"""
    start = time.time()
    socket.send(bytes(expression))
    result = socket.recv()
    total_time = (time.time() - start)*1000.0
    total_time_str = '{0:.3f}'.format(total_time)
    logging.info('{} = {} in {}ms'.format(expression, result, total_time_str))

    return {
        'result': result,
        'time': total_time_str
    }

def response_error(msg):
    """Prepare error response"""
    response.status = 400
    logging.error(msg)
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
    run(app=app, host = '127.0.0.1', port = 8000)
