#! /usr/bin/env python

import subprocess
import collections
import json

# import ROOT stuff
import ROOT

eoscommand = '/afs/cern.ch/project/eos/installation/pro/bin/eos.select'
PFNprefix = 'root://eoscms//eos/cms'
eospath = '/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR15/'
outtreeName = 'outtree.root'
outjson = 'outjson.json'
#root -l root://eoscms//eos/cms/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR15/calibTree_247243.root
#root -l root://cmsxrootd.fnal.gov//store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR15/calibTree_247243.root

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
#allCalibrationFiles = [ PFNprefix + eospath + f for f in files ]
#print allCalibrationFiles[0]

allCalibrationFiles = collections.OrderedDict(sorted(allCalibrationFiles.items()))
#print allCalibrationFiles
#print sorted(allCalibrationFiles.keys())
#print collections.OrderedDict(sorted(allCalibrationFiles.items()))
nRuns = len(allCalibrationFiles)

outfile = ROOT.TFile(outtreeName, 'recreate')
outtree = ROOT.TTree('t', 't')

for irun, run in enumerate(allCalibrationFiles.items()):
    myfile = run[1]['files'][0] # first file of the list
    print "Starting looking at run", irun, "/", nRuns, ":", run[0], "with file:", myfile

    saturatedEvents = {}
    rawid = {}
    t = ROOT.TChain('gainCalibrationTree/tree')
    t.Add(myfile)
    run[1]['nEvents'] = t.GetEntries()
    print "\tnEvents", run[1]['nEvents']
    for ievent, event in enumerate(t):
        if ievent % 5e4 == 0:
            print '\t\tnow treating event', ievent
        if ievent > 1e4:
            break
        saturationIndices = []
#        print len(t.GainCalibrationsaturation)
        for ivalue, value in enumerate(t.GainCalibrationsaturation):
            if bool(value):
                saturationIndices.append(ivalue)
        if len(saturationIndices) < 3:
            continue
        saturatedEvents[ievent] = saturationIndices
        rawid[ievent] = [ t.GainCalibrationrawid[i] for i in saturationIndices ]
    run[1]['nSaturatedEvents'] = len(saturatedEvents)
    run[1]['saturatedEvents'] = saturatedEvents
    run[1]['rawid'] = rawid
    print "\tnSaturatedEvents:", run[1]['nSaturatedEvents']
    break

#print json.dumps(allCalibrationFiles, sort_keys=True,indent=4, separators=(',', ': '))

with open(outjson, 'w') as f:
    json.dump(allCalibrationFiles, f)

