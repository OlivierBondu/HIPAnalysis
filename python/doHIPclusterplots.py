#!/bin/env python
# Python imports
import os
import numpy as np
# File location
outdir = "/storage/data/cms"
eosdir = "store/user/obondu/CRAB_PrivateMC/crab_HIPAnalysis/"
#taskdir = "151211_182718/0000/"
taskdir = "160418_095701/0000/"
#outdir = ''
#eosdir = ''
#taskdir = 'HIPCalibTrees_160418_firsttry/'
plotdir = "plots_160525_clusters"
# ROOT setup
import ROOT
from ROOT import TChain, TCanvas, TLatex, TLegend
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.TGaxis.SetMaxDigits(3)

chain = TChain("clustertree")
chain.Add(os.path.join(outdir, eosdir, taskdir) + "output_581*root")
chain00 = TChain("clustertree")
chain00.Add('/home/fynu/obondu/TRK/CMSSW_7_4_15/src/CalibTracker/HIPAnalysis/test/output_SDV_HIP_2016-05-16_00.root')
chain01 = TChain("clustertree")
chain01.Add('/home/fynu/obondu/TRK/CMSSW_7_4_15/src/CalibTracker/HIPAnalysis/test/output_SDV_HIP_2016-05-16_01.root')
chain02 = TChain("clustertree")
chain02.Add('/home/fynu/obondu/TRK/CMSSW_7_4_15/src/CalibTracker/HIPAnalysis/test/output_SDV_HIP_2016-05-16_02.root')
#chain.Add(os.path.join(outdir, eosdir, taskdir) + "output_57*root")
print "chain.GetEntries()=", chain.GetEntries()
print "chain00.GetEntries()=", chain00.GetEntries()
print "chain01.GetEntries()=", chain01.GetEntries()
print "chain02.GetEntries()=", chain02.GetEntries()

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
#"": ["", ":"],
"nStrips": ["nStrips", "#Clusters:nStrips"],
"nSaturatedStrips": ["nSaturatedStrips", "#Clusters:nSaturatedtrips"],
"(nSaturatedStrips / nStrips)": ["nSaturatedStrips_o_nStrips", "#Clusters:nSaturatedtrips / nStrips"],
"totalCharge": ["totalCharge", "#Clusters:total charge"],
"totalChargeoverpath": ["totalChargeoverpath", "#Clusters:(total charge) / path"],
"(nSaturatedStrips / nStrips):totalCharge": ["nSaturatedStrips_o_nStrips_vs_totalCharge", "nSaturatedtrips / nStrips:total charge"],
"(nSaturatedStrips / nStrips):totalChargeoverpath": ["nSaturatedStrips_o_nStrips_vs_totalChargeoverpath", "nSaturatedtrips / nStrips:(total charge) / path"],

"(nSaturatedStrips / nStrips):nStrips": ["nSaturatedStrips_o_nStrips_vs_nStrips", "nSaturatedtrips / nStrips:nStrips"],
"totalChargeoverpath:nStrips": ["totalChargeoverpath_vs_nStrips", "totalChargeoverpath:nStrips"],
"totalChargeoverpath:(nSaturatedStrips / nStrips)": ["totalChargeoverpath_vs_nSaturatedStrips_o_nStrips", "totalChargeoverpath:nSaturatedtrips / nStrips"],
}

