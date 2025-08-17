# SIGPIPE Demo

This example shows what happens when writing to a socket that has already received an RST packet.

## Files
- `sigpipe.py`: Demonstrates `SIGPIPE` when writing to a reset socket.

## Usage

First, start the RST server from [rst-packet](../rst-packet/README.md):

```bash
python rstserver.py
```

Then run:

```bash
python sigpipe.py
```

Expected output:

```text
[Errno 104] Connection reset by peer

Traceback (most recent call last):
  File "sigpipe.py", line 43, in <module>
    s.send('hello')
socket.error: [Errno 32] Broken pipe
```

## Reference

- [Broken Pipe and SIGPIPE](https://man7.org/linux/man-pages/man7/signal.7.html)
