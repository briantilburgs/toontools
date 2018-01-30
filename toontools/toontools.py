#!/usr/bin/env python

import sys
import argparse
import logging

from ToonAPIv3 import Toon

from pynteractive import *

def draw_usage_chart(gas, elec):

    chart=Chart()
    chart.view()
    gas_x=[]
    gas_y=[]
    for item in gas['days']:
        gas_x.append((int(item['timestamp'])/1000000))
        gas_y.append((int(item['value'])))

    elec_x=[]
    elec_y=[]
    for item in elec['days']:
        elec_x.append(item['timestamp'])
        elec_y.append(item['offPeak'])

    logging.info(gas_x)
    logging.info(gas_y)
    chart.addSeries('Gas used', gas_x, gas_y)
    #chart.addSeries('Electricity used', elec_x, elec_y)
    chart.addSeries('Squirrels killed by humans',
    [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
    [200,240,300,313,317,380,360,320,503,460,510,600,550,500,460,490]) 


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

    t = Toon(authcode, args.username, args.password)
    #t.login()
    agrid = t.get_agreement_id()
    logging.info("AgreementID is: %s" % agrid)
    t.get_status()
    t.get_thermostat_states()
    t.get_thermostat_state_current()
    t.get_thermostat_programs()
    if args.getusage:
        t.get_cons_elec_gas(gas_elec= args.getusage)

    gas  = t.get_cons_elec_gas(gas_elec= 'gas', interval='days')
    elec = t.get_cons_elec_gas(gas_elec= 'electricity', interval='days')
    
    # Future: Draw Chart in VisJS
    #draw_usage_chart(gas, elec)

    return()

if __name__ == '__main__':
    prog = 'python ' + sys.argv[0]
    parser = argparse.ArgumentParser(description='This App Creates an Application Network Profile with all its EPS, Contracts etc')
    parser = argparse.ArgumentParser(prog, usage='%(prog)s [options]')
    parser.add_argument("--username",     required=True, help='''toon@username.nl''')
    parser.add_argument("--password",     required=True, help='''T00nP@ssword''')
    parser.add_argument("--authcode",     required=False, help='''cfQEqOGA''')
    parser.add_argument("--getusage",     required=False, help='''gas/ elctricity''')
    parser.add_argument("--exportformat", required=False, help='''excel/ visjs''')
    parser.add_argument("--from",         required=False, help='''2017-01-01''')
    parser.add_argument("--to",           required=False, help='''2017-12-31''')
    parser.add_argument("--DEBUG",    action='store_true')
    args = parser.parse_args()
    main(args)
