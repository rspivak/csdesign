# Self-Pipe Trick

This example shows how to avoid race conditions when handling signals and using `select`.

## Files
- `selsigrace.py`: Demonstrates the race condition.
- `selfpipe.py`: Fixes the problem using the self-pipe trick.

## Concept

If a signal arrives after setting the handler but before calling `select`, the process may block indefinitely. The self-pipe trick avoids this.

## How it works

1. Create a pipe and make both ends nonblocking.  
2. Add the read end of the pipe to the `select` read list.  
3. The signal handler writes a byte to the pipe.  
4. After `select` returns, check if the pipe is readable.  
5. Drain the pipe and handle the signal safely.

## Usage

Start:

```bash
python selsigrace.py
```

Send a signal:

```bash
kill -USR1 <PID>
```

Then try:

```bash
python selfpipe.py
```

It will output "Got signal" and exit cleanly.

## Reference

- [Self-Pipe Trick](http://cr.yp.to/docs/selfpipe.html)
