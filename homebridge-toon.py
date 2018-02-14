#!/usr/bin/env python3

from toontools import Toon
import sys
import argparse
import logging

def setlogging(args):
    if args.DEBUG:
        print("Set Logging to DEBUG")
        logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s',)
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s',)

def main(args):
    setlogging(args)

    t = Toon.load_from_config('conf/toon.json')

    t.set_termostat_states()
    t.set_termostat_temp(temp=args.settemp, state=args.state, prog=args.prog)


    return()

if __name__ == '__main__':
    prog = 'python ' + sys.argv[0]
    parser = argparse.ArgumentParser(description='This App Creates an Application Network Profile with all its EPS, Contracts etc')
    parser = argparse.ArgumentParser(prog, usage='%(prog)s [options]')
    parser.add_argument("--settemp",     required=False, default='2100', help='''Geef Temp (*100)''')
    parser.add_argument("--prog",     required=True, default='0', help='''Geef state''')
    parser.add_argument("--state",     required=True, default='0', help='''Prog ON/Off''')
    parser.add_argument("--DEBUG",    action='store_true')
    args = parser.parse_args()
    main(args)
