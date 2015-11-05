#! /usr/bin/env python
import subprocess
import collections

eoscommand = '/afs/cern.ch/project/eos/installation/pro/bin/eos.select'
PFNprefix = 'root://eoscms//eos/cms'
eospath = '/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR15/'

proc = subprocess.Popen([eoscommand, 'ls', eospath], stdout=subprocess.PIPE)
files = []
while True:
    line = proc.stdout.readline().strip('\n')
    if line != '':
        files.append(line)
    else:
        break

allRuns = [ r.strip('.root').split('_')[1] for r in files ]
allRuns = set(allRuns)
allCalibrationFiles = {}
for run in allRuns:
    allCalibrationFiles[run] = {}
    allCalibrationFiles[run]['files'] = sorted([ PFNprefix + eospath + f for f in files if f.strip('.root').split('_')[1] == run ])

allCalibrationFiles = collections.OrderedDict(sorted(allCalibrationFiles.items()))

for run in allCalibrationFiles.items():
    print run[1]['files'][0]
#for irun, run in enumerate(allCalibrationFiles.items()):
#    myfile = run[1]['files'][0] # first file of the list


