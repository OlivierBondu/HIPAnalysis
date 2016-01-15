#!/bin/env python
# Python imports
import os
# File location
outdir = "/storage/data/cms"
eosdir = "store/user/obondu/CRAB_PrivateMC/crab_HIPAnalysis_test/"
taskdir = "151211_182718/0000/"
# ROOT setup
import ROOT
from ROOT import TChain, TCanvas, TLatex
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
#ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.TGaxis.SetMaxDigits(3)

chain = TChain("t")
chain.Add(os.path.join(outdir, eosdir, taskdir) + "output_*root")
print "chain.GetEntries()=", chain.GetEntries()

c1 = TCanvas()

vars = {
"nSaturatedStrips": "nSaturatedStrips",
"nSaturatedStrips:run": "nSaturatedStrips_vs_run",
"nSaturatedStrips:lumi": "nSaturatedStrips_vs_lumi",
"(nClusters / nTotClusters)": "nClusters_o_nTotClusters",
"(nClusters / nTotClusters):run": "nClusters_o_nTotClusters_vs_run",
"(nClusters / nTotClusters):lumi": "nClusters_o_nTotClusters_vs_lumi"
}

cuts = {
"allTracker": "1", 
"TIB": "subDetector == 3",
"TID": "subDetector == 4",
"TOB": "subDetector == 5",
"TEC": "subDetector == 6"
}

for icut, cut in enumerate(cuts):
    print cut
    for ivar, var in enumerate(vars):
        print "\t" + var
        options = ""
        if ":" in var:
#            print True
            options = "colz"
        chain.Draw(var + ">>h_tmp_%s_%s" % (icut, ivar), cuts[cut], options)
        h = ROOT.gDirectory.Get("h_tmp_%s_%s" % (icut, ivar))
        h.SetTitle("")
        if len(var.split(":")) > 1:
            c1.SetLogy(0)
            h.SetTitle(";" + var.split(":")[1] + ";" + var.split(":")[0])
#            if vars[var] == "nSaturatedStrips_vs_lumi":
#                h.SetMaximum(1.0e-6)
#                h.SetMinimum(1.0e-7)
#                h.GetYaxis().SetRangeUser(5.0e-7, 5.0e-6)
#                c1.Update()
        else:
            c1.SetLogy(1)
            h.GetXaxis().SetTitle(var.split(":")[0])
        latexLabel = TLatex()
        latexLabel.SetTextSize(0.55 * c1.GetTopMargin())
        latexLabel.SetNDC()
        latexLabel.SetTextFont(42) # helvetica
        latexLabel.DrawLatex(0.72, 0.92, cut)
        c1.Print("plots/" + vars[var] + "_" + cut + ".png")
        c1.Print("plots/" + vars[var] + "_" + cut + ".pdf")
# now with profiles for 2D
        if len(var.split(":")) > 1:
            p = h.ProfileX()
            p.Draw()
            c1.Print("plots/profileX_" + vars[var] + "_" + cut + ".png")
            c1.Print("plots/profileX_" + vars[var] + "_" + cut + ".pdf")

