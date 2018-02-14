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

    t.get_devices()
    #t.set_termostat_temp(temp="2100", prog="0")
    dev = t.get_device('o-001-101133:happ_smartplug_6634E9BC69E')

    t.set_device(dev['uuid'], state='1')
    alldevs = [
      {
        "uuid": "decc65a4-4f0b-4c26-8c6d-42f60ce38b21",
        "deviceType": "hue_light-LWB004",
        "name": "Table 1",
        "rgbColor": "FFEB99"
      },
      {
        "uuid": "2ae096eb-d9ac-44ad-ae49-2076844de97e",
        "deviceType": "hue_light-LWB004",
        "name": "Table 2",
        "rgbColor": "FFEB99"
      },
      {
        "uuid": "feb5f16d-ca27-4bd5-8f5b-df479b25662a",
        "deviceType": "hue_light-LWB004",
        "name": "Table 3",
        "rgbColor": "FFEB99"
      },
      {
        "uuid": "709e50c1-b3a5-4e9a-bf1f-2e9ef97ab5f7",
        "deviceType": "hue_light-LWB004",
        "name": "Sofa 1",
        "rgbColor": "FFEB99"
      },
      {
        "uuid": "5c538bba-a0d1-49ff-95b9-d16ee8e80cab",
        "deviceType": "hue_light-LWB004",
        "name": "Sofa 2",
        "rgbColor": "FFEB99"
      },
      {
        "uuid": "4804ca5b-022d-4913-aba9-bd6902f62730",
        "deviceType": "hue_light-LWB004",
        "name": "Sofa 3",
        "rgbColor": "FFEB99"
      },
      {
        "uuid": "a8ad58b4-1d73-45ab-8c67-4edd4f787dae",
        "deviceType": "hue_light-LWB004",
        "name": "Sofa 4",
        "rgbColor": "FFEB99"
      },
      {
        "uuid": "e8f7fe29-e7e8-4044-aa55-de9c2a9c49a0",
        "deviceType": "hue_light-LLC020",
        "name": "Brians Light",
        "rgbColor": "D7B19F"
      },
      {
        "uuid": "df799b90-e3c9-47c4-b61e-7de503096c84",
        "deviceType": "hue_light-LLC020",
        "name": "Babette's light",
        "rgbColor": "D1AAFF"
      },
      {
        "uuid": "o-001-101133:happ_smartplug_6634E9BC69E",
        "deviceType": "FGWP011",
        "name": "Boiler1"
      },
      {
        "uuid": "o-001-101133:happ_smartplug_663F228A510",
        "deviceType": "FGWP011",
        "name": "TV"
      }
    ]



    t.set_device('e8f7fe29-e7e8-4044-aa55-de9c2a9c49a0', state='0')
    #t.set_device('df799b90-e3c9-47c4-b61e-7de503096c84', state='0')

    #t.set_device('o-001-101133:happ_smartplug_663F228A510', state='0')

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
