//
//  Hello World client in C++
//  Connects REQ socket to tcp://localhost:5555
//  Sends "Hello" to server, expects "World" back
//
#include <zmq.hpp>
#include <string>
#include <iostream>
#include <string>
#include <string.h>
#include <thread>

// gcc -o zmqclient zmq_client.cpp -lzmq -lstdc++

class ZMQClient
{
private:
    std::string _addr;
    zmq::context_t context;
    zmq::socket_t socket;
    std::string conn;
    std::binding
    int request_num;

public:
    ZMQClient::ZMQClient(std::string conn)
        : context(1), conn(conn), request_num(0)
    {

        std::cout << "Connecting to hello world server…" << std::endl;
    };

    ~ZMQClient(){

    };

    void Connect()
    {
        bCompleted = false;
        bRunning = true;
        socket->connect(conn);
    };

    void SendSignal()
    {
        zmq::message_t request(5);
        memcpy(request.data(), "Hello", 5);
        std::cout << "Sending Hello " << request_num << "…" << std::endl;
        socket.send(request);

        bCompleted = false;
        bRunning = true;
        request_num++;
    };

    void ReceiveSignal()
    {
        //  Get the reply.
        zmq::message_t reply;
        socket.recv(&reply);
        bCompleted = true;
        bRunning = false;

        std::cout << "Received World " << request_num << std::endl;
    };
        // http://thisthread.blogspot.com/2011/08/multithreading-with-zeromq.html

    void Test()
    {
        boost::thread m_thread;
        try
        {
            m_thread.create_thread(std::bind(&doWork, std::ref(context)));
        }
        catch (const zmq::error_t &ze)
        {
            std::cout << "Exception: " << ze.what() << std::endl;
        }
        m_thread.join(); // 6
    };

    void doWork(zmq::context_t &context)
    {
        try
        {
            zmq::socket_t socket(context, ZMQ_DEALER);  // 1
            socket.connect(conn); 
            
            zmq::message_t request(5);
            memcpy(request.data(), "Hello", 5);
            std::cout << "Sending Hello " << request_num << "…" << std::endl;
            socket.send(request);
                                  // 2
            while (true)
            {
                zmq::message_t request;
                socket.recv(&request);

                std::string data((char *)request.data(), (char *)request.data() + request.size());
                std::cout << "Received: " << data << std::endl;
                bCompleted = false;
                bRunning = true;

                boost::this_thread::sleep(boost::posix_time::seconds(1)); // 3
            }
        }
        catch (const zmq::error_t &ze)
        {
            std::cout << "Exception: " << ze.what() << std::endl;
        }
    };

    void Close()
    {
        socket.close();  
    };
};

int main()
{
    //  Prepare our context and socket
    ZMQClient zmqclient("tcp://localhost:12000");
    zmqclient.Connect();
    zmqclient.SendSignal();
    zmqclient.ReceiveSignal();
    return 0;
}
