#!/bin/env python
# Python imports
import os
import sys
import json
import numpy as np
import collections
from array import array
import th2_rebin_numpy
import CalibTracker.HIPAnalysis.utils as utils
import copy
import bisect
# ROOT setup
import ROOT
from ROOT import TFile, TCanvas, TLatex, TLegend
#ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.TGaxis.SetMaxDigits(3)

# File location
# CRAB output dir: /storage/data/cms/store/user/obondu/CRAB_PrivateMC/crab_CalibTreesLayerAnalysis/170622_161745/0000/
#histdir = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test"
#histfile = "histos.root"

histdir = '/storage/data/cms/store/user/obondu/CRAB_PrivateMC/'
histdir = '/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/python/'

# 296786
#color = ROOT.kBlue
#histfile = "crab_anEffAnalysis_run_296786_split_0/170814_153849/0000/histos_1.root"
#histfile = "crab_anEffAnalysis_run_296786_split_12/170814_153853/0000/histos_1.root"
#histfile = "crab_anEffAnalysis_run_296786_split_24/170814_153858/0000/histos_1.root"
# 297722
#color = ROOT.kMagenta+1
#histfile = "crab_anEffAnalysis_run_297722_split_0/170814_153820/0000/histos_1.root"
#histfile = "crab_anEffAnalysis_run_297722_split_12/170814_153824/0000/histos_1.root"
#histfile = "crab_anEffAnalysis_run_297722_split_24/170814_153829/0000/histos_1.root"
# 299061
#color = ROOT.kRed+1
#histfile = "crab_anEffAnalysis_run_299061_split_0/170814_153834/0000/histos_1.root"
#histfile = "crab_anEffAnalysis_run_299061_split_12/170814_153839/0000/histos_1.root"
#histfile = "crab_anEffAnalysis_run_299061_split_24/170814_153844/0000/histos_1.root"
# 301165
color = ROOT.kGreen+1
histfile = "../test/histos_run_301165_split_0.root"
histfile = "../test/histos_run_301165_split_6.root"
histfile = "../test/histos_run_301165_split_12.root"
histfile = "../test/histos_run_301165_split_24.root"
#histfile = "crab_anEffAnalysis_run_301165_split_0/170815_164724/0000/histos_1.root"
#histfile = "crab_anEffAnalysis_run_301165_split_12/170815_164728/0000/histos_1.root"
#histfile = "crab_anEffAnalysis_run_301165_split_24/170815_164733/0000/histos_1.root"
#color = ROOT.kCyan+1
# FIXME: waiting for 300235

### 297503
###histfile = "crab_anEffAnalysis_run_297503_split_0/170814_153903/0000/histos_1.root"
###histfile = "crab_anEffAnalysis_run_297503_split_12/170814_153907/0000/histos_1.root"
###histfile = "crab_anEffAnalysis_run_297503_split_24/170814_153912/0000/histos_1.root"
### 297100
###histfile = "crab_anEffAnalysis_run_297100_split_0/170814_153806/0000/histos_1.root"
###histfile = "crab_anEffAnalysis_run_297100_split_24/170814_153815/0000/histos_1.root"

#task = histfile.split('/')[0]
#run = int(task.split('_')[3])
#SPLITTRAIN = int(task.split('_')[5])
task = histfile.split(".")[-2]
run = int(task.split('_')[2])
SPLITTRAIN = int(task.split('_')[4])
plotdir = "171006_SoN_%i_%i" % (run, SPLITTRAIN)
DEBUG = False
print run, SPLITTRAIN, plotdir


c1 = TCanvas()
c2 = TCanvas("c2", "c2", 1200, 600)
if not os.path.exists(plotdir):
    os.makedirs(plotdir)
