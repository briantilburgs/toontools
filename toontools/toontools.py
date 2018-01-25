#!/usr/bin/env python

import sys
import argparse
import logging

from Toon import Toon


def setlogging(args):
    if args.DEBUG:
        print("Set Logging to DEBUG")
        logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s',)
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s',)

def main(args):
    setlogging(args)
    try:
        authcode = args.authcode
    except:
        authcode = 0
    t = Toon(authcode)
    #t.login()
    #agrid = t.get_agreement_id()
    #logging.info("AgreementID is: %s" % agrid)
    #t.get_status()

    return()

if __name__ == '__main__':
    prog = 'python ' + sys.argv[0]
    parser = argparse.ArgumentParser(description='This App Creates an Application Network Profile with all its EPS, Contracts etc')
    parser = argparse.ArgumentParser(prog, usage='%(prog)s [options]')
    parser.add_argument("--authcode",     required=False, help='''cfQEqOGA''')
    parser.add_argument("--getusage",     required=False, help='''gas/ elctricity''')
    parser.add_argument("--exportformat", required=False, help='''excel/ visjs''')
    parser.add_argument("--from",         required=False, help='''2017-01-01''')
    parser.add_argument("--to",           required=False, help='''2017-12-31''')
    parser.add_argument("--DEBUG",    action='store_true')
    args = parser.parse_args()
    main(args)
    


