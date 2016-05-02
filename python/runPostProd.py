#!/bin/env python
# Python imports
import os
import json
import argparse
from array import array
# File location
outdir = "/storage/data/cms"
eosdir = "store/user/obondu/CRAB_PrivateMC/crab_HIPAnalysis/"
taskdir = "160418_095701/0000/"
outtreedir_ = "HIPCalibTrees_160418_firsttry"
# ROOT setup
import ROOT
from ROOT import TChain, TFile
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
# User utilities
import getLumiJSON
import compute_sample_luminosity

def runPostProd(indir, outtreedir):
    #####
    print "\nGet the lumi JSON file"
    #####
    outjson = 'allcalibtrees.json'
    getLumiJSON.getLumiJSON(indir, outjson)
    print 'done'

    #####
    print "\nGet the luminosity"
    #####
    parser = argparse.ArgumentParser(description='Compute luminosity of a set of samples.')
    options = parser.parse_args()
    options.inputfiles = [outjson]
    options.local = False
    options.username = 'obondu'
    alllumi = ''
    with open(outjson) as f:
        d = json.load(f)
        d_ = {}
        for k in d:
            d_[int(k)] = d[k]
        alllumi = compute_sample_luminosity.compute_luminosity(d, options)
        with open('allcalibtrees.csv', 'w') as o:
            o.write(alllumi)
    headerLine = ''
    brilInfo = {}
    # Get Header to fill the dir
    with open('allcalibtrees.csv') as f:
        firstCommentedLine = True
        for line in f:
            if '#' not in line:
                continue
            if firstCommentedLine:
                firstCommentedLine = False
                continue
            elif len(headerLine) < 1:
                #run:fill,ls,time,beamstatus,E(GeV),delivered(/ub),recorded(/ub),avgpu,source
                headerLine = line.strip().replace('#', '').replace(':', ',', 1).split(',')
                break
#    print headerLine
    irun = headerLine.index('run')
    ifill = headerLine.index('fill')
    ils = headerLine.index('ls')
    itime = headerLine.index('time')
    idelivered = headerLine.index('delivered(/ub)')
    irecorded = headerLine.index('recorded(/ub)')
    iavgpu = headerLine.index('avgpu')
    # Get the info itself
    with open('allcalibtrees.csv') as f:
        for line in f:
            if 'Summary' in line:
                break
            if '#' in line:
                continue
            # 247243:3829,1:0,06/06/15 12:55:37,STABLE BEAMS,6500,460.468,0.000,17.2,BCM1F^M
            #257490:4420,1:1,09/25/15 18:55:00,STABLE BEAMS,6500,59085.017,57661.731,0.0,PXL^M
            l = line.strip().replace(':', ',', 1).split(',')
            if len(l) < (max(irun, ifill, ils, itime, idelivered, irecorded, iavgpu) + 1):
                continue
            brilInfo[l[itime]] = {}
            brilInfo[l[itime]]['run'] = int(l[irun])
            brilInfo[l[itime]]['fill'] = int(l[ifill])
            brilInfo[l[itime]]['ls'] = int(l[ils].split(':')[0])
            brilInfo[l[itime]]['delivered'] = float(l[idelivered])
            brilInfo[l[itime]]['recorded'] = float(l[irecorded])
            brilInfo[l[itime]]['avgpu'] = float(l[iavgpu])
#            break
#    print brilInfo
    print 'done'

    #####
    print '\nAdd the luminosity to the tree'
    #####
    if not os.path.exists(outtreedir):
        os.makedirs(outtreedir)
    outFile = outtreedir + '/output.root'
    newFile = TFile(outFile, 'recreate')
    for treename in ['eventtree']: #, 'clustertree']: # ["t"]
        chain = TChain(treename)
        chain.Add(indir + 'output_30*root')
        t = chain.CloneTree(0)
        nEntries = chain.GetEntries()
        nSkipped = 0
        print '\ttree=', treename, 'nEntries=', nEntries
        delivered = array('f', [0.])
        recorded = array('f', [0.])
        avgpu = array('f', [0.])
        t.Branch('brilcalc_delivered', delivered, 'brilcalc_delivered/F' )
        t.Branch('brilcalc_recorded', recorded, 'brilcalc_recorded/F' )
        t.Branch('brilcalc_avgpu', avgpu, 'brilcalc_avgpu/F' )
        for i in range(chain.GetEntries()):
            if (i % 1000 == 0 and i < 10000) or (i % 10000 == 0):
                print '\t\t\tTreating event i= %i / %i (%.1f %%)' % (i, nEntries, float(i)/float(nEntries) * 100.)
            chain.GetEntry(i)
    #        print chain.run
            hasLumiInfo = False
            for k in brilInfo:
    #            print brilInfo[k]['run']
    #            break
                if (treename == 'eventtree' and brilInfo[k]['run'] == chain.run_) or (treename == 'clustertree' and brilInfo[k]['run'] == chain.run):
                    if (treename == 'eventtree' and brilInfo[k]['ls'] == chain.lumi_) or (treename == 'clustertree' and brilInfo[k]['run'] == chain.lumi):
                        hasLumiInfo = True
                        delivered[0] = brilInfo[k]['delivered']
                        recorded[0] = brilInfo[k]['recorded']
                        avgpu[0] = brilInfo[k]['avgpu']
    #                    print 'voila', i, chain.run, chain.lumi
    #            print delivered
            if not hasLumiInfo:
                nSkipped += 1
    #            print '\tSkipping event %i: has no lumi info (run= %i, ls= %i)' % (i, chain.run, chain.lumi)
                continue
            t.Fill()
    #        break
        print '\tnSkipped= %i (%.1f %%)' % (nSkipped, float(nSkipped) / nEntries * 100)
        newFile.Write()
    newFile.Close()
    print 'done'

if __name__ == '__main__':
    indir = os.path.join(outdir, eosdir, taskdir)
    outtreedir = outtreedir_
    runPostProd(indir, outtreedir)

