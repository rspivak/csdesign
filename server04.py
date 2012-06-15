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
TCP Preforked Server, Passing Descriptor to Child

Pool of child processes handle client requests.
"""

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'


import os
import sys
import errno
import struct
import select
import socket
import optparse

BACKLOG = 5

# keep track of children status (busy or free)
CHILDREN = []
# child status
FREE, BUSY = 0, 1

FMT = '<i'


def write_fd(sock, fd):
    """Write a descriptor to the socket."""
    data = struct.pack(FMT, fd)
    return sock.sendmsg([b'1'], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, data)])


def read_fd(sock):
    """Read a descriptor from the socket."""
    data_size, ancdata_size = 1, socket.CMSG_LEN(struct.calcsize(FMT))

    # read the data and ancillary data from the UNIX domain socket
    # we're interested only in ancillary data that contains descriptor
    msg, ancdata, flags, addr = sock.recvmsg(data_size, ancdata_size)

    cmsg_level, cmsg_type, cmsg_data  = ancdata[0]
    if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
        fd = struct.unpack(FMT, cmsg_data)[0]
        return fd


def handle(sock):
    # read a line that tells us how many bytes to write back
    bytes_num = int(sock.recv(1024))
    data = b'*' * bytes_num

    print('Got request to send %s bytes. Sending them all...' % bytes_num)
    # send them all
    sock.sendall(data)


def child_loop(index, parent_pipe):
    """Main child loop."""
    while True:
        # block waiting for a descriptor from the parent
        fd = read_fd(parent_pipe)

        # create a socket object from the desriptor passed by the parent.
        # this socket represents connection to a client
        conn = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)

        handle(conn)

        # close handled socket connection and off to handle another request
        conn.close()
        os.close(fd)

        # signal to the parent that we're free to handle another request
        parent_pipe.send(b'1')


def create_child(index, listen_sock):
    # create an unnamed pair of TCP connected sockets in UNIX domain.
    # descriptors will be passed through these sockets
    child_pipe, parent_pipe = socket.socketpair()

    pid = os.fork()
    if pid > 0: # parent
        CHILDREN.append({'status': FREE, 'pipe': child_pipe, 'pid': pid})
        print('Starting child with PID: %s' % pid)
        # close unused descriptor
        parent_pipe.close()
        return pid

    # this is child

    # close unused copies of descriptors
    child_pipe.close()
    listen_sock.close()

    # child never returns
    child_loop(index, parent_pipe)


def serve_forever(host, port, childnum):
    # create, bind. listen
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # re-use the port
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # put listening socket into non-blocking mode
    listen_sock.setblocking(0)

    listen_sock.bind((host, port))
    listen_sock.listen(BACKLOG)

    print('Listening on port %d ...' % port)

    # read, write, exception lists with sockets to poll
    main_rlist, wlist, elist = [listen_sock], [], []

    # prefork children
    for index in range(childnum):
        create_child(index, listen_sock)
        # watch the socket
        main_rlist.append(CHILDREN[index]['pipe'])

    FREE_CHILD_COUNT = childnum

    while True:
        # read list with sockets to poll
        rlist = main_rlist.copy()

        # if we don't have a free child, stop accepting connections
        # (although the kernel will still be queueing up new connections
        # because of the BACKLOG)
        if FREE_CHILD_COUNT == 0:
            rlist.remove(listen_sock)

        # block in select
        readables, writables, exceptions = select.select(rlist, wlist, elist)

        if listen_sock in readables: # new client connection, we can accept now
            try:
                conn, client_address = listen_sock.accept()
            except IOError as e:
                code, msg = e.args
                if code == errno.EINTR:
                    continue
                else:
                    raise

            # find a free child to pass the connection to
            for child in CHILDREN:
                if child['status'] == FREE: # free
                    # mark as busy
                    child['status'] = BUSY

                    # pass the connection's descriptor to the child
                    write_fd(child['pipe'], conn.fileno())
                    # server doesn't need this connection any more
                    conn.close()

                    FREE_CHILD_COUNT -= 1
                    break
            else:
                # this shouldn't happen
                raise Exception('No free child found')

        # find newly-available children
        for child in CHILDREN:
            child_pipe = child['pipe']
            if child_pipe in readables:
                data = child_pipe.recv(1)
                if not data:
                    # child terminated
                    raise Exception('Child terminated unexpectedly')
                child['status'] = FREE # free
                FREE_CHILD_COUNT += 1


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
