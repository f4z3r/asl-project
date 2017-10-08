MIDDLEWARE LAYOUT:

            Blocking Queue
            +-+-+-+-+-+     ---> Thread
Client -->  | | | | | | --> ---> Thread --> Client
            +-+-+-+-+-+     ---> Thread

Each thread will be connected to every server containing a copy of the key value store. In cases of reads, note that load balancing needs to be considered. Whether to load balance with the other threads is to see.

QUEUE:
Make usage of java.util.concurrent.BlockingQueue
This queue makes sure that the multiple threads acting on the queue do not pop the same element when requesting a new job.

Note that one separate thread will probably have to handle adding new jobs to the queue. That thread then only handles storing the requests of the clients onto the queue. Note that we will not implement a priority queue as it makes the system more complex and no client has reason for priority.


WORKING THREADS:
Each working thread will be connected to each server containing copies of the key value store. Note that a single thread can perform some load balancing when handling a MUTLIGET by sending separate requests to distinct servers instead of a single large request to a single server. Whether each thread will communicate with the other threads to ensure that load balancing is performed across all threads is to be determined but unlikely. A more simple and equally effective approach is to use a stochastic approach.

Each thread is then responsible for sending a response to the client based on the request.

Make use of the java.lang.Runtime class and availableProcessors() function to determine the number of cores on the machine and run the middleware on said number of cores. Note that this needs to be logged as it greatly affects performance.
Make use of Fork/Join framework to have parallelism.

Do not shut down the threads between each job. Thread creation can take significant time if the jobs are short (which is likely going to be the case).


GENERAL:
Create main class called:
    MyMiddleware(myIp, myPort, mcAddresses, numThreadsPTP, readSharded)
with run function to run the system.

myIp            External IP address of the middleware host
myPort          Port that the middleware listens to
mcAddresses     Addresses and ports of the database servers
numThreadsPTP   Number of threads the middleware runs on
readSharded     Boolean providing whether reads should be sharded or not





PROGRAM STRUCTURE:
MyMiddleware:       main class
    run()           runs the middleware

    calls on blocking queue (instance of it) maybe extension for more info sharing across threads

WorkingThread implements Runnable
    run()           connects to server, parses and load balances

    parseRequest()  parses requests
    getServer()     stochastic approach for load balancing

Request
    Stores
        command
        client that requested
        time received
        parsed: is it ready to be sent to servers


Use python fabric3 to automate uploads, log file uploading to github/gitlab test automation, distribution automation etc. Note that the servers run on ubuntu.


