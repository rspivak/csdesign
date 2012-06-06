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
import sys
import errno
import socket
import optparse


def request(host, port, child_num, con_num, bytes):
    # spawn child_num children processes
    for cnum in range(child_num):

        pid = os.fork()
        if pid == 0: # child

            for i in range(con_num):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                sock.sendall(str(bytes))

                data = sock.recv(bytes)
                if len(data) != bytes:
                    raise Exception('Server returned only %d bytes' % len(data))

                sock.close() # TIME_WAIT state on the client

            print 'Child %d is done' % cnum
            os._exit(0)

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


def main():
    parser = optparse.OptionParser()
    parser.add_option(
        '-i', '--host', dest='host', help='Hostname or IP address')

    parser.add_option('-p', '--port', dest='port', type='int', help='Port')

    parser.add_option(
        '-c', '--child-num', dest='childnum', type='int', default=5,
        help='Number of children to spawn. Default is 5'
        )
    parser.add_option(
        '-t', '--con-num', dest='connum', type='int', default=500,
        help='Number of connections to establish. Default is 5'
        )
    parser.add_option(
        '-b', '--bytes', dest='bytes', type='int', default=3000,
        help='Number of bytes to request. Default is 3000'
        )

    options, args = parser.parse_args()

    if not (options.host and options.port):
        parser.print_help()
        sys.exit(1)

    request(options.host, options.port,
            options.childnum, options.connum, options.bytes)

if __name__ == '__main__':
    main()
