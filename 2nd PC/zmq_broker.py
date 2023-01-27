import zmq
import time
from collections import OrderedDict

def test():

    context = zmq.Context.instance()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:12000")
    backend = context.socket(zmq.ROUTER)
    backend.bind("tcp://*:13000")
    frontend.setsockopt(zmq.RCVHWM, 100)
    backend.setsockopt(zmq.RCVHWM, 100)
    
    workers = OrderedDict()
    clients = {}
    msg_cache = []
    poll = zmq.Poller()
    
    poll.register(backend, zmq.POLLIN)
    poll.register(frontend, zmq.POLLIN)
    
    while True:
        socks = dict(poll.poll(10))
        now = time.time()
        # Receive back-end messages
        if backend in socks and socks[backend] == zmq.POLLIN:
                        # Receive back-end address, client address, and back-end return response ps: here worker_addr, client_addr, reply are all bytes type
            worker_addr, client_addr, response = backend.recv_multipart()
                        # Store the backend in workers
            workers[worker_addr] = time.time()
            if client_addr in clients:
                                # If the client address exists, forward the returned response to the client and delete the client
                frontend.send_multipart([client_addr, response])
                clients.pop(client_addr)
            else:
                                # Client does not exist
                print(worker_addr, client_addr)
                # Process all unprocessed messages
        while len(msg_cache) > 0 and len(workers) > 0:
                        # Take out a recently communicated worker
            worker_addr, t = workers.popitem()
                        # Determine whether the heartbeat period expires and retake the worker
            if t - now > 1:
                continue
            msg = msg_cache.pop(0)
                        # Forward cached messages
            backend.send_multipart([worker_addr, msg[0], msg[1]])
                # Receive front-end messages
        if frontend in socks and socks[frontend] == zmq.POLLIN:
                        # Get the client address and request content ps: client_addr and request here are all bytes type
            client_addr, request = frontend.recv_multipart()
            clients[client_addr] = 1
            while len(workers) > 0:
                                # Take out a recently communicated worker
                worker_addr, t = workers.popitem()
                                # Determine whether the heartbeat period expires and re-take the worker
                if t - now > 1:
                    continue
                                # Forward message
                backend.send_multipart([worker_addr, client_addr, request])
                break
            else:
                                # While normally ends, the message is not forwarded and stored in the cache
                msg_cache.append([client_addr, request])

if __name__ == '__main__':
   test() 
