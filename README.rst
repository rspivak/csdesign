Simple Examples of Concurrent Server Design in Python
-----------------------------------------------------

The `client.py <https://github.com/rspivak/csdesign/blob/master/client.py>`_ can be used with all the servers.

1. TCP Concurrent Server, One Child per Client (fork)

   `server01.py <https://github.com/rspivak/csdesign/blob/master/server01.py>`_

2. TCP Concurrent Server, I/O Multiplexing (select)

   `server02.py <https://github.com/rspivak/csdesign/blob/master/server02.py>`_


Roadmap
-------

- TCP Concurrent Server, One Thread per Client

- TCP Concurrent Server, I/O Multiplexing (poll)

- TCP Concurrent Server, I/O Multiplexing (epoll)

- TCP Preforked Server

- TCP Prethreaded Server

- Documentation for every example


