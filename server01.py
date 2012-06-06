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

"""
TCP Concurrent Server, One Child per Client (fork).

Multiple server processes to handle any number of clients.
"""

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import os
import sys
import errno
import signal
import socket
import optparse

BACKLOG = 5


def _reap_children(signum, frame):
    """Collect zombie children."""
    while True:
        try:
            # wait for all children, do not block
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0: # no more zombies
                break
        except:
            # Usually this would be OSError exception
            # with 'errno' attribute set to errno.ECHILD
            # which means there are no more children
            break


def handle(sock):
    # read a line that tells us how many bytes to write
    bytes = int(sock.recv(1024))
    # get our random bytes
    data = os.urandom(bytes)

    print 'Got request to send %d bytes. Sending them all...' % bytes
    # send them all
    sock.sendall(data)


def serve_forever(host, port):
    # setup SIGCHLD handler
    signal.signal(signal.SIGCHLD, _reap_children)

    # create, bind. listen
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # re-use the port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen(BACKLOG)

    print 'Listening on port %d ...' % port

    # spawn a new child process for every request
    while True:
        try:
            conn, client_address = sock.accept()
        except IOError as e:
            code, msg = e.args
            if code == errno.EINTR:
                continue
            else:
                raise

        pid = os.fork()
        if pid == 0: # child
            # close listening socket
            sock.close()
            handle(conn)
            os._exit(0)

        # parent - close connected socket
        conn.close()


def main():
    parser = optparse.OptionParser()
    parser.add_option(
        '-i', '--host', dest='host', default='0.0.0.0',
        help='Hostname or IP address. Default is 0.0.0.0'
        )

    parser.add_option(
        '-p', '--port', dest='port', type='int', default=2000,
        help='Port. Default is 2000')

    options, args = parser.parse_args()

    serve_forever(options.host, options.port)

if __name__ == '__main__':
    main()
