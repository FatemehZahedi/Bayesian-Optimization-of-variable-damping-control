import zmq
from  time import sleep
import time
import logging

log = logging.getLogger(__name__)

def main():

    HOST = '192.168.0.109'  # Standard loopback interface address (localhost)
    log.info("Hostname: %s", HOST)
    # Socket facing services
    context = zmq.Context.instance()
    # Socket facing services
    tcp_socket = context.socket(zmq.STREAM)
    backend    = context.socket(zmq.DEALER)

    tcp_socket.bind("tcp://%s:%s" % (HOST, 50000))
    backend.connect("tcp://%s:%s" % (HOST, 12000))

    seq_num = 0
    last_seq_num = seq_num

    while True:
        if(last_seq_num is not seq_num):
            last_seq_num = seq_num
            print("last_seq_num:", last_seq_num)
        
        if(seq_num == 0):
            id, reply = tcp_socket.recv_multipart()
            print("id, received:", id, str(reply))

            if reply and len(reply) > 1:
                backend.send_multipart([reply])
                seq_num = 1              

        elif(seq_num == 1):
            request = backend.recv_multipart()            
            print("request[0], len:", request[0], len(request[0]))
            data = request[0]

            if data and len(data) > 1:
                seq_num = 2

        elif(seq_num == 2):
            #tcp_socket.send_multipart([data])
            print("sending : ", data)

            tcp_socket.send_multipart([id, data])#, flags=zmq.DONTWAIT)  

            start = time.time()
            seq_num = 3

        elif(seq_num == 3):
            elapsed = time.time() - start
            if(elapsed > 3.0):
                seq_num = 0

        sleep(1)                

if __name__ == "__main__":
    main()


    
