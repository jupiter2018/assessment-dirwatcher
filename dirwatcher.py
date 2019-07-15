#!/usr/bin/env python2

import sys
import argparse
import os
import logging
import time
import datetime
import signal


exit_flag = False
dir_file_list = {}
mylogger = logging.getLogger(__file__)
mylogger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
# formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
# file_handler = logging.FileHandler('dirwatcher.log')
# file_handler.setFormatter(formatter)
# mylogger.addHandler(file_handler)


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    # mylogger.warn('Received ' + signal.Signals(sig_num).name)
    # log the signal name (the python2 way)
    signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                    if v.startswith('SIG') and not v.startswith('SIG_'))
    mylogger.warn('Received ' + signames[sig_num])
    global exit_flag
    exit_flag = True


def detect_added_files(filename, ext):
    f_name, f_ext = os.path.splitext(filename)
    if f_ext == ext:
        if filename not in dir_file_list.keys():
            dir_file_list[filename] = 0
            mylogger.info("New file added to directory: {}".format(filename))


def detect_removed_files(dirname, ext):
    for curkey in dir_file_list.keys():
        if curkey not in os.listdir(dirname):
            del dir_file_list[curkey]
            mylogger.info("File deleted from directory: {}".format(curkey))


def scan_single_file(dirname, filename, magicword, lastlinenum):
    filepath = os.path.join(dirname, filename)
    with open(filepath, 'r') as myfile:
        file_content = myfile.readlines()
        for num, line in enumerate(file_content[lastlinenum:], lastlinenum+1):
            if magicword in line:
                mylogger.info(
                    "file:{2}:{0} found in line number {1}".format(magicword, num, filename))
    dir_file_list[filename] = len(file_content)


def watch_directory(dirname, ext, magicword, poll):
    
    # print(dir_file_list)
    detect_removed_files(dirname, ext)
    for f in os.listdir(dirname):
        detect_added_files(f, ext)
        lastlinenum = dir_file_list[f]
        # print(dir_file_list)
        scan_single_file(dirname, f, magicword, lastlinenum)


def create_parser():
    """Create a cmd line parser object with 2 argument definitions"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dir', help='Provide a target directory')
    parser.add_argument('--ext', help='extension to filter', default='.txt')
    parser.add_argument('--poll', help='polling time', type=int, default=2)
    parser.add_argument('magicText', help='find the magic text')
    return parser


def main():
    start_time = datetime.datetime.now()
    mylogger.info(
        "\n------------------------"
        "\nStarting Dirwatcher program: {}"
        "\n------------------------".format(start_time.isoformat())
    )
    parser = create_parser()
    args = parser.parse_args()
    print(args)

    if not args:
        parser.print_usage()
        sys.exit(1)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # else:
    #     watch_directory(args.dir, args.ext)
    mylogger.info(
        'Watching {0} for files ending with {1} containing magictext {2}' 
        .format(args.dir, args.ext, args.magicText))
    while not exit_flag:
        try:
            # call my directory watching function..
            watch_directory(args.dir, args.ext, args.magicText, args.poll)
        except OSError as e:
            mylogger.error(str(e))
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            mylogger.error("An error has occurred: {}".format(e))

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(args.poll)

    uptime = datetime.datetime.now() - start_time
    mylogger.info("Stopped Dirwatcher program: {}".format(str(uptime)))


if __name__ == '__main__':
    main()
