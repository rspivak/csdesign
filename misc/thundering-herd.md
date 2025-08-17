# The Thundering Herd Problem

When a preforked server is running, each child process is blocked on
the same listening socket, waiting in a call to `accept`.

When a new connection arrives:

- **All children wake up.**
- The first one scheduled gets the connection and returns from `accept`.
- The rest go back to sleep, having woken up for nothing.

This repeated "false wakeup" is called the **Thundering Herd problem**.

---

## Example

Run the preforked server:

```bash
python server03a.py
```

Then run the client:

```bash
python client.py -i localhost -p 2000 -c 15 -t 100 -b 4096
```

Press `Ctrl-C` after it finishes.

On Linux, you’ll see the connections distributed fairly evenly across
children. Example run on Fedora:

```
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
```

---

## Why it matters

- The herd problem causes **wasted wakeups**, which waste CPU cycles.
- In heavy-load systems, this inefficiency can matter a lot.
- Solutions:
  - Parent handles `accept` and passes the descriptor (see `server04.py`).
  - Kernel-level load balancing (some OSes optimize this).

---

**References:**
- [Thundering Herd Problem (Wikipedia)](https://en.wikipedia.org/wiki/Thundering_herd_problem)
