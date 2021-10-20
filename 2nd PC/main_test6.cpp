
#include <iostream>
#include <string>

#include "tcp_client.h"

// gcc -o main_test6 main_test6.cpp tcp_client.cpp -lstdc++  -lpthread

// http://api.zeromq.org/4-3:zmq-inproc

int main() {

    int check_routine_ms = 20; // every 20ms check routine 

    TcpClient client(check_routine_ms);
    
    //connect to host
    client.conn("192.168.0.109", 50000);

    bool bSendSignal = false;
    bool bWorkDone = false;
    bool bStartSignal = true;
    bool bAllFinished = false;
    int nTrialCount = 0;
    int nTotalCount = 5;

    bool bLoopEnd = false;
    bool bEndFlag = false;
    
    while(!bLoopEnd)
    {
        /* your code line */
        for(int j=0;j<100000;j++)
        {
            int seq_num = client.CheckStatus(false);
            std::cout << "\r" << "seq_num[" << seq_num << "]your code line[" << j << "] is running"  << std::flush;
        }
        //////////////////// your code line is ended

        if(bStartSignal)
        {
            client.ClearStatusBit();
            client.Start(5000.0, false);
            bStartSignal = false;
        }

        if(client.WorkDone())
        {
            char buffer[40];
            float elapsedTime = client.GetElapsed_in_sec(false);        
            sprintf(buffer, "%.4f", elapsedTime);
            std::string str_elapsedTime(buffer);

            std::cout << "\r" << "[Elapsed Time :" << str_elapsedTime << "sec ]" << std::flush;
            std::cout << "nTrialCount (" << nTrialCount << " of " <<  nTotalCount << ") is ended" << std::endl;
            // at certain time (only work done): 
            bStartSignal = true;
            nTrialCount++;

            if(nTrialCount > nTotalCount)
            {        
                // really finished            
                std::cout << "Finished all jobs!" << std::endl;
                client.End();
                bEndFlag = true;
            }
        }

        if(bEndFlag)
        {
            break;
        }     
    }
}
