/*
    C++ Socket Client
*/
#include <iostream> //cout
#include <stdio.h> //printf
#include <string.h> //strlen
#include <string> //string
#include <sys/socket.h> //socket
#include <arpa/inet.h> //inet_addr
#include <netdb.h> //hostent
#include <unistd.h>

#include <thread>
#include <vector>
#include <iostream>
#include <future>
#include <chrono>
#include <mutex>

using namespace std;
// https://www.binarytides.com/code-a-simple-socket-client-class-in-c/
/*
    TCP Client class
*/

typedef std::chrono::high_resolution_clock Time;
typedef std::chrono::milliseconds ms;
typedef std::chrono::duration<float> fsec;
using time_point = Time::time_point;

class TcpClient
{
    private:
        int sock;
        std::string address;
        string response_data = "";
        int port;
        struct sockaddr_in server;

    public:
        TcpClient(int check_routine_ms);
        bool conn(string, int);
        bool send_data(string data);
        string receive(int); // something bad
        int receive(int sockfd, void *buf, size_t len, int flags);

    public:
        float GetElapsed_in_sec(bool bPrint);
        void SendAndRecieveSignalThread();         
        void Start(float wait_milliseconds, bool bPrint);
        void End();
        int CheckStatus(bool bPrint);
        void ClearStatusBit();
        bool WorkDone();

private:
    bool m_bConnected;
    bool m_bSendResult;
    bool m_bRecvResult;

    bool m_bOnceSend;
    bool m_bOnceRecv;

    bool m_bDone;
    bool m_bPrint;

    time_point m_start_time, m_end_time;
    float m_wait_ms;
    float m_eplased_time;
    int m_check_routine_ms;

    std::mutex mutex_lock;
    
    int seq_num;
    bool  m_bRestartTrigger;
    bool  m_bEndTrigger;
    string send_msgs;
    string recv_msgs;

private:
    std::future<bool> m_handle;
    std::thread runFunc;
    bool m_bThreadStart;
    string str_last_data;
};
