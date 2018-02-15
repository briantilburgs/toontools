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

    logging.info(t.get_devices())

    dev = t.get_device('o-001-101133:happ_smartplug_6634E9BC69E')
    
    # Turn on device
    t.set_device(dev['uuid'], state='1')
    
    # Or turn off
    t.set_device(dev['uuid'], state='0')

    t.get_devices()

    return()

if __name__ == '__main__':
    prog = 'python ' + sys.argv[0]
    parser = argparse.ArgumentParser(description='This App Creates an Application Network Profile with all its EPS, Contracts etc')
    parser = argparse.ArgumentParser(prog, usage='%(prog)s [options]')
    parser.add_argument("--getusage",     required=False, default='both', help='''gas/ electricity/ both''')
    parser.add_argument("--DEBUG",    action='store_true')
    args = parser.parse_args()
    main(args)
