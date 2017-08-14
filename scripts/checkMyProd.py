#!/bin/env python
import argparse
import os
from CRABAPI.RawCommand import crabCommand
import sys
import site
sys.path.append(os.path.join(site.USER_BASE, 'lib', 'python2.6', 'site-packages'))
from progressbar import ProgressBar, SimpleProgress
import json
import copy

# Silencing the CRAB client
from CRABClient.UserUtilities import setConsoleLogLevel
from CRABClient.ClientUtilities import LOGLEVEL_MUTE
setConsoleLogLevel(LOGLEVEL_MUTE)


def get_options():
    parser = argparse.ArgumentParser(description='Check the current crab production')
    parser.add_argument('--workArea', action='store', dest='workArea', default='tasks', type=str,
                        help='CRAB work area')
    parser.add_argument('--newProd', action='store_true', dest='isNewProd', help='switch it on once per new prod')
    options = parser.parse_args()
    return options


def checkMyProd(workArea, isNewProd):
    tasks = [t for t in os.listdir(workArea)]
    summary = None
    summaryFile = 'prod_status.json'
    tocheck = []
    if isNewProd: 
        summary = {}
        tocheck = tasks
        summary['files'] = []
    else:
        if not os.path.isfile(summaryFile):
            raise IOError('There is no pre-existing summary file, please run the script with --new for the first time')
        with open(summaryFile, 'r') as f:
            summary = json.load(f)
        tmp = copy.deepcopy(summary)
        for k in tmp:
            if 'files' in k:
                continue
            if ('COMPLETED' not in k) and ('FAILED' not in k):
                tocheck += summary[k]
                del summary[k]
                
    pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(tocheck)).start()
    print 'Checking CRAB status of (not COMPLETED) tasks'
    for it, t in enumerate(tocheck):
        pbar.update(it + 1)
        res = crabCommand('status', dir = workArea + '/' + t)
        status = res['status']
        proxiedWebDir = res['proxiedWebDir']
        tmp = proxiedWebDir.split('/')[-1]
        time = tmp.split(':')[0]
#        print res
        if status in summary:
            summary[status].append(t)
        else:
            summary[status] = [t]
    pbar.finish()

    print 'Summary:'
    for k in summary:
        if 'files' in k:
            continue
        print k, len(summary[k])

    files = summary['files']
    for t in summary['COMPLETED']:
        alreadyHere = False
        for f in files:
            if t in f:
                alreadyHere = True
        if not alreadyHere:
            res = crabCommand('getoutput', '--dump', dir = workArea + '/' + t)
            print 'task:\t', t
            files += res['lfn']
            for f in res['lfn']:
                print '\t', f

    with open(summaryFile, 'w') as f:
        json.dump(summary, f)
    return


if __name__ == '__main__':
    options = get_options()
    checkMyProd(options.workArea, options.isNewProd)

