#!/bin/env python
# Python imports
import os
import json
# File location
outdir = "/storage/data/cms"
eosdir = "store/user/obondu/CRAB_PrivateMC/crab_HIPAnalysis_test/"
taskdir = "151211_182718/0000/"
# ROOT setup
import ROOT
from ROOT import TChain
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
#ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.TGaxis.SetMaxDigits(3)

chain = TChain("t")
chain.Add(os.path.join(outdir, eosdir, taskdir) + "output_*root")
print "chain.GetEntries()=", chain.GetEntries()

runlist = {}

for i in xrange(chain.GetEntries()):
    chain.GetEntry(i)
    r = int(chain.run)
    ls = int(chain.lumi)
    if r not in runlist:
        runlist[r] = []
    runlist[r].append(ls)

for r in runlist:
    # remove duplicates
    l = list(set(runlist[r]))
    # sort
    l.sort()
    runlist[r] = []
    for ls in l:
        # not optimal since there could be consecutive ls, but well
        runlist[r].append([ls,ls])
#print runlist

with open('allcalibtrees.json', 'w') as f:
    json.dump(runlist, f)



