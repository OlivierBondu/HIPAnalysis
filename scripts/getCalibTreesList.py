#!/bin/env python
import argparse
import socket
import os
import subprocess
import CalibTracker.HIPAnalysis.utils as utils
import json


def get_options():
    parser = argparse.ArgumentParser(description='Return the list of calib trees for a given run')
    parser.add_argument('--run', action='store', dest='run', default=[296173], nargs='+', type=int,
                        help='Run number')
    parser.add_argument('-n', '--username', dest='username', help='Remote lxplus username (local username by default)')
    parser.add_argument('--path', action='store', dest='path', default='/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR17/',
                        type=str, help='path at which find the calibTrees')
    parser.add_argument('--suffix', action='store', dest='suffix', default='', type=str, help='suffix to be appended to the output file name')
    options = parser.parse_args()
    if options.username is None:
        import pwd, os
        options.username = pwd.getpwuid(os.getuid()).pw_name
    return options


def getCalibTreesList(username, run, path, suffix):
    lhcFill = utils.get_fill_number(run, username)
    CMSSW_BASE = os.environ['CMSSW_BASE']
    if len(suffix) > 0 and (suffix[0] is not '_'):
        suffix = '_' + suffix
    outfilename = os.path.join(CMSSW_BASE, 'src/', 'CalibTracker/HIPAnalysis', 'test/data', 'list_calibTrees_Fill-%i_Run-%i%s.json' % (lhcFill, run, suffix))
    if os.path.isfile(outfilename):
        print 'File already exist: %s' % outfilename
        return

    prefix = '/eos/cms'
    fullpath = prefix + path
    utils.connect_to_lxplus(username)
    print "Listing the available calibTrees via eos ls on lxplus" 
    fulllist = subprocess.check_output(['ssh', '%s@lxplus.cern.ch' % username, 'ls', fullpath])
    fulllist = [x for x in fulllist.split('\n') if str(run) in x]
    if len(fulllist) == 0:
        print 'There is no calibTrees associated with run %i, exiting' % run
        return
    outjson = {}
    outjson['files'] = [path + f for f in fulllist]
    with open(outfilename, 'w+') as f:
        json.dump(outjson, f)
    print 'List written to file %s' % outfilename
    return


if __name__ == '__main__':
    options = get_options()
    username = options.username
    path = options.path
    suffix = options.suffix
    for run in options.run:
        getCalibTreesList(username, run, path, suffix)
        print ''
