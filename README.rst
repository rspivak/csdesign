Simple Examples of Concurrent Server Design in Python
-----------------------------------------------------

The `client.py <https://github.com/rspivak/csdesign/blob/master/client.py>`_ can be used with all the servers.

1. TCP Concurrent Server, One Child per Client (fork)

   `server01.py <https://github.com/rspivak/csdesign/blob/master/server01.py>`_

2. TCP Concurrent Server, I/O Multiplexing (select)

   `server02.py <https://github.com/rspivak/csdesign/blob/master/server02.py>`_

3. TCP Preforked Server, Children Call 'accept'

   Calling *'fork'* by the server for every client connection can be
   costly in terms of resources. One possible solution is to prefork
   some number of children when the server starts and use the pool of
   preforked processes to handle incoming connections.

   `server03.py <https://github.com/rspivak/csdesign/blob/master/server03.py>`_

   This design is a little bit unusual in a sense that it's not the
   server that calls *'accept'* to accept a new connection, but all
   children are blocked in the call to *'accept'* on the **same listening
   socket** passed from the parent process.

   The way it works is that all child processes are blocked waiting
   for an event on the same listening socket. When a new connection
   arrives **all** children are awakened. The first child process to
   run will make a call to *'accept'* and the rest of the processes
   will be put to sleep on the same call. Rinse repeat.
   The behavior is called `Thundering herd problem <http://en.wikipedia.org/wiki/Thundering_herd_problem>`_

   To see the distribution of connections to the children (i.e. how
   many times every child succeeded in calling *'accept'* and getting
   a new connection socket) run the following server in the foreground
   and press Ctrl-C when the client is done.

   `server03a.py <https://github.com/rspivak/csdesign/blob/master/server03a.py>`_

   On Linux the connection distribution is uniform. With the following
   client parameters on my Fedora box

   ::

     $ python client.py -i localhost -p 2000 -c 15 -t 100 -b 4096

   this is how the distribution looks like:

   ::

     child 0 : 127 times
     child 1 : 144 times
     child 2 : 138 times
     child 3 : 147 times
     child 4 : 160 times
     child 5 : 161 times
     child 6 : 161 times
     child 7 : 130 times
     child 8 : 181 times
     child 9 : 133 times


Roadmap
-------

- TCP Concurrent Server, One Thread per Client

- TCP Concurrent Server, I/O Multiplexing (poll)

- TCP Concurrent Server, I/O Multiplexing (epoll)

- TCP Preforked Server, Passing Descriptor to Child

- TCP Prethreaded Server

- Documentation for every example


