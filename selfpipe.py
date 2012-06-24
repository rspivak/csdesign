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
Demonstrates SELF-PIPE Trick that is used to
avoid race condtions when waiting for signals and calling select() on
a set of descriptors.
"""

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import os
import sys
import fcntl
import time
import errno
import select
import signal

# read, write pipe descriptors
RD, WD = None, None


def handler(signum, frame):
    try:
        os.write(WD, 'x')
    except OSError as e:
        if e.errno != errno.EAGAIN:
            print 'Signal handler write error'
            os._exit(1)


def main():
    print 'PID: %s' % os.getpid()

    # 1. Create a pipe and make both ends nonblocking
    global RD, WD
    RD, WD = os.pipe()

    flags = fcntl.fcntl(RD, fcntl.F_GETFL)
    fcntl.fcntl(RD, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    flags = fcntl.fcntl(WD, fcntl.F_GETFL)
    fcntl.fcntl(WD, fcntl.F_SETFL, flags | os.O_NONBLOCK)


    # 2. Add read end of the pipe to the read list of descriptors
    # read, write, exception lists with descriptors to poll
    rlist, wlist, elist = [RD], [], []

    # 3. Install signal handler for USR1 signal
    signal.signal(signal.SIGUSR1, handler)

    # A racing can happen at this point if the signal arrives before
    # the call to 'select' - but we're ready for it, bring it on!

    # call 'select' in loop - this way we determine the signal arrival
    # through examinination of the read end of the pipe (RD descriptor)
    while True:
        try:
            readables, writables, exceptions = select.select(
                rlist, wlist, elist)
        except select.error as e:
            code, msg = e.args
            # restart if interrupted by a signal
            if code == errno.EINTR:
                continue
            else:
                raise
        else:
            # we have result - break the loop
            break

    # 4. Check if our pipe's read end descriptor is in the result set
    if RD in readables:
        print 'Got signal'
        # 5. Read all the bytes, because multiple
        # signal may have arrived
        while True:
            try:
                os.read(RD, 1)
            except OSError as e:
                if e.errno == errno.EAGAIN:
                    # the pipe is drained - exit
                    break
                else:
                    raise
    else:
        print 'Something unexpected happened'


if __name__ == '__main__':
    main()

