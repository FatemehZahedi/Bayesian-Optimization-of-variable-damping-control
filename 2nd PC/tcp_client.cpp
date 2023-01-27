#include "tcp_client.h"

/*
    constructor
*/
TcpClient::TcpClient(int check_routine_ms)
{
    sock = -1;
    port = 0;

    m_wait_ms = 0.0f;
    m_check_routine_ms = check_routine_ms;

    m_bOnceSend = false;
    m_bOnceRecv = false;

    m_bSendResult = false;
    m_bRecvResult = false;
    m_bDone = false;
    m_bConnected = false;

    m_bThreadStart = false;
    m_bRestartTrigger = false;
    m_bEndTrigger = false;

    seq_num = 0;
    m_end_time = Time::now();
}

/*
    Connect to a host on a certain port number
*/
bool TcpClient::conn(string address, int port)
{
    // create socket if it is not already created
    if(sock == -1)
    {
        //Create socket
        sock = socket(AF_INET , SOCK_STREAM , 0);
        if (sock == -1)
        {
            perror("Could not create socket");
        }

        cout<<"Socket created\n";
    }
    else { /* OK , nothing */ }

    server.sin_addr.s_addr = inet_addr(address.c_str());
    server.sin_family = AF_INET;
    server.sin_port = htons( port );

    //Connect to remote server
    if( connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0 )
    {
        perror("connect failed. Error");
        
        return false;
    }

    cout<<"Connected\n";
    address = address;
    port = port;
    m_bConnected = true;

    return true;
}

/*
    Send data to the connected host
*/
bool TcpClient::send_data(string data)
{
    cout<<"Sending data...";
    cout<<data;
    cout<<"\n";
    
    // Send some data
    if( send(sock , data.c_str() , strlen( data.c_str() ) , 0) < 0)
    {
        perror("Send failed : ");
        return false;
    }
    
    std::cout<< "\nData send :" << data << std::endl;

    m_bSendResult = true;

    return true;
}

/*
    Receive data from the connected host
*/
string TcpClient::receive(int size=512)
{
    char buffer[size];
    string reply = "";
    
    size_t len = 0;
    //Receive a reply from the server
    len = recv(sock , buffer , sizeof(buffer) , 0);

    if(len < 0)
    {
        puts("recv failed");
        return "";
    }
    else
    {
        buffer[len] = 0;
        std::cout << buffer << std::endl;
        string reply_data(buffer);
        reply = reply_data;   
        str_last_data = reply; 
    }

    return reply;
}

int TcpClient::receive(int sockfd, void *buf, size_t len, int flags)
{
    size_t toread = len;
    char  *bufptr = (char*) buf;

    while (toread > 0)
    {
        ssize_t rsz = recv(sockfd, bufptr, toread, flags);
        if (rsz <= 0)
            return rsz;  /* Error or other end closed connection */

        toread -= rsz;  /* Read less next time */
        bufptr += rsz;  /* Next buffer position to read into */
    }

    return len;
}

float TcpClient::GetElapsed_in_sec(bool bPrint)
{
    m_end_time = Time::now();
    std::chrono::duration<float> elapsed_seconds = m_end_time-m_start_time;
    m_eplased_time = fsec(elapsed_seconds).count();

    if(bPrint)
    {
        // elapsed_seconds.count();
        std::cout << "elapsed time: " << elapsed_seconds.count() << "s\n";
    }

    return m_eplased_time;
}

void TcpClient::SendAndRecieveSignalThread() 
{
    const auto wait_duration = std::chrono::milliseconds(m_check_routine_ms);

    while(1)
    {
        std::cout << "\r" << "seq_num :" << seq_num << std::flush;
                
        if(m_bEndTrigger)
        {
            seq_num = 99;
        }

        if(seq_num == 0)
        {
            if(m_bRestartTrigger)
            {
                seq_num = 1;
                m_bOnceSend = false;
                m_start_time = Time::now(); 
            }
        }
        else if(seq_num == 1)
        {
            if(!m_bConnected)
            {
                conn(address, port);
            }

            if(m_bConnected)
            {
                m_bOnceSend = false;
                m_bSendResult = false;
                seq_num = 2;
            }
        }
        else if(seq_num == 2)
        {
            if(!m_bOnceSend)
            {  
                send_msgs = "Hello";
                send_data(send_msgs);
                m_bOnceSend = true;
            }

            if(m_bSendResult)
            {
                seq_num = 3;
            }                   
        }
        else if(seq_num == 3)
        {
            GetElapsed_in_sec(m_bPrint);

            //Read response
            char chRecvBuff[1024];
            memset(chRecvBuff, 0, sizeof(chRecvBuff));

            mutex_lock.lock();
            //int iRet = receive(sock, chRecvBuff, sizeof(chRecvBuff), 0);
            //recv_msgs = string(chRecvBuff);
            recv_msgs = receive(1024);
            std::cout << "recv_msgs :" << recv_msgs << std::endl;
            mutex_lock.unlock();   

            if (recv_msgs == ""){
                m_bRecvResult = false;
            }
                
            else
            {
                std::string output = recv_msgs;
                std::cout << "\nrecieved data: " << output << std::endl;
                std::cout << "recieved result: " << m_bRecvResult << std::endl;
                std::cout << std::endl;
                m_bRecvResult = true;
            }

            if(m_bRecvResult)
            {
                seq_num = 4;
            }
        }
        else if(seq_num == 4)
        {
            GetElapsed_in_sec(false);
            m_bDone = true;
        }
        else if(seq_num == 99)
        {
            break;
        }

        if(m_eplased_time >= m_wait_ms)
        {
            // timeout : go to the first level
            GetElapsed_in_sec(m_bPrint);
            seq_num = 0;
        } 

        std::this_thread::sleep_for(wait_duration); 
    }
}

void TcpClient::Start(float wait_milliseconds, bool bPrint)
{
    m_wait_ms = wait_milliseconds; 
    m_bPrint = bPrint;
    seq_num = 0;
    m_bRestartTrigger = true;

    if(!m_bThreadStart)
    {
        runFunc = std::thread(&TcpClient::SendAndRecieveSignalThread, this);
        m_bThreadStart = true;
        m_bRestartTrigger = true;
    }
}

int TcpClient::CheckStatus(bool bPrint)
{
    GetElapsed_in_sec(bPrint);
    return seq_num;
}

bool TcpClient::WorkDone()
{
    return m_bDone;
}

void TcpClient::ClearStatusBit()
{
    m_bOnceSend = false;
    m_bOnceRecv = false;
    m_bSendResult = false;
    m_bRecvResult = false;
    m_bDone = false;
    
    std::cout << "\nClearStatusBit()" << std::endl;
}

void TcpClient::End()
{
    m_bEndTrigger = true;

    if(m_bThreadStart)
    {
        runFunc.join();
    }
    
    std::cout << "runFunc thread is terminated" << std::endl;
    close(sock);
    std::cout << "socket is closed" << std::endl;
}