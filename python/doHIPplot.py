#!/bin/env python
# Python imports
import os
import numpy as np
# File location
#outdir = "/storage/data/cms"
#eosdir = "store/user/obondu/CRAB_PrivateMC/crab_HIPAnalysis/"
#taskdir = "151211_182718/0000/"
#taskdir = "160405_120842/0000/"
outdir = ''
eosdir = ''
taskdir = 'HIPCalibTrees_160412bis/'
plotdir = "plots_160413"
# ROOT setup
import ROOT
from ROOT import TChain, TCanvas, TLatex
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.TGaxis.SetMaxDigits(3)

chain = TChain("t")
chain.Add(os.path.join(outdir, eosdir, taskdir) + "output*root")
print "chain.GetEntries()=", chain.GetEntries()

c1 = TCanvas()
if not os.path.exists(plotdir):
    os.makedirs(plotdir)
# kBird palette
stops = np.array([0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
red = np.array([0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764])
green = np.array([0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832])
blue = np.array([0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539])
ROOT.TColor.CreateGradientColorTable(9, stops, red, green, blue, 255, 1)

vars = {
#"subDetector": ["subDetector", "#Clusters:subDetector"],
"nSaturatedStrips": ["nSaturatedStrips", "#Clusters:nSaturatedStrips"],
"@nSaturatedStrips.size()": ["nClusters", "#Events:nClusters"], # == nSaturatedClusters[0]
#"saturatedCharge[1]
"nSaturatedClusters[0]": ["nSaturatedClusters_0", "#Events:nClusters w/ (nSaturatedStrips #geq 0)"],
"nSaturatedClusters[1]": ["nSaturatedClusters_1", "#Events:nClusters w/ (nSaturatedStrips #geq 1)"],
"nSaturatedClusters[2]": ["nSaturatedClusters_2", "#Events:nClusters w/ (nSaturatedStrips #geq 2)"],
"nSaturatedClusters[3]": ["nSaturatedClusters_3", "#Events:nClusters w/ (nSaturatedStrips #geq 3)"],
"nSaturatedClusters[4]": ["nSaturatedClusters_4", "#Events:nClusters w/ (nSaturatedStrips #geq 4)"],
"nTracks": ["nTracks", "#Events:nTracks"],
"nTotTracks": ["nTotTracks", "#Events:nTotTracks"],
"bx": ["bx", "#Events:Bunch Crossing"],
"(brilcalc_recorded/1000.)": ["lumi", "#Events:recorded lumi (nb)"],
"brilcalc_avgpu": ["pu", "#Events:<pu>"],

#"": ["", ":"],
#"nSaturatedStrips[3]:run": "nSaturatedStrips_vs_run",
#"nSaturatedStrips[3]:lumi": "nSaturatedStrips_vs_ls",
#"nSaturatedStrips[3]:(brilcalc_recorded/1000.)": ["nSaturatedStrips_vs_lumi", "nSaturatedStrips:recorded lumi (nb)"],
#"nSaturatedStrips[3]:brilcalc_avgpu": ["nSaturatedStrips_vs_pu", "nSaturatedStrips:<pu>"],
#"nSaturatedStrips[3]:bx": ["nSaturatedStrips_vs_bx", "nSaturatedStrips:bx"],
#"nSaturatedStrips[3]:nTracks": ["nSaturatedStrips_vs_nTracks", "nSaturatedStrips:nTracks"],
#"nSaturatedStrips[3]:brilcalc_nTotTracks": ["nSaturatedStrips_vs_nTotTracks", "nSaturatedStrips:nTotTracks"],
#"(nClusters / nSaturatedClusters[0])": "nClusters_o_nTotClusters",
#"(nClusters / nSaturatedClusters[0]):run": "nClusters_o_nTotClusters_vs_run",
#"(nClusters / nSaturatedClusters[0]):lumi": "nClusters_o_nTotClusters_vs_lumi",
"(nSaturatedClusters[1] / nSaturatedClusters[0]):(brilcalc_recorded/1000.)": ["nSaturatedClusters_1_o_nTotClusters_vs_lumi", "nSaturatedClusters (1) / nTotClusters:recorded lumi (nb)", [11.5e-6, 13.5e-6]],
"(nSaturatedClusters[1] / nSaturatedClusters[0]):brilcalc_avgpu": ["nSaturatedClusters_1_o_nTotClusters_vs_pu", "nSaturatedClusters (1)/ nTotClusters:<pu>", [10e-6, 25e-6]],
"(nSaturatedClusters[1] / nSaturatedClusters[0]):bx": ["nSaturatedClusters_1_o_nTotClusters_vs_bx", "nSaturatedClusters (1)/ nTotClusters:bx", [10.e-6, 25e-6]],
"(nSaturatedClusters[1] / nSaturatedClusters[0]):nTracks": ["nSaturatedClusters_1_o_nTotClusters_vs_nTracks", "nSaturatedClusters (1)/ nTotClusters:nTracks", [10e-6, 25e-6]],
"saturatedCharge[1]:(brilcalc_recorded/1000.)": ["", ":"],

"(nSaturatedClusters[2] / nSaturatedClusters[0]):(brilcalc_recorded/1000.)": ["nSaturatedClusters_2_o_nTotClusters_vs_lumi", "nSaturatedClusters (2) / nTotClusters:recorded lumi (nb)", [0.4e-6, 0.8e-6]],
"(nSaturatedClusters[2] / nSaturatedClusters[0]):brilcalc_avgpu": ["nSaturatedClusters_2_o_nTotClusters_vs_pu", "nSaturatedClusters (2)/ nTotClusters:<pu>", [0.25e-6, 2e-6]],
"(nSaturatedClusters[2] / nSaturatedClusters[0]):bx": ["nSaturatedClusters_2_o_nTotClusters_vs_bx", "nSaturatedClusters (2)/ nTotClusters:bx", [0.25e-6, 2.1e-6]],
"(nSaturatedClusters[2] / nSaturatedClusters[0]):nTracks": ["nSaturatedClusters_2_o_nTotClusters_vs_nTracks", "nSaturatedClusters (2)/ nTotClusters:nTracks", [0.25e-6, 1.5e-6]],

"(nSaturatedClusters[3] / nSaturatedClusters[0]):(brilcalc_recorded/1000.)": ["nSaturatedClusters_3_o_nTotClusters_vs_lumi", "nSaturatedClusters (3) / nTotClusters:recorded lumi (nb)", [0.15e-6, 0.3e-6]],
"(nSaturatedClusters[3] / nSaturatedClusters[0]):brilcalc_avgpu": ["nSaturatedClusters_3_o_nTotClusters_vs_pu", "nSaturatedClusters (3)/ nTotClusters:<pu>", [0, 1e-6]],
"(nSaturatedClusters[3] / nSaturatedClusters[0]):bx": ["nSaturatedClusters_3_o_nTotClusters_vs_bx", "nSaturatedClusters (3)/ nTotClusters:bx", [0.15, 0.4e-6]],
"(nSaturatedClusters[3] / nSaturatedClusters[0]):nTracks": ["nSaturatedClusters_3_o_nTotClusters_vs_nTracks", "nSaturatedClusters (3)/ nTotClusters:nTracks", [0, 0.8e-6]],

"(nSaturatedClusters[4] / nSaturatedClusters[0]):(brilcalc_recorded/1000.)": ["nSaturatedClusters_4_o_nTotClusters_vs_lumi", "nSaturatedClusters (4) / nTotClusters:recorded lumi (nb)", [0, 5e-6]],
"(nSaturatedClusters[4] / nSaturatedClusters[0]):brilcalc_avgpu": ["nSaturatedClusters_4_o_nTotClusters_vs_pu", "nSaturatedClusters (4)/ nTotClusters:<pu>", [0, 5e-6]],
"(nSaturatedClusters[4] / nSaturatedClusters[0]):bx": ["nSaturatedClusters_4_o_nTotClusters_vs_bx", "nSaturatedClusters (4)/ nTotClusters:bx", [0, 5e-6]],
"(nSaturatedClusters[4] / nSaturatedClusters[0]):nTracks": ["nSaturatedClusters_4_o_nTotClusters_vs_nTracks", "nSaturatedClusters (4)/ nTotClusters:nTracks", [0, 5e-6]],
}

cuts = {
"allTracker": "1", 
#"TIB": "subDetector == 3",
#"TID": "subDetector == 4",
#"TOB": "subDetector == 5",
#"TEC": "subDetector == 6"
}

for icut, cut in enumerate(cuts):
    print cut
    for ivar, var in enumerate(vars):
        print "\t" + var
        options = ""
        if ":" in var:
#            print True
            options = "colznum"
        chain.Draw(var + ">>h_tmp_%s_%s" % (icut, ivar), cuts[cut], options)
        h = ROOT.gDirectory.Get("h_tmp_%s_%s" % (icut, ivar))
        h.SetTitle("")
        if len(var.split(":")) > 1:
            c1.SetLogy(0)
#            h.SetTitle(";" + var.split(":")[1] + ";" + var.split(":")[0])
            h.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h.SetContour(1000)
#            if vars[var] == "nSaturatedStrips_vs_lumi":
#                h.SetMaximum(1.0e-6)
#                h.SetMinimum(1.0e-7)
#                h.GetYaxis().SetRangeUser(5.0e-7, 5.0e-6)
#                c1.Update()
        else:
            c1.SetLogy(1)
            h.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h.GetXaxis().SetTitle(vars[var][1].split(':')[1])
#            h.GetXaxis().SetTitle(vars[var][1])
        latexLabel = TLatex()
        latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
        latexLabel.SetNDC()
        latexLabel.SetTextFont(42) # helvetica
        latexLabel.DrawLatex(0.27, 0.96, cut)
        c1.Print(plotdir + "/" + vars[var][0] + "_" + cut + ".png")
        c1.Print(plotdir + "/" + vars[var][0] + "_" + cut + ".pdf")
# now with profiles for 2D
        if len(var.split(":")) > 1:
            p = h.ProfileX()
#            if len(vars[var]) > 2:
#                p.GetYaxis().SetRangeUser(vars[var][2][0], vars[var][2][1])
            p.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            p.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            p.Draw()
            c1.Print(plotdir + "/profileX_" + vars[var][0] + "_" + cut + ".png")
            c1.Print(plotdir + "/profileX_" + vars[var][0] + "_" + cut + ".pdf")

