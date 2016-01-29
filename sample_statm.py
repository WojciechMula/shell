import os
import sys
import optparse
import time
import errno


class StatmSampler:

    def __init__(self, options):

        self.options = options
        self.pid    = options.pid
        self.delay  = options.delay
        self.output = None

        self.path   = '/proc/%s/statm' % self.pid
        self.count  = 0
        self.timestamp_fmt = '%Y-%m-%dT%H:%M:%S'


    def run(self):
        if not os.path.exists(self.path):
            print "program %s is not running" % self.pid
            return
            
        print 'sampling PID %s every %0.2fs; output is %s' % (self.pid, self.delay, self.options.output_name)
        with open(self.options.output_name, 'a') as self.output:
            self.__do_run()


    def __do_run(self):
        while True:
            try:
                if not self.__take_snapshot():
                    break

                time.sleep(self.delay)
            except KeyboardInterrupt:
                break

        print "%d sample(s) saved in %s\n" % (self.count, self.options.output_name)


    def __take_snapshot(self):

        try:
            with open(self.path, 'r') as f:
                stat = f.read().rstrip()
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            else:
                raise e

        timestamp = time.strftime(self.timestamp_fmt)

        self.output.write('%s %s\n' % (timestamp, stat))
        self.output.flush()
        self.count += 1
        return True


class ProgramError:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

 
def get_options(argv):
    parser = optparse.OptionParser(usage="""Usage: %prog [options]""")

    parser.add_option(
        '-p', '--pid', dest='pid',
        help='PID to sample'
    )

    parser.add_option(
        '-o', '--output', dest='output_name',
        help='Name of ouput file (default: pid.statm)'
    )

    parser.add_option(
        '-d', '--delay', dest='delay', default=1000, type='int',
        help='Sampling frequency in milliseconds (default 1000ms)'
    )

    options, _ = parser.parse_args(argv)
    options.delay = options.delay / 1000.0

    if options.pid is None:
        raise ProgramError('Option -p is required')

    if options.output_name is None:
        options.output_name = '%s.statm' % options.pid

    if options.delay < 0.01:
        raise ProgramError('Delay value must not be lass than 10ms')

    return options


def main():
    try:
        options = get_options(sys.argv[1:])
    except ProgramError as err:
        print err
        return 1

    sampler = StatmSampler(options)
    sampler.run()

    return 0

if __name__ == '__main__':
    sys.exit(main())
