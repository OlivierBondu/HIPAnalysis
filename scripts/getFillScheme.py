#!/bin/env python
import argparse
import json
import pprint
import StringIO
import csv
import urllib2

def get_options():
    parser = argparse.ArgumentParser(description='Return the filled bunches for a given run')
    parser.add_argument('--run', action='store', dest='run',
                        default=296173,
                        help='Run for which the BX has to be fetched')
    options = parser.parse_args()
    return options

def get_bucket_list(reader):
    l = []
    # The bucket size is 2.5ns, so that means ~36k buckets (35640?)
    for irow, row in enumerate(reader):
        # skip header
        if ('HEAD ON' in ' '.join(row)) or ('bucket' in ' '.join(row)):
            continue
        # keep only buckets colliding in IP5
        # header is:
        # B1 bucket number    IP1 IP2 IP5 IP8
        if row[3] is not '-':
#            print '\t'.join(row)
            l.append(int(row[3]))
    return l

def get_fill_number(run):
    # FIXME
    fill = 5750
    return fill

def main(run):
    # Get the fill number
    n_fill = get_fill_number(run)
    # Get the fill scheme and write it to file
    fill_scheme_file = 'bunch_scheme_fill_%i.json' % n_fill
    LPC_API = 'https://lpc.web.cern.ch/cgi-bin/schemeInfo.py'
    QUERY = '?fill=%i&fmt=json' % n_fill
    # curl -o fill_5750.json https://lpc.web.cern.ch/cgi-bin/schemeInfo.py\?fill\=5750\&fmt\=json
    request = urllib2.Request('%s%s' % (LPC_API, QUERY))
    response = urllib2.urlopen(request)
    with open(fill_scheme_file, 'w') as f:
        f.write(response.read())
    d = None
    scheme = []
    n_colliding_bx = None
    with open(fill_scheme_file, 'r') as f:
        d = json.load(f)
        # content similar to https://cmswbm.cern.ch/FillPatterns/25ns_601b_589_522_540_48bpi15inj_bcms.txt
        # taken from https://lpc.web.cern.ch/cgi-bin/schemeInfo.py?fill=5750&fmt=json
        text = d['fills']['%i' % n_fill]['csv']
        text = text.split('\n\n') # split by paragraph
        text = [t for t in text if 'HEAD ON' in t]
        pseudofile_b1 = StringIO.StringIO(text[0])
        reader = csv.reader(text[0].split('\n'), delimiter=',')
        l_b1 = get_bucket_list(reader)
        n_colliding_bx = len(l_b1)
        l_b1 = [x / 10 + 1 for x in l_b1]
        # does the job!
        # thanks to https://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list
        from operator import itemgetter
        from itertools import groupby
        data = l_b1
        for k, g in groupby(enumerate(data), lambda (i,x):i-x):
            scheme.append(map(itemgetter(1), g))
    # print final result
    n_trains = len(scheme)
    print 'number of colliding bunches:', n_colliding_bx
    print 'number of trains:', n_trains
    for itrain, train in enumerate(scheme):
        print 'train %i, bx %i-%i' % (itrain, train[0],train[-1])
    # define edges:
    n_edges = 0
    edges = []
    if all(x > 0 for x in scheme[0]):
        n_edges += 1
        edges.append(0)
    for train in scheme:
        n_edges += 2
        edges.append(train[0])
        edges.append(train[-1] + 1)
    if all(x < 3563 for x in scheme[-1]):
        n_edges += 1
        edges.append(3563)
    print 'n_edges = %i' % n_edges
    print 'edges:', edges


if __name__ == '__main__':
    options = get_options()
    run = options.run
    main(run)

