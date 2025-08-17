# Simple Examples of Concurrent Server Design in Python

This repository contains **minimal, educational examples** of different
concurrent server design patterns in Python. Each server demonstrates a
classic approach used in Unix/Linux systems programming: forking,
multiplexing, preforking, and more.

The goal: keep the code small and focused so you can **learn the concepts**
without distractions.

---

## Client

The test client works with all servers:

[client.py](https://github.com/rspivak/csdesign/blob/master/client.py)

---

## Server Examples

| Example | Technique | Notes |
|---------|-----------|-------|
| [server01.py](https://github.com/rspivak/csdesign/blob/master/server01.py) | One child per client (`fork`) | Simple, but resource-heavy with many clients |
| [server02.py](https://github.com/rspivak/csdesign/blob/master/server02.py) | I/O multiplexing (`select`) | Efficient single-process model |
| [server03.py](https://github.com/rspivak/csdesign/blob/master/server03.py) | Preforked, children call `accept` | Demonstrates the **Thundering Herd** problem |
| [server03a.py](https://github.com/rspivak/csdesign/blob/master/server03a.py) | Preforked, connection distribution demo | Shows how Linux distributes connections |
| [server04.py](https://github.com/rspivak/csdesign/blob/master/server04.py) | Parent accepts, passes socket to child | Avoids **Thundering Herd**; requires Python 3.3+ |

---

## Quickstart

Run a server in one terminal:

```bash
python server01.py