cuts = {
#"allTracker": "1", 
"TIB": "subDetector == 3",
"TID": "subDetector == 4",
"TOB": "subDetector == 5",
"TEC": "subDetector == 6",
#"TIB_charge_over_400": "(subDetector == 3) && (totalChargeoverpath > 400)",
#"TID_charge_over_400": "(subDetector == 4) && (totalChargeoverpath > 400)",
#"TOB_charge_over_400": "(subDetector == 5) && (totalChargeoverpath > 400)",
#"TEC_charge_over_400": "(subDetector == 6) && (totalChargeoverpath > 400)",
##### selection on nSaturatedStrips
#"allTracker_1_sat_strip": "1 && (nSaturatedStrips > 0)", 
#"TIB_1_sat_strip": "(subDetector == 3) && (nSaturatedStrips > 0)",
#"TID_1_sat_strip": "(subDetector == 4) && (nSaturatedStrips > 0)",
#"TOB_1_sat_strip": "(subDetector == 5) && (nSaturatedStrips > 0)",
#"TEC_1_sat_strip": "(subDetector == 6) && (nSaturatedStrips > 0)",
#"allTracker_2_sat_strip": "1 && (nSaturatedStrips > 1)", 
#"TIB_2_sat_strip": "(subDetector == 3) && (nSaturatedStrips > 1)",
#"TID_2_sat_strip": "(subDetector == 4) && (nSaturatedStrips > 1)",
#"TOB_2_sat_strip": "(subDetector == 5) && (nSaturatedStrips > 1)",
#"TEC_2_sat_strip": "(subDetector == 6) && (nSaturatedStrips > 1)",
#"allTracker_3_sat_strip": "1 && (nSaturatedStrips > 2)", 
#"TIB_3_sat_strip": "(subDetector == 3) && (nSaturatedStrips > 2)",
#"TID_3_sat_strip": "(subDetector == 4) && (nSaturatedStrips > 2)",
#"TOB_3_sat_strip": "(subDetector == 5) && (nSaturatedStrips > 2)",
#"TEC_3_sat_strip": "(subDetector == 6) && (nSaturatedStrips > 2)",
#"allTracker_4_sat_strip": "1 && (nSaturatedStrips > 3)", 
#"TIB_4_sat_strip": "(subDetector == 3) && (nSaturatedStrips > 3)",
#"TID_4_sat_strip": "(subDetector == 4) && (nSaturatedStrips > 3)",
#"TOB_4_sat_strip": "(subDetector == 5) && (nSaturatedStrips > 3)",
#"TEC_4_sat_strip": "(subDetector == 6) && (nSaturatedStrips > 3)",
}

for icut, cut in enumerate(cuts):
    print cut
    for ivar, var in enumerate(vars):
        print "\t" + var
        options = ""
        if ":" in var:
#            print True
            options = "colznum"
        chain00.Draw(var + ">>h00_tmp_%s_%s" % (icut, ivar), cuts[cut], options)
        chain01.Draw(var + ">>h01_tmp_%s_%s" % (icut, ivar), cuts[cut], options)
        chain02.Draw(var + ">>h02_tmp_%s_%s" % (icut, ivar), cuts[cut], options)
        chain.Draw(var + ">>h_tmp_%s_%s" % (icut, ivar), cuts[cut], options)
        h = ROOT.gDirectory.Get("h_tmp_%s_%s" % (icut, ivar))
        h.SetTitle("")
        h00 = ROOT.gDirectory.Get("h00_tmp_%s_%s" % (icut, ivar))
        h00.SetTitle("")
        h01 = ROOT.gDirectory.Get("h01_tmp_%s_%s" % (icut, ivar))
        h01.SetTitle("")
        h02 = ROOT.gDirectory.Get("h02_tmp_%s_%s" % (icut, ivar))
        h02.SetTitle("")
        if len(var.split(":")) > 1:
            c1.SetLogy(0)
#            h.SetTitle(";" + var.split(":")[1] + ";" + var.split(":")[0])
            h.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h.SetContour(1000)
            h00.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h00.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h00.SetContour(1000)
            h01.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h01.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h01.SetContour(1000)
            h02.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h02.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h02.SetContour(1000)
#            if vars[var] == "nSaturatedStrips_vs_lumi":
#                h.SetMaximum(1.0e-6)
#                h.SetMinimum(1.0e-7)
#                h.GetYaxis().SetRangeUser(5.0e-7, 5.0e-6)
#                c1.Update()
        else:
            c1.SetLogy(1)
            h.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h00.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h00.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h01.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h01.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h02.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            h02.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            h.SetLineWidth(2)
            h00.SetLineWidth(2)
            h01.SetLineWidth(2)
            h02.SetLineWidth(2)
            h00.SetLineColor(ROOT.kRed+1)
            h01.SetLineColor(ROOT.kGreen+1)
            h02.SetLineColor(ROOT.kBlue+1)
            err = ROOT.Double(0)
            norm = h.IntegralAndError(1, h.GetNbinsX(), err)
            norm00 = h00.IntegralAndError(1, h00.GetNbinsX(), err)
            norm01 = h01.IntegralAndError(1, h01.GetNbinsX(), err)
            norm02 = h02.IntegralAndError(1, h02.GetNbinsX(), err)
            print norm, norm00, norm01, norm02
            print h.GetMean(1), h00.GetMean(1), h01.GetMean(1), h02.GetMean(1)
            h00.Scale(norm / float(norm00))
            h01.Scale(norm / float(norm01))
            h02.Scale(norm / float(norm02))
            h00.Draw("same")
            h01.Draw("same")
            h02.Draw("same")
            h.Draw("same") # draw data on top
