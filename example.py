#!/usr/bin/env python3

from toontools import Toon
import logging

def main():
    # logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s',)

    session = Toon.load_from_config('toontools/conf/toon.json')

    print('Retrieving thermostat states')
    print(session.get_thermostat_states())

    print('\nRetrieving current status')
    print(session.get_status())

    print('\nRetrieving thermostat states')
    print(session.get_thermostat_states())

    print('\nRetrieving current thermostat state')
    print(session.get_thermostat_state_current())

    print('\nRetriving thermostat programs')
    print(session.get_thermostat_programs())

    print('\nRetrieving current thermostat temp')
    print(session.get_thermostat_current_temp())

    print('\nRetrieving electricity and gas')
    print(session.get_cons_elec_gas())



if __name__ == '__main__':
    main()
