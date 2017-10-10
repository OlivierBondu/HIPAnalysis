#!/bin/env python
from datetime import datetime
import subprocess
import ast
import os


def get_outfile(run, lhcfill, suffix=''):
    CMSSW_BASE = os.environ['CMSSW_BASE']
    outfilename = None
    outpath = os.path.join(CMSSW_BASE, 'src/', 'CalibTracker/HIPAnalysis', 'test/data')
    noFile = False
    if len(suffix) > 0 and (suffix[0] is not '_'):
        suffix = '_' + suffix
    if lhcfill:
        outfilename = os.path.join(outpath, 'list_calibTrees_Fill-%i_Run-%i%s.json' % (lhcfill, run, suffix))
    else:
        outfilename = [os.path.join(outpath, f) for f in os.listdir(outpath) if ('list_calibTrees_Fill' in f and 'Run-%i%s.json' % (run, suffix) in f)]
        if len(outfilename) == 0:
            noFile = True
        else:
            outfilename = outfilename[0]
    if not(os.path.isfile(outfilename)):
        noFile = True

    if noFile:
        print 'File does not exist: %s' % outfilename
        print 'Please run getCalibTreesList.py first'
        return None
    return outfilename


def connect_to_lxplus(username):
    print "Checking Kerberos ticket before attempting to run on lxplus"
    p = subprocess.Popen(['klist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    ticket = stdout
    ticket = [x for x in ticket.split('\n') if 'CERN.CH@CERN.CH' in x]
    is_ticket_valid = True
    if len(ticket) > 0:
        ticket = ticket[0]
        print "Current ticket: %s" % ticket
        ticket = ticket.split()
        now = datetime.now()
        t_ticket = datetime.strptime(ticket[2] + ':' + ticket[3], '%m/%d/%y:%H:%M:%S')
        if now > t_ticket:
            print 'Ticket no longer valid'
            is_ticket_valid = False
    else:
        print 'No ticket'
        is_ticket_valid = False

    if not(is_ticket_valid):
        print 'Running kinit, please enter your lxplus password for username %s' % username
        p = subprocess.Popen(['kinit', '%s@CERN.CH' % username])
        p.communicate()
    return


def connect_to_grid():
    p = subprocess.Popen(['voms-proxy-info', '--timeleft'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    timeleft = int(stdout.replace('\n', ''))
    if timeleft < 3600:
        print 'Grid proxy do not exist or less than an hour of validity (%ih:%im:%is left)' % (timeleft / 3600, (timeleft % 3600) / 60, timeleft % 60)
        # less than an hour left on proxy, let's renew it
        p = subprocess.call(['voms-proxy-init', '--voms', 'cms'])
    else:
        print 'Grid proxy still valid for another %ih:%im:%is' % (timeleft / 3600, (timeleft % 3600) / 60, timeleft % 60)
    return


def get_fill_number(run, username, viaLxplus=True):
    explain = 'Getting the fill number for run %i ' % run
    lhcFill = None
    if viaLxplus:
        print explain + 'via lxplus'
        connect_to_lxplus(username)
        cmds = []
        cmds = cmds + ['ssh', '%s@lxplus.cern.ch' % username]
        cmds = cmds + ['python', '/afs/cern.ch/user/v/valdo/public/rhapi.py', '\"select f.lhcfill from runreg_global.runs f where f.runnumber=%i\"' % run, '-f', 'json']
        result = subprocess.check_output(cmds)
        s = ast.literal_eval(result)
        lhcFill = s['data'][0][0]
    else:
        # Not via lxplus, so the other way around is through DAS via the GRID
        print explain + 'via the GRID'
        connect_to_grid()
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
    print 'lhcFill=', lhcFill
    return lhcFill

