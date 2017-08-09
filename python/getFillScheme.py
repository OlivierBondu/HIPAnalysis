#!/bin/env python
import argparse
import json
import pprint
import StringIO
import csv
import urllib2
import subprocess
import os
import CalibTracker.HIPAnalysis.utils as utils


def get_options():
    parser = argparse.ArgumentParser(description='Return the filled bunches for a given run')
    parser.add_argument('--run', action='store', dest='run', default=[296173], nargs='+', type=int,
                        help='Run for which the BX has to be fetched')
    parser.add_argument('-n', '--username', dest='username', help='Remote lxplus username (local username by default)')
    options = parser.parse_args()
    if options.username is None:
        import pwd, os
        options.username = pwd.getpwuid(os.getuid()).pw_name
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


def getFillScheme(lhcfill):
    # Get the fill scheme and write it to file
    LPC_API = 'https://lpc.web.cern.ch/cgi-bin/schemeInfo.py'
    QUERY = '?fill=%i&fmt=json' % lhcfill
    # curl -o fill_5750.json https://lpc.web.cern.ch/cgi-bin/schemeInfo.py\?fill\=5750\&fmt\=json
    print 'Getting fill scheme from LPC'
    request = urllib2.Request('%s%s' % (LPC_API, QUERY))
    response = urllib2.urlopen(request)
    scheme = []
    bx_scheme_name = None
    d = json.loads(response.read())
    bx_scheme_name = d['fills']['%i' % lhcfill]['name']
    # content similar to https://cmswbm.cern.ch/FillPatterns/25ns_601b_589_522_540_48bpi15inj_bcms.txt
    # taken from https://lpc.web.cern.ch/cgi-bin/schemeInfo.py?fill=5750&fmt=json
    text = d['fills']['%i' % lhcfill]['csv']
    text = text.split('\n\n') # split by paragraph
    text = [t for t in text if 'HEAD ON' in t]
    pseudofile_b1 = StringIO.StringIO(text[0])
    reader = csv.reader(text[0].split('\n'), delimiter=',')
    l_b1 = get_bucket_list(reader)
    l_b1 = [x / 10 + 1 for x in l_b1]
    # does the job!
    # thanks to https://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list
    from operator import itemgetter
    from itertools import groupby
    data = l_b1
    for k, g in groupby(enumerate(data), lambda (i,x):i-x):
        scheme.append(map(itemgetter(1), g))
    return scheme, bx_scheme_name


def get_edges(scheme):
    edges = []
    if all(x > 0 for x in scheme[0]):
        edges.append(0)
    for train in scheme:
        edges.append(train[0])
        edges.append(train[-1] + 1)
    if all(x < 3563 for x in scheme[-1]):
        edges.append(3563)
    return edges


def get_str_bx_intervals(scheme):
    str_filled_bx_intervals = []
    for itrain, train in enumerate(scheme):
        interval = '%i-%i' % (train[0],train[-1])
        length = train[-1] - train[0] + 1
        str_filled_bx_intervals.append(interval)
        print 'train: %i\tbx: %s\tlength: %i' % (itrain, interval, length)
    return str_filled_bx_intervals

def prepareSchemeForRealUse(outfile, data, scheme, bx_scheme_name):
    data['scheme'] = scheme
    data['bx_scheme_name'] = bx_scheme_name
    data['n_colliding_bx'] = len([bx for train in scheme for bx in train])
    data['n_trains'] = len(scheme)
    print 'number of colliding bunches:', data['n_colliding_bx'] 
    print 'number of trains:', data['n_trains']
    data['edges'] = get_edges(scheme)
    print 'n_edges = %i' % len(data['edges'])
    str_filled_bx_intervals= get_str_bx_intervals(scheme)
    with open(outfile, 'w') as f:
        json.dump(data, f)
    print 'results printed to file %s' % outfile
    return 


def get_outfile(run, lhcfill):
    CMSSW_BASE = os.environ['CMSSW_BASE']
    outfilename = os.path.join(CMSSW_BASE, 'src/', 'CalibTracker/HIPAnalysis', 'test/data', 'list_calibTrees_Fill-%i_Run-%i.json' % (lhcfill, run))
    if not(os.path.isfile(outfilename)):
        print 'File does not exist: %s' % outfilename
        print 'Please run getCalibTreesList.py first'
        return None, None
    data = None
    with open(outfilename, 'r') as f:
        data = json.load(f)
    return outfilename, data

if __name__ == '__main__':
    options = get_options()
    username = options.username
    for run in options.run:
        lhcfill = utils.get_fill_number(run, username)
        outfile, data = get_outfile(run, lhcfill)
        if outfile:
            scheme, bx_scheme_name = getFillScheme(lhcfill)
            prepareSchemeForRealUse(outfile, data, scheme, bx_scheme_name)
        print ''

