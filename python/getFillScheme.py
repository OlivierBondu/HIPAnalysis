#!/bin/env python
import argparse
import json
import pprint
import StringIO
import csv
import urllib2
import subprocess
import os


def get_options():
    parser = argparse.ArgumentParser(description='Return the filled bunches for a given run')
    parser.add_argument('--run', action='store', dest='run', default=296173, type=int,
                        help='Run for which the BX has to be fetched')
    parser.add_argument('--split', action='store', dest='split', default=0, type=int,
                        help='Split the trains in subtrains of length split')
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
    # Note: in principle we could access this more cleanly through the Run Registry API
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/DqmRrApi
    # but I cannot manage to have it run if not on lxplus
    p = subprocess.Popen(['voms-proxy-info', '--timeleft'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    timeleft = int(stdout.replace('\n', ''))
    if timeleft < 3600:
        print 'Grid proxy do not exist or less than an hour of validity (%ih:%im:%is left)' % (timeleft / 3600, (timeleft % 3600) / 60, timeleft % 60)
        print '(Needed to access DAS)'
        # less than an hour left on proxy, let's renew it
        p = subprocess.call(['voms-proxy-init', '--voms', 'cms'])
    else:
        print 'Grid proxy still valid for another %ih:%im:%is' % (timeleft / 3600, (timeleft % 3600) / 60, timeleft % 60)
    print 'Getting fill number from DAS for run %i' % run
    p = subprocess.Popen(['das_client', '--query', 'run=%i' % run, '--format=json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    tmp = json.loads(stdout)
    tmp = tmp['data'][0]['run']
    tmp = [x for x in tmp if len(x) > 1]
    for t in tmp:
        try:
            lhcFill = t['lhcFill']
            break
        except KeyError:
            continue
#    lhcFill = tmp[0]['lhcFill']
    print 'lhcFill=', lhcFill
    return lhcFill


def getFillScheme(run, split=0):
    # Get the fill number
    n_fill = get_fill_number(run)
    # Get the fill scheme and write it to file
    fill_scheme_file = 'bunch_scheme_fill_%i.json' % n_fill
    LPC_API = 'https://lpc.web.cern.ch/cgi-bin/schemeInfo.py'
    QUERY = '?fill=%i&fmt=json' % n_fill
    # curl -o fill_5750.json https://lpc.web.cern.ch/cgi-bin/schemeInfo.py\?fill\=5750\&fmt\=json
    print 'Getting fill scheme from LPC'
    request = urllib2.Request('%s%s' % (LPC_API, QUERY))
    response = urllib2.urlopen(request)
    # FIXME: avoid writing the file to disk, surely there is a way to deal keeping this in memory only...
    with open(fill_scheme_file, 'w') as f:
        f.write(response.read())
    d = None
    scheme = []
    n_colliding_bx = None
    bx_scheme_name = None
    with open(fill_scheme_file, 'r') as f:
        d = d = json.load(f)
        bx_scheme_name = d['fills']['%i' % n_fill]['name']
    bx_scheme_name += '.json'
    os.rename(fill_scheme_file, bx_scheme_name)
    with open(bx_scheme_name, 'r') as f:
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
    str_filled_bx_intervals = []
    str_splittrains = []
    for itrain, train in enumerate(scheme):
        interval = '%i-%i' % (train[0],train[-1])
        length = train[-1] - train[0] + 1
        nfullsubtrains = 0
        nsubtrains = 0
        if split != 0:
            nfullsubtrains = length / split
            if length % split != 0:
                nsubtrains += 1
        nsubtrains += nfullsubtrains
        print 'train: %i\tbx: %s\tlength: %i' % (itrain, interval, length)
        for isubtrain in xrange(nsubtrains):
            maxisubtrain = (isubtrain + 1) * split - 1
            if nsubtrains > nfullsubtrains and isubtrain == nsubtrains -1:
                maxisubtrain = -1
            subinterval = '%i-%i' % (train[isubtrain * split], train[maxisubtrain])
            sublength = train[maxisubtrain] - train[isubtrain * split] + 1
            print '\tsubtrain: %i\tbx: %s\tlength: %i' % (isubtrain, subinterval, sublength)
            str_splittrains.append(subinterval)
        str_filled_bx_intervals.append(interval)
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
#    print 'edges:', edges
    print 'results printed to file %s' % bx_scheme_name
    return str_filled_bx_intervals, edges, str_splittrains


if __name__ == '__main__':
    options = get_options()
    run = options.run
    split = options.split
    getFillScheme(run, split)

