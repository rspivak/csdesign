###############################################################################
#
# Copyright (c) 2012 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import os
import mmap
import errno
import signal
import socket
import optparse

BACKLOG = 5

# stores pids of all preforked children
PIDS = []

# anonymous memory-mapped file that holds
# counters for child processes to count how many times
# they called 'accept' and got new connection socket
MAP = None


def handle(sock):
    # read a line that tells us how many bytes to write back
    bytes = int(sock.recv(1024))
    # get our random bytes
    data = os.urandom(bytes)

    print 'Got request to send %d bytes. Sending them all...' % bytes
    # send them all
    sock.sendall(data)


def child_loop(index, listen_sock):
    """Main child loop."""
    while True:
        # block waiting for connection to handle
        try:
            conn, client_address = listen_sock.accept()
        except IOError as e:
            code, msg = e.args
            if code == errno.EINTR:
                continue
            else:
                raise

        # the process woke up and got socket connection - update the counter
        inc_counter(index)

        # handle request
        handle(conn)

        # close handled socket connection and off to handle another request
        conn.close()


def create_child(index, listen_sock):
    pid = os.fork()
    if pid > 0: # parent
        return pid

    print 'Child started with PID: %s' % os.getpid()
    # child never returns
    try:
        child_loop(index, listen_sock)
    except KeyboardInterrupt:
        pass


def _exit_handler():
    # terminate all children
    for pid in PIDS:
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass

    # wait for all children to finish
    while True:
        try:
            pid, status = os.wait()
        except OSError as e:
            if e.errno == errno.ECHILD:
                break
            else:
                raise

        if pid == 0:
            break


def _cleanup(signum, frame):
    """SIGTERM signal handler"""
    _exit_handler()
    os._exit(0)


def create_array(childnum):
    """Creates anonymous memory mapped file of the size `childnum`"""
    map = mmap.mmap(-1, childnum) # anonymous mapped file, numchild bytes
    map.seek(0)
    array = bytearray(childnum) # array of zero bytes
    map.write(str(array))
    return map


def inc_counter(index):
    map = MAP
    map.seek(0)
    array = bytearray(map.read(1024)) # stats for max 1024 preforked children
    array[index] += 1
    map.seek(0)
    map.write(str(array))

def print_stats():
    map = MAP
    map.seek(0)
    array = bytearray(map.read(len(PIDS)))
    print
    for index, val in enumerate(array):
        print 'child %-2s: %d times' % (index, val)
    print


def serve_forever(host, port, childnum):
    # create, bind, listen
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # re-use the port
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    listen_sock.bind((host, port))
    listen_sock.listen(BACKLOG)

    print 'Listening on port %d ...' % port

    global MAP
    MAP = create_array(childnum)

    # prefork children
    global PIDS
    PIDS = [create_child(index, listen_sock) for index in range(childnum)]

    # setup SIGTERM handler - in case the parent is killed
    signal.signal(signal.SIGTERM, _cleanup)

    # parent never calls 'accept' - children do all the work
    # all parent does is sleeping :)
    try:
        signal.pause()
    except KeyboardInterrupt:
        _exit_handler()
        print_stats()


def main():
    parser = optparse.OptionParser()
    parser.add_option(
        '-i', '--host', dest='host', default='0.0.0.0',
        help='Hostname or IP address. Default is 0.0.0.0'
        )

    parser.add_option(
        '-p', '--port', dest='port', type='int', default=2000,
        help='Port. Default is 2000')

    parser.add_option(
        '-n', '--child-num', dest='childnum', type='int', default=10,
        help='Number of children to prefork. Default is 10')

    options, args = parser.parse_args()

    serve_forever(options.host, options.port, options.childnum)

if __name__ == '__main__':
    main()
