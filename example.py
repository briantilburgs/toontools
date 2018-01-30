#!/usr/bin/env python3

from toontools import Toon
import logging

def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s',)

    session = Toon.load_from_config('toontools/conf/toon.json')


if __name__ == '__main__':
    main()
