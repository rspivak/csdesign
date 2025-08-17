# Simple Examples of Concurrent Server Design in Python

This repository contains **minimal, educational examples** of different
concurrent server design patterns in Python. Each server demonstrates a
classic approach used in Unix/Linux systems programming: forking,
multiplexing, preforking, and more.

The goal: keep the code small and focused so you can **learn the concepts**
without distractions.


## Client

The test client works with all servers:

[client.py](./client.py)

---

## Server Examples

| Example | Technique | Notes |
|---------|-----------|-------|
| [server01.py](./server01.py) | One child per client (`fork`) | Simple, but resource-heavy with many clients |
| [server02.py](./server02.py) | I/O multiplexing (`select`) | Efficient single-process model |
| [server03.py](./server03.py) | Preforked, children call `accept` | Demonstrates the **Thundering Herd** problem |
| [server03a.py](./server03a.py) | Preforked, connection distribution demo | Shows how Linux distributes connections |
| [server04.py](./server04.py) | Parent accepts, passes socket to child | Avoids **Thundering Herd**; requires Python 3.3+ |

---

## Quickstart

Run a server in one terminal:

```bash
python server01.py
```

Run the client in another:

```bash
python client.py -i localhost -p 2000 -c 5 -t 10 -b 1024
```

---

## Miscellaneous Examples

Extra socket programming tricks and demos are available in the `misc/` folder:

- [RST Packet Generation](./misc/rst-packet/README.md)  
  Demonstrates how to send TCP RST packets using `SO_LINGER`.

- [SIGPIPE Demo](./misc/sigpipe/README.md)  
  Shows what happens when writing to a reset socket.

- [Self-Pipe Trick](./misc/self-pipe/README.md)  
  Classic technique to avoid race conditions with `select`.

- [Sendfile Optimization](./misc/sendfile/README.md)  
  Efficient file transfers using the `sendfile(2)` system call.

---

## Roadmap

- [x] TCP Concurrent Server, One Child per Client  
- [x] TCP Concurrent Server, I/O Multiplexing (select)  
- [x] TCP Preforked Server, Children Call `accept`  
- [x] TCP Preforked Server, Descriptor Passing  
- [ ] TCP Concurrent Server, One Thread per Client  
- [ ] TCP Concurrent Server, I/O Multiplexing (poll)  
- [ ] TCP Concurrent Server, I/O Multiplexing (epoll)  
- [ ] TCP Prethreaded Server  
- [ ] TCP_CORK socket option examples  
- [ ] Documentation for every example  

---

## Acknowledgments

- *Unix Network Programming, Volume 1: The Sockets Networking API
  (3rd Edition)* by W. Richard Stevens, Bill Fenner, Andrew M. Rudoff  
  The classic. Many techniques here are drawn from this book.

- *The Linux Programming Interface* by Michael Kerrisk  
  Another excellent reference.