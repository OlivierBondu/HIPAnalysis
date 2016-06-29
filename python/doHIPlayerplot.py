#!/bin/env python
# Python imports
import os
import numpy as np
# File location
outdir = "/storage/data/cms"
eosdir = "store/user/obondu/CRAB_PrivateMC/crab_HIPAnalysis/"
taskdir = "160616_162801/0000/"
#outdir = '/home/fynu/obondu/TRK/CMSSW_7_4_15/src'
#eosdir = 'CalibTracker/HIPAnalysis/'
#taskdir = ''
plotdir = "plots_160620_perLayer"
# ROOT setup
import ROOT
from ROOT import TChain, TCanvas, TLatex
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.TGaxis.SetMaxDigits(3)

chain = TChain("layertree")
print os.path.join(outdir, eosdir, taskdir) + "output_*.root"
#chain.Add(os.path.join(outdir, eosdir, taskdir) + "output_1.root")
chain.Add(os.path.join(outdir, eosdir, taskdir) + "output_*.root")
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

layers = []
#layers += ["TIDP_D%i" % i for i in xrange(1,4)]
#layers += ["TIDM_D%i" % i for i in xrange(1,4)]
#layers += ["TECP_W%i" % i for i in xrange(1,10)]
#layers += ["TECM_W%i" % i for i in xrange(1,10)]
#layers += ["TOB_L%i" % i for i in xrange(1,7)]
layers += ["TOB_L%i" % i for i in xrange(1,2)]
#layers += ["TIB_L%i" % i for i in xrange(1,5)]

plots = {
"meanChargeoverpath__": {
    "name": "meanChargeoverpath",
    "title": "#Events:< charge / path >",
    "binning": "(80, 100, 900)",
    "norm": "1",
    "ylog": False,
    },
#"meanChargeoverpath__:bx__": {
#    "name": "meanChargeoverpath_vs_bx", 
#    "title": "< charge / path >:bx",
#    "binning": "(35, 0, 3500, 500, 0, 2000)"
#    },
}

runs = {
257400: {
    "color": ROOT.kRed+1,
    "marker": 20,
    },
257487: {
    "color": ROOT.kMagenta+1,
    "marker": 21,
    },
257613: {
    "color": ROOT.kBlue+1,
    "marker": 22,
    },
257645: {
    "color": ROOT.kCyan+1,
    "marker": 23,
    },
257822: {
    "color": ROOT.kGreen+1,
    "marker": 24,
    },
258158: {
    "color": ROOT.kYellow+1,
    "marker": 25,
    },
258177: {
    "color": ROOT.kOrange+1,
    "marker": 26,
    },
260627: {
    "color": ROOT.kPink+1,
    "marker": 27,
    },
}

cuts = {
#"allTracker": "1", 
}
for x in layers:
    cuts[x] = 'layer__ == \"%s\"' % (x)
h = {}
p = {}

for icut, cut in enumerate(cuts):
    print "cut= ", cut
    for iplot, plot in enumerate(plots):
        print "\tplot= ", plot
        options = ""
        if ":" in plot:
            options = "colznum"
        binning = plots[plot].get('binning', '')
        for irun, run in enumerate(runs):
            print "\t\trun= ", run
            totalcut = '(%s) && (run__ == %i)' % (cuts[cut], run)
            if irun > 0 and ':' not in plot:
                options += 'SAME'
            hname = "h_tmp_%s_%s_%s" % (icut, iplot, irun)
            chain.Draw(plot + ">>%s%s" % (hname, binning), totalcut, options)
            h[hname] = ROOT.gDirectory.Get(hname)
            h[hname].SetLineColor(runs[run]['color'])
            h[hname].SetTitle("")
            extrafilename = ''
            if ':' in plot: # this is a 2D plot
                h[hname].SetContour(1000) # for prettier contours
            norm = plots[plot].get('norm', None)
            if norm == '1':
                h[hname].Scale(1. / chain.GetEntries(totalcut))
                h[hname].GetYaxis().SetTitle('Norm. to unity')
            else:
                h[hname].GetYaxis().SetTitle(plots[plot]['title'].split(':')[0])
            h[hname].GetXaxis().SetTitle(plots[plot]['title'].split(':')[1])
            h[hname].SetDirectory(0)
            if ':' in plot:
                p[hname] = h[hname].ProfileX()
                p[hname].SetDirectory(0)
            h[hname].Draw(options)
        latexLabel = TLatex()
        latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
        latexLabel.SetNDC()
        latexLabel.SetTextFont(42) # helvetica
        latexLabel.DrawLatex(0.27, 0.96, cut)
        if plots[plot].get('ylog', False):
            c1.SetLogy(1)
            extrafilename += '_log'
        else:
            c1.SetLogy(0)
        c1.Print(plotdir + "/" + plots[plot]['name'] + "_" + cut + extrafilename + ".png")
        c1.Print(plotdir + "/" + plots[plot]['name'] + "_" + cut + extrafilename + ".pdf")
        c1.Print(plotdir + "/" + plots[plot]['name'] + "_" + cut + extrafilename + ".root")
        c1.Clear()

# now with profiles for 2D
        print "\tprofileplot= ", plot
        if ':' not in plot:
            continue
        for irun, run in enumerate(runs):
            print "\t\trun= ", run
            hname = "h_tmp_%s_%s_%s" % (icut, iplot, irun)
#            print h[hname], h[hname].GetName(), h[hname].GetTitle(), h[hname].GetEntries()
#            options = ''
#            if irun > 0:
#                options = 'd'
#            p[hname] = h[hname].ProfileX() #"%s_PFX" % (hname), 1, -1, options)
#            print p[hname], p[hname].GetName(), p[hname].GetTitle(), p[hname].GetEntries()
            p[hname].GetYaxis().SetTitle(plots[plot]['title'].split(':')[0])
            p[hname].GetXaxis().SetTitle(plots[plot]['title'].split(':')[1])
            p[hname].SetMarkerColor(runs[run]['color'])
            p[hname].SetMarkerStyle(runs[run]['marker'])
            p[hname].SetMinimum(250)
            p[hname].SetMaximum(450)
            options = ''
            if irun > 0:
                options = 'SAME'
#            print 'options= ', options
            p[hname].Draw(options)
            ROOT.gPad.Modified()
            ROOT.gPad.Update()
            # end of loop over runs
        c1.Print(plotdir + "/profileX_" + plots[plot]['name'] + "_" + cut + ".png")
        c1.Print(plotdir + "/profileX_" + plots[plot]['name'] + "_" + cut + ".pdf")
        c1.Print(plotdir + "/profileX_" + plots[plot]['name'] + "_" + cut + ".root")
        c1.Clear()