# kBird palette
stops = np.array([0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
red = np.array([0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764])
green = np.array([0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832])
blue = np.array([0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539])
ROOT.TColor.CreateGradientColorTable(9, stops, red, green, blue, 255, 1)

layers = []
layers = ["TOB_L%i" % i for i in xrange(1,2)] # to do only TOB_L1
lumisections = [
        [1, 100],
    ]

jsonf = utils.get_outfile(run, None)
if not jsonf:
    sys.exit()
data = None
with open(jsonf, 'r') as f:
    data = json.load(f)

edges = data['edges'] + [3600]
edges = map(float, edges)
if DEBUG:
    print 'DEBUG:\tedges= ', edges

# construct train ranges to get the proper histograms
bxs = []
splitedges = [0]
for train in data['scheme']:
    if SPLITTRAIN > 0 and len(train) > SPLITTRAIN:
        for i in xrange(len(train) / SPLITTRAIN):
            bxs.append('%i-%i' % (train[i * SPLITTRAIN], train[(i + 1) * SPLITTRAIN - 1]))
            splitedges += [train[i * SPLITTRAIN], train[(i + 1) * SPLITTRAIN - 1]]
        if len(train) % SPLITTRAIN != 0:
            bxs.append('%i-%i' % (train[len(train) / SPLITTRAIN * SPLITTRAIN], train[-1]))
            splitedges += [train[len(train) / SPLITTRAIN * SPLITTRAIN], train[-1]]
    else:
        bxs.append('%i-%i' % (train[0], train[-1]))
        splitedges += [train[0], train[-1]]
# construct edge ranges for proper rebinning
splitedges = [0]
for b in bxs:
    tmp = map(int, b.split('-'))
    tmp[1] += 1
    splitedges += tmp
splitedges += [3600]
splitedges = sorted(list(set(splitedges)))
splitedges = map(float, splitedges)
if DEBUG:
    print 'DEBUG:\tsplitedges=', splitedges

print 'layers= ', layers
print 'lumisections= ', lumisections

runs = collections.OrderedDict()
runs[run] = {
    "color": color,
    "marker": 2,
    "intL": "43.1 /pb",
    "initialLumi": "2.81e33 cm^{-2}/s",
    "date": "06/06/17",
    "comments": "",
    }

filepath = os.path.join(histdir, histfile)
if DEBUG:
    print 'DEBUG:\tfile=', filepath
f = TFile(filepath)
def GetKeyNames( self, dir = "" ):
        self.cd(dir)
        return [key.GetName() for key in ROOT.gDirectory.GetListOfKeys()]
TFile.GetKeyNames = GetKeyNames

keyList = f.GetKeyNames('')
##print "\nKeys in file:", keyList
#for k in keyList:
#    if ('chargeoverpath' in k) and ('vs_bx' not in k):
#        print f.Get(k).ClassName(), k

plots = collections.OrderedDict()
xplots = {}
plots['h_ClusterStoN_vs_bx_zoom'] = {
        'histname': 'h_ClusterStoN_vs_bx',
        'class': 'TH2',
        'y-min': 10,
        'y-max': 70,
        'x-min': 0,
        'x-max': 500,
        'x-custom': True,
        'x-title': 'bx number',
        'y-title': 'signal / noise',
        'comments': 'mean and RMS',
    }
plots['h_ClusterStoN_vs_bx_fit_lpg_zoom'] = {
        'histname': 'h_ClusterStoN_vs_bx_fit_lpg',
        'class': 'TGraphAssymmErrors',
        'y-min': 20,
        'y-max': 26,
        'x-min': 0,
        'x-max': 500,
        'x-custom': False,
        'x-title': 'bx number',
        'y-title': 'signal / noise',
        'comments': 'max of Landau + Gaussian',
    }
plots['h_ClusterStoN_vs_bx_fit_lxg_zoom'] = {
        'histname': 'h_ClusterStoN_vs_bx_fit_lxg',
        'class': 'TGraphAssymmErrors',
        'y-min': 20,
        'y-max': 26,
        'x-min': 0,
        'x-max': 500,
        'x-custom': False,
        'x-title': 'bx number',
        'y-title': 'signal / noise',
        'comments': 'max of Landau #otimes Gaussian',
    }
plots['h_ClusterStoN_vs_bx'] = {
        'histname': 'h_ClusterStoN_vs_bx',
        'class': 'TH2',
        'y-min': 10,
        'y-max': 70,
        'x-min': 0,
        'x-max': 3600,
        'x-custom': True,
        'x-title': 'bx number',
        'y-title': 'signal / noise',
        'comments': 'mean and RMS',
    }
plots['h_ClusterStoN_vs_bx_fit_lxg'] = {
        'histname': 'h_ClusterStoN_vs_bx_fit_lxg',
        'class': 'TGraphAssymmErrors',
        'y-min': 20,
        'y-max': 26,
        'x-min': 0,
        'x-max': 3600,
        'x-custom': False,
        'x-title': 'bx number',
        'y-title': 'signal / noise',
        'comments': 'max of Landau #otimes Gaussian',
    }
plots['h_ClusterStoN_vs_bx_fit_lpg'] = {
        'histname': 'h_ClusterStoN_vs_bx_fit_lpg',
        'class': 'TGraphAssymmErrors',
        'y-min': 20,
        'y-max': 26,
        'x-min': 0,
        'x-max': 3600,
        'x-custom': False,
        'x-title': 'bx number',
        'y-title': 'signal / noise',
        'comments': 'max of Landau + Gaussian',
    }
plots['ClusterStoN'] = {
        'histname': 'h_ClusterStoN',
        'class': 'TH1',
        'norm': '1',
        'x-min': 0,
        'x-max': 200,
        'xrebin': 5,
        'y-max': 0.255,
        'y-log': False,
        'legendColumns': 1,
        'x-title': 'signal / noise',
        'comments': '',
    }
plots['RooPlot_ClusterStoN'] = {
        'histname': 'frame',
        'class': 'RooPlot',
        'comments': '',
}
bxs_th2 = ['0-3600']
#bxs_th1 = bxs[0:min(5, len(bxs))]
bxs_th1 = bxs[3:4]

ymin = None
ymax = None
xylegend = [0.25, 0.80, 0.65, 0.90]
ncollegend = 1
for ilayer, layer in enumerate(layers):
    if DEBUG: print 'DEBUG:\tLayer= ', layer
    for iplot, plot in enumerate(plots):
        print "\nPLOT %i / %i" % (
                iplot
                + ilayer * len(plots)
                + 1
            , len(layers) * len(plots))
        if DEBUG: 
            print 'DEBUG:\tplot= ', plot
        # Do TH2 histos
        plotname = 'h_%s_%s' % (plot, layer)
# IF TH2
        if 'TH2' in plots[plot]['class']:
            if DEBUG:
                print 'DEBUG:\tThis is a TH2 plot'
            atLeastOneHistoToDraw = False
            c2.cd()
            legend = TLegend(xylegend[0], xylegend[1], xylegend[2], xylegend[3], "")
            legend.SetNColumns(ncollegend)
            legend.SetFillColor(ROOT.kWhite)
            legend.SetLineColor(ROOT.kWhite)
            legend.SetShadowColor(ROOT.kWhite)
            for irun, run in enumerate(runs):
                for ilumisection, lumisection in enumerate(lumisections):
                    for ibx, bx in enumerate(bxs_th2):
                        if DEBUG:
                            print 'DEBUG:\tbx= ', bx
                        for k in keyList:
                            if plots[plot]['histname'] not in k:
                                continue
                            if 'custom' in k:
                                continue
                            if layer not in k or str(run) not in k:
                                continue
                            if bx not in k:
                                continue
                            h = f.Get(k)
                            if not 'TH2' in h.ClassName():
                                continue
                            if h.GetEntries() == 0:
                                if DEBUG:
                                    print 'DEBUG:\tempty histo, skipping'
                                continue
                            atLeastOneHistoToDraw = True
                            if DEBUG:
                                print 'DEBUG:\tkey= ', k
                                print 'DEBUG:\thistname= ', plots[plot]['histname']
                                print 'DEBUG:\tnEntries= ', h.GetEntries()
                            drawoptions = ''
                            if 'rebin' in plots[plot]:
                                h.RebinX(plots[plot]['rebin'])
                                if DEBUG:
                                    print "DEBUG:\trebinning"
                            tmpsplitedges = copy.deepcopy(splitedges)
                            if 'x-max' in plots[plot] and 'x-min' in plots[plot]:
                                h.GetXaxis().SetRangeUser(plots[plot]['x-min'], plots[plot]['x-max'])
                                if plots[plot]['x-min'] not in tmpsplitedges:
                                    bisect.insort(tmpsplitedges, plots[plot]['x-min'])
                                if plots[plot]['x-max'] not in tmpsplitedges:
                                    bisect.insort(tmpsplitedges, plots[plot]['x-max'])
                                i = bisect.bisect_left(tmpsplitedges, plots[plot]['x-min'])
                                tmpsplitedges = tmpsplitedges[i:]
                                i = bisect.bisect(tmpsplitedges, plots[plot]['x-max'])
                                tmpsplitedges = tmpsplitedges[:i]
                            if plots[plot]['x-custom']:
                                if DEBUG:
                                    print 'DEBUG:\tcustom rebinning (edges)'
                                    print tmpsplitedges
                                h = h.rebinX(tmpsplitedges)
                            p = h.ProfileX()
                            p.SetLineColor(runs[run]['color'])
                            p.SetMarkerColor(runs[run]['color'])
                            p.SetMarkerStyle(runs[run]['marker'])
                            p.GetYaxis().SetTitle(h.GetYaxis().GetTitle())
                            if 'x-title' in plots[plot]:
                                p.GetXaxis().SetTitle(plots[plot]['x-title'])
                            if 'y-title' in plots[plot]:
                                p.GetYaxis().SetTitle(plots[plot]['y-title'])
                            if 'y-min' in plots[plot]:
                                p.SetMinimum(plots[plot]['y-min'])
                            if 'y-max' in plots[plot]:
                                p.SetMaximum(plots[plot]['y-max'])
                            ymin = p.GetMinimum()
                            ymax = p.GetMaximum()
                            if DEBUG:
                                print 'DEBUG:\tymin, ymax= ', ymin, ymax
#                            if 'x-max' in plots[plot] and 'x-min' in plots[plot]:
#                                p.GetXaxis().SetRangeUser(plots[plot]['x-min'], plots[plot]['x-max'])
                            c2.SetGrid()
                            if plots[plot].get('y-log', False):
                                c2.SetLogy(1)
                            else:
                                c2.SetLogy(0)
                            if irun > 0 or ilumisection > 0 or ibx > 0:
                                drawoptions += 'same'
                            legend.SetHeader(layer)
                            p.Draw(drawoptions)
                            legend.AddEntry(p.GetName(), '%i %s %s' % (run, runs[run]['comments'], plots[plot]['comments']), 'lp')
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        # end of loop over histos
                    # end of loop over bx intervals
                # end of loop of lumisections
            # end of loop over runs
            if atLeastOneHistoToDraw:
                mypoly = {}
                for i in xrange(0, len(edges), 2):
                    if i+1 >= len(edges):
                        continue
                    if ('x-max' in plots[plot] and 'x-min' in plots[plot] and
                            (edges[i] < plots[plot]['x-min'] or edges[i+1] > plots[plot]['x-max'])):
                        continue
                    x = array('f', [edges[i], edges[i+1], edges[i+1], edges[i]])
                    y = array('f', [ymin, ymin, ymax, ymax])
                    mypoly[i] = ROOT.TPolyLine(4, x, y)
                    mypoly[i].SetFillColorAlpha(ROOT.kGray, .35)
                    mypoly[i].SetLineColor(ROOT.kGray)
                    mypoly[i].SetLineWidth(0)
                    mypoly[i].Draw('fsame')
                ROOT.gPad.RedrawAxis()
                latexLabel = TLatex()
                latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
                latexLabel.SetNDC()
                latexLabel.SetTextFont(42) # helvetica
    #            latexLabel.DrawLatex(0.27, 0.96, layer)
                legend.Draw()
                c2.Print(plotdir + "/" + plotname + ".png")
                c2.Print(plotdir + "/" + plotname + ".pdf")
            c2.Clear()
            # end of work on TH2
        # Do TH2 histos
        plotname = 'h_%s_%s' % (plot, layer)
# IF TGRAPH
        if 'TGraph' in plots[plot]['class']:
            if DEBUG:
                print 'DEBUG:\tThis is a TGraph plot'
            atLeastOneHistoToDraw = False
            c2.cd()
            legend = TLegend(xylegend[0], xylegend[1], xylegend[2], xylegend[3], "")
            legend.SetNColumns(ncollegend)
            legend.SetFillColor(ROOT.kWhite)
            legend.SetLineColor(ROOT.kWhite)
            legend.SetShadowColor(ROOT.kWhite)
            for irun, run in enumerate(runs):
                for ilumisection, lumisection in enumerate(lumisections):
                    for ibx, bx in enumerate(bxs_th2):
                        if DEBUG:
                            print 'DEBUG:\tbx= ', bx
                        for k in keyList:
                            if plots[plot]['histname'] not in k:
                                continue
                            if 'custom' in k:
                                continue
                            if layer not in k or str(run) not in k:
                                continue
                            if bx not in k:
                                continue
                            h = f.Get(k)
                            if not 'TGraph' in h.ClassName():
                                continue
                            if h.GetN() == 0:
                                if DEBUG:
                                    print 'DEBUG:\tempty histo, skipping'
                                continue
                            atLeastOneHistoToDraw = True
                            if DEBUG:
                                print 'DEBUG:\tkey= ', k
                                print 'DEBUG:\thistname= ', plots[plot]['histname']
                                print 'DEBUG:\tnEntries= ', h.GetN()
                            drawoptions = 'ap'
                            if 'rebin' in plots[plot]:
                                h.RebinX(plots[plot]['rebin'])
                                if DEBUG:
                                    print "DEBUG:\trebinning"
                            if plots[plot]['x-custom']:
                                if DEBUG:
                                    print 'DEBUG:\tcustom rebinning (edges)'
                                    print splitedges
                                h = h.rebinX(splitedges)
                            h.SetLineColor(runs[run]['color'])
                            h.SetMarkerColor(runs[run]['color'])
                            h.SetMarkerStyle(runs[run]['marker'])
                            h.GetYaxis().SetTitle(h.GetYaxis().GetTitle())
                            if 'x-title' in plots[plot]:
                                h.GetXaxis().SetTitle(plots[plot]['x-title'])
                            if 'y-title' in plots[plot]:
                                h.GetYaxis().SetTitle(plots[plot]['y-title'])
                            if 'y-min' in plots[plot]:
                                h.SetMinimum(plots[plot]['y-min'])
                            if 'y-max' in plots[plot]:
                                h.SetMaximum(plots[plot]['y-max'])
                            ymin = h.GetMinimum()
                            ymax = h.GetMaximum()
                            if DEBUG:
                                print 'DEBUG:\tymin, ymax= ', ymin, ymax
                            if 'x-max' in plots[plot] and 'x-min' in plots[plot]:
                                h.GetXaxis().SetLimits(plots[plot]['x-min'], plots[plot]['x-max'])
                            c2.SetGrid()
                            if plots[plot].get('y-log', False):
                                c2.SetLogy(1)
                            else:
                                c2.SetLogy(0)
                            if irun > 0 or ilumisection > 0 or ibx > 0:
                                drawoptions += 'same'
                            legend.SetHeader(layer)
                            h.Draw(drawoptions)
                            legend.AddEntry(h.GetName(), '%i %s %s' % (run, runs[run]['comments'], plots[plot]['comments']), 'lp')
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        # end of loop over histos
                    # end of loop over bx intervals
                # end of loop of lumisections
            # end of loop over runs
            if atLeastOneHistoToDraw:
                mypoly = {}
                if DEBUG:
                    print 'DEBUG:\tymin, ymax=', ymin, ymax
                for i in xrange(0, len(edges), 2):
                    if i+1 >= len(edges):
                        continue
                    if ('x-max' in plots[plot] and 'x-min' in plots[plot] and
                            (edges[i] < plots[plot]['x-min'] or edges[i+1] > plots[plot]['x-max'])):
                        continue
                    x = array('f', [edges[i], edges[i+1], edges[i+1], edges[i]])
                    y = array('f', [ymin, ymin, ymax, ymax])
                    mypoly[i] = ROOT.TPolyLine(4, x, y)
                    mypoly[i].SetFillColorAlpha(ROOT.kGray, .35)
                    mypoly[i].SetLineColor(ROOT.kGray)
                    mypoly[i].SetLineWidth(0)
                    mypoly[i].Draw('fsame')
                ROOT.gPad.RedrawAxis()
                latexLabel = TLatex()
                latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
                latexLabel.SetNDC()
                latexLabel.SetTextFont(42) # helvetica
    #            latexLabel.DrawLatex(0.27, 0.96, layer)
                legend.Draw()
                c2.Print(plotdir + "/" + plotname + ".png")
                c2.Print(plotdir + "/" + plotname + ".pdf")
            c2.Clear()
            # end of work on TH2
# IF TH1
        # Do TH1 histos
        if 'TH1' in plots[plot]['class']:
            if DEBUG:
                print 'DEBUG:\tThis is a TH1 plot'
            c1.cd()
            legend = TLegend(xylegend[0], xylegend[1], xylegend[2], xylegend[3], "")
            legend.SetNColumns(ncollegend)
            legend.SetFillColor(ROOT.kWhite)
            legend.SetLineColor(ROOT.kWhite)
            legend.SetShadowColor(ROOT.kWhite)
            atLeastOneHistoToDraw = False
            for irun, run in enumerate(runs):
                for ilumisection, lumisection in enumerate(lumisections):
                    for ibx, bx in enumerate(bxs_th1):
                        if DEBUG:
                            print 'DEBUG:\tbx= ', bx
                        for k in keyList:
                            if plot not in k:
                                continue
                            if layer not in k or str(run) not in k:
                                continue
                            if bx not in k:
                                continue
                            h = f.Get(k)
                            if 'TH1' not in h.ClassName():
                                continue
                            if h.GetEntries() == 0:
                                if DEBUG:
                                    print 'DEBUG:\tempty histo, skipping'
                                continue
                            else:
                                if DEBUG:
                                    print 'DEBUG:\tnEntries= %i' % h.GetEntries()
                            atLeastOneHistoToDraw = True
                            drawoptions = ''
                            if DEBUG:
                                print 'DEBUG:\t', layer, run, bx, h.ClassName(), k
    #                    h.RebinX(10)
                            h.SetLineColor(runs[run]['color'])
                            h.SetLineWidth(2)
                            norm = plots[plot].get('norm', None)
                            if 'x-title' in plots[plot]:
                                h.GetXaxis().SetTitle(plots[plot]['x-title'])
                            if 'y-title' in plots[plot]:
                                h.GetYaxis().SetTitle(plots[plot]['y-title'])
                            if norm == '1':
                                h.Scale(1. / h.GetEntries())
                                h.GetYaxis().SetTitle('Norm. to unity')
                            else:
                                h.GetYaxis().SetTitle(h.GetYaxis().GetTitle())
                            c1.SetGrid()
                            if plots[plot].get('y-log', False):
                                c1.SetLogy(1)
                            else:
                                c1.SetLogy(0)
                            if irun > 0 or ilumisection > 0 or ibx > 0:
                                drawoptions += 'same'
                                legend.SetHeader(layer)
                            if plots[plot].get('xrebin', None):
                                h.RebinX(plots[plot]['xrebin'])
                            if 'y-min' in plots[plot]:
                                h.SetMinimum(plots[plot]['y-min'])
                            if 'y-max' in plots[plot]:
                                h.SetMaximum(plots[plot]['y-max'])
                            if 'x-max' in plots[plot]:
                                h.GetXaxis().SetRangeUser(plots[plot]['x-min'], plots[plot]['x-max'])
                            if 'legendColumns' in plots[plot]:
                                legend.SetNColumns(plots[plot]['legendColumns'])
                            h.Draw(drawoptions)
                            legend.AddEntry(h.GetName(), '%i %s %s bxs:%s' % (run, runs[run]['comments'], plots[plot]['comments'], bx), 'l')
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        # end of loop over histos
                        if DEBUG:
                            print 'DEBUG:\tend of loop over histos'
                    # end of loop over bx intervals
                # end of loop of lumisections
            # end of loop over runs
            if atLeastOneHistoToDraw:
                latexLabel = TLatex()
                latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
                latexLabel.SetNDC()
                latexLabel.SetTextFont(42) # helvetica
    #            latexLabel.DrawLatex(0.27, 0.96, layer)
                legend.Draw()
                c1.Print(plotdir + "/" + plotname + ".png")
                c1.Print(plotdir + "/" + plotname + ".pdf")
            else:
                if DEBUG:
                    print 'DEBUG:\tNothing to Draw!'
            c1.Clear()
            # end of work on TH1
# IF RooPlot
        # Do RooPlot histos
        if 'RooPlot' in plots[plot]['class']:
            if DEBUG:
                print 'DEBUG:\tThis is a RooPlot plot'
            c1.cd()
            legend = TLegend(xylegend[0], xylegend[1], xylegend[2], xylegend[3], "")
            legend.SetNColumns(ncollegend)
            legend.SetFillColor(ROOT.kWhite)
            legend.SetLineColor(ROOT.kWhite)
            legend.SetShadowColor(ROOT.kWhite)
            atLeastOneHistoToDraw = False
            for irun, run in enumerate(runs):
                for ilumisection, lumisection in enumerate(lumisections):
                    for ibx, bx in enumerate(bxs_th1):
                        if DEBUG:
                            print 'DEBUG:\tbx= ', bx
                        for k in keyList:
                            if plots[plot]['histname'] not in k:
                                continue
                            if layer not in k or str(run) not in k:
                                continue
                            if bx not in k:
                                continue
                            h = f.Get(k)
                            if 'RooPlot' not in h.ClassName():
                                continue
                            drawoptions = ''
                            if DEBUG:
                                print 'DEBUG:\t', layer, run, bx, h.ClassName(), k
                            h.SetTitle('')
                            if 'x-title' in plots[plot]:
                                h.GetXaxis().SetTitle(plots[plot]['x-title'])
                            if 'y-title' in plots[plot]:
                                h.GetYaxis().SetTitle(plots[plot]['y-title'])
                            c1.SetGrid()
                            if plots[plot].get('y-log', False):
                                c1.SetLogy(1)
                            else:
                                c1.SetLogy(0)
                            h.Draw(drawoptions)
                            legend.AddEntry(p.GetName(), '%i %s %s' % (run, runs[run]['comments'], plots[plot]['comments']), 'l')
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        # end of loop over histos
                        if DEBUG:
                            print 'DEBUG:\tend of loop over histos'
                        latexLabel = TLatex()
                        latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
                        latexLabel.SetNDC()
                        latexLabel.SetTextFont(42) # helvetica
            #            latexLabel.DrawLatex(0.27, 0.96, layer)
#                        legend.Draw()
                        c1.Print(plotdir + "/" + plotname + ".png")
                        c1.Print(plotdir + "/" + plotname + ".pdf")
                        c1.Clear()
                    # end of loop over bx intervals
                # end of loop of lumisections
            # end of loop over runs
            # end of work on RooPlot
        # end of loop over runs
    # end of loop over plots
# end of loop over layer 


