#!/usr/bin/env python3

import sys
import argparse
import logging
import time
import datetime
import xlsxwriter

from ToonAPIv3 import Toon

def write_data_to_excel():
    # Create new Excel ad write data to tabs
    pass

def msec_to_time(msec):
    '''Convert miliseconds to Python datetime object - Date & Time'''

    date_time = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(msec/1000.0)
    )
    return(date_time)

def msec_to_day(msec):
    '''Convert miliseconds to Python datetime object - Date Only'''
    timepattern = '%Y-%m-%d'

    date_time = time.strftime(
        timepattern, time.localtime(msec/1000.0)
    )
    return(date_time)

def day_to_msec(data_time):
    '''Convert Python datetime object to miliseconds - Date Only'''
    timepattern = '%Y-%m-%d'
    msec = int(
        time.mktime(
            time.strptime(
                data_time, timepattern)
            )
        ) * 1000
    return(msec)

def get_usage_from_to(t, interval='hours',
                          from_time="2018-01-01",
                          to_time=datetime.datetime.now().strftime("%Y-%m-%d"),
                          gas_elec='both'):

    from_time_msec = day_to_msec(from_time)
    to_time_msec = day_to_msec(to_time)
    returndata = { 
        'gas':         {'hours': [], 'days': [], 'weeks': [], 'months': [], 'years': []},
        'electricity': {'hours': [], 'days': [], 'weeks': [], 'months': [], 'years': []}
    }

    get_ge = []

    if gas_elec == 'both':
        get_ge.append('gas')
        get_ge.append('electricity')
    else:
        get_ge.append(gas_elec)

    if args.getusageinter == 'all':
        usageinter = ['hours', 'days', 'weeks', 'months', 'years']
    else:
        usageinter = [ args.getusageinter ]

    logging.info('Getting data from: {}({}) till: {}({})'.format(from_time, from_time_msec, to_time, to_time_msec))

    for ge in get_ge:
        for uinter in usageinter:
            response = t.get_cons_elec_gas(interval=uinter,
                                             from_time=from_time_msec,
                                             to_time=to_time_msec,
                                             gas_elec=ge)
            returndata[ge][uinter] = response[uinter]

    return returndata

def write_to_new_sheet(wb, data, ge, interv):
    logging.debug('Write to Excel: {}'.format(data))
    worksheet = wb.add_worksheet('{}_{}'.format(ge, interv))
    row = 0
    col = 0

    for sample in data:
        if row == 0:
            headers = list(sample.keys())
            logging.debug("Alle Keys registered for row0 {}".format(headers))
            for key in headers:
                worksheet.write(row, col , key)
                col+=1
            row+=1
            col=0
        for key in headers:
            worksheet.write(row, col , sample[key])
            col+=1
        col=0

        tijd = msec_to_time(sample['timestamp'])

        worksheet.write(row, col,     tijd)

        row += 1


def write_to_xlsx(data, namedata):

    # Create a workbook and add a worksheet.
    filename = 'Toon-Usage_' + namedata + '_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.xlsx'
    wb = xlsxwriter.Workbook(filename)
    logging.info("Writing into File: {}".format(filename))
    nrsht = 0
    for gas_elc in data:
        for interv in data[gas_elc]:
            logging.debug('Write to Excel: {} {}'.format(interv, data[gas_elc][interv]))
            if data[gas_elc][interv] != []:
                write_to_new_sheet(wb, data[gas_elc][interv], gas_elc, interv)
                nrsht += 1
    logging.info("{} sheets added to {}".format(nrsht, filename))


    wb.close()
    pass


def setlogging(args):
    if args.DEBUG:
        print("Set Logging to DEBUG")
        logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s',)
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s',)

def main(args):
    setlogging(args)

    t = Toon.load_from_config('conf/toon.json')
    nu = datetime.datetime.now()
    print(nu.year)
    print(nu.strftime("%Y-%m-%d"))

    t.get_status()
    t.get_thermostat_states()
    t.get_thermostat_state_current()
    t.get_thermostat_programs()
    t.get_thermostat_current_temp()
    
    usagedict = get_usage_from_to(t, 
                                  interval=args.getusageinter,
                                  from_time=args.getusagestart,
                                  to_time=args.getusagestop,
                                  gas_elec=args.getusage)
    
    write_to_xlsx(usagedict, t._agreement_id)


    return()

if __name__ == '__main__':
    prog = 'python ' + sys.argv[0]
    parser = argparse.ArgumentParser(description='This App Creates an Application Network Profile with all its EPS, Contracts etc')
    parser = argparse.ArgumentParser(prog, usage='%(prog)s [options]')
    parser.add_argument("--getusage",     required=False, default='both', help='''gas/ electricity/ both''')
    parser.add_argument("--getusageinter",required=False, default="hours", help='''hours/ days/ weeks/ months/ year/ all''')
    parser.add_argument("--getusagestart",required=False, default="2018-01-01", help='''2018-01-01''')
    parser.add_argument("--getusagestop", required=False, default=datetime.datetime.now().strftime("%Y-%m-%d"), help='''2018-01-01''')
    parser.add_argument("--exportformat", required=False, default="excel", help='''excel/ visjs (Future feature)''')
    parser.add_argument("--DEBUG",    action='store_true')
    args = parser.parse_args()
    main(args)
