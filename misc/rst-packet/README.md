# RST Packet Generation

This example demonstrates how to send a TCP RST packet using the `SO_LINGER` socket option.

## Files
- `rstserver.py`: Iterative server that binds to `localhost:2000` and sends an RST packet after accepting a connection.

## Usage

Start the server:

```bash
python rstserver.py
```

When a client connects, the server immediately sends an RST packet and closes.

## Reference

- [Linux `SO_LINGER` option](https://man7.org/linux/man-pages/man7/socket.7.html)