#            h.GetXaxis().SetTitle(vars[var][1])
        latexLabel = TLatex()
        latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
        latexLabel.SetNDC()
        latexLabel.SetTextFont(42) # helvetica
        latexLabel.DrawLatex(0.27, 0.96, cut)
        legend = TLegend(0.45, 0.72, 0.80, 0.93, "")
        legend.SetFillColor(ROOT.kWhite)
        legend.SetLineColor(ROOT.kWhite)
        legend.SetShadowColor(ROOT.kWhite)
        legend.AddEntry(h.GetName(), "2015 data", "l")
        legend.AddEntry(h00.GetName(), "SIM default", "l")
        legend.AddEntry(h01.GetName(), "SIM p_{HIP} = 1e-03, #tau_{APV} = 700 ns", "l")
        legend.AddEntry(h02.GetName(), "SIM p_{HIP} = 1e-03, #tau_{APV} = 1400 ns", "l")
        legend.Draw()
        c1.Update()
        c1.Print(plotdir + "/" + vars[var][0] + "_" + cut + ".png")
        c1.Print(plotdir + "/" + vars[var][0] + "_" + cut + ".pdf")
# now with profiles for 2D
        if len(var.split(":")) > 1:
            p = h.ProfileX()
            p00 = h00.ProfileX()
            p00.SetMarkerStyle(21)
            p00.SetMarkerColor(ROOT.kRed+1)
            p00.SetLineColor(ROOT.kRed+1)
            p01 = h01.ProfileX()
            p01.SetMarkerStyle(22)
            p01.SetMarkerColor(ROOT.kGreen+1)
            p01.SetLineColor(ROOT.kGreen+1)
            p02 = h02.ProfileX()
            p02.SetMarkerStyle(22)
            p02.SetMarkerColor(ROOT.kBlue+1)
            p02.SetLineColor(ROOT.kBlue+1)
#            if len(vars[var]) > 2:
#                p.GetYaxis().SetRangeUser(vars[var][2][0], vars[var][2][1])
            p.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            p.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            p00.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            p00.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            p01.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            p01.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            p02.GetYaxis().SetTitle(vars[var][1].split(':')[0])
            p02.GetXaxis().SetTitle(vars[var][1].split(':')[1])
            p.Draw()
            p00.Draw("same")
            p01.Draw("same")
            p02.Draw("same")
            p.Draw("same") # data on top of the others
            latexLabel = TLatex()
            latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
            latexLabel.SetNDC()
            latexLabel.SetTextFont(42) # helvetica
            latexLabel.DrawLatex(0.27, 0.96, cut)
            legend = TLegend(0.45, 0.72, 0.80, 0.93, "")
            legend.SetFillColor(ROOT.kWhite)
            legend.SetLineColor(ROOT.kWhite)
            legend.SetShadowColor(ROOT.kWhite)
            legend.AddEntry(p.GetName(), "2015 data", "lp")
            legend.AddEntry(p00.GetName(), "SIM default", "lp")
            legend.AddEntry(p01.GetName(), "SIM p_{HIP} = 1e-03, #tau_{APV} = 700 ns", "lp")
            legend.AddEntry(p02.GetName(), "SIM p_{HIP} = 1e-03, #tau_{APV} = 1400 ns", "lp")
            legend.Draw()
            c1.Update()
            c1.Print(plotdir + "/profileX_" + vars[var][0] + "_" + cut + ".png")
            c1.Print(plotdir + "/profileX_" + vars[var][0] + "_" + cut + ".pdf")

