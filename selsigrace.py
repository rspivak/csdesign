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
Illustrates a problem with a race condition that might happen if a process
needs to monitor several descriptors for I/O and wait for the delivery of
a signal.
"""

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import os
import sys
import time
import errno
import select
import signal

GOT_SIGNAL = False


def handler(signum, frame):
    global GOT_SIGNAL
    GOT_SIGNAL = True


def main():
    print 'PID: %s' % os.getpid()

    signal.signal(signal.SIGUSR1, handler)

    # read, write, exception lists with descriptors to poll
    rlist, wlist, elist = [sys.stdin.fileno()], [], []

    print 'Sleep for 10 secs'
    time.sleep(10)
    print 'Wake up and block in "select"'

    #
    # Nasty racing can happen at this point if the signal arrives before
    # the call to 'select' - the call won't be interrupted and 'select'
    # will block
    #

    # block in select
    try:
        readables, writables, exceptions = select.select(rlist, wlist, elist)
    except select.error as e:
        code, msg = e.args
        if code == errno.EINTR:
            if GOT_SIGNAL:
                print 'Got signal'
        else:
            raise


if __name__ == '__main__':
    main()
