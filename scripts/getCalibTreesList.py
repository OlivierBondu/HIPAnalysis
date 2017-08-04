#!/bin/env python
import argparse
import socket
import os
import subprocess
import CalibTracker.HIPAnalysis.getFillScheme as getFillScheme


def get_options():
    parser = argparse.ArgumentParser(description='Return the list of calib trees for a given run')
    parser.add_argument('--run', action='store', dest='run', default=[296173], nargs='+', type=int,
                        help='Run number')
    parser.add_argument('-n', '--username', dest='username', help='Remote lxplus username (local username by default)')
    options = parser.parse_args()
    if options.username is None:
        import pwd, os
        options.username = pwd.getpwuid(os.getuid()).pw_name
    return options


def getCalibTreesList(username, run):
    lhcFill = getFillScheme.get_fill_number(run)
    CMSSW_BASE = os.environ['CMSSW_BASE']
    outfilename = os.path.join(CMSSW_BASE, 'src/', 'CalibTracker/HIPAnalysis', 'test/data', 'list_calibTrees_Fill-%i_Run-%i.txt' % (lhcFill, run))
    if os.path.isfile(outfilename):
        print 'File already exist: %s' % outfilename
        return

    path = '/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR17/'
    prefix = '/eos/cms'
    fullpath = prefix + path
    print "Checking Kerberos ticket before attempting to run on lxplus"
    p = subprocess.Popen(['klist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    ticket = stdout
    ticket = [x for x in ticket.split('\n') if 'CERN.CH@CERN.CH' in x]
    if len(ticket) > 0:
        print "Current ticket: %s" % ticket[0]
    else:
        print "No ticket, running kinit, please enter your lxplus password"
#        ticket = subprocess.check_output(['kinit', '%s@CERN.CH' % username])
        p = subprocess.Popen(['kinit', '%s@CERN.CH' % username])
        p.communicate()
    print "Listing the available calibTrees via eos ls on lxplus" 
    fulllist = subprocess.check_output(['ssh', '%s@lxplus.cern.ch' % username, 'ls', fullpath])
    fulllist = [x for x in fulllist.split('\n') if str(run) in x]
    if len(fulllist) == 0:
        print 'There is no calibTrees associated with run %i, exiting' % run
        return

    with open(outfilename, 'w') as outfile:
        for f in fulllist:
            outfile.write(path + f + '\n')
    print 'List written to file %s' % outfilename
    return


if __name__ == '__main__':
    options = get_options()
    username = options.username
    for run in options.run:
        getCalibTreesList(username, run)
        print ''
