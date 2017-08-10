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
# File location
# CRAB output dir: /storage/data/cms/store/user/obondu/CRAB_PrivateMC/crab_CalibTreesLayerAnalysis/170622_161745/0000/
histdir = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test"
histfile = "histos.root"
run = 299061
DEBUG = True

plotdir = "170809_SoN_%i" % run
# ROOT setup
import ROOT
from ROOT import TFile, TCanvas, TLatex, TLegend
#ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.TGaxis.SetMaxDigits(3)


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

edges = data['edges']
if DEBUG:
    print 'DEBUG:\tedges= ', edges

print 'layers= ', layers
print 'lumisections= ', lumisections

runs = collections.OrderedDict()
runs[run] = {
    "color": ROOT.kBlue+1,
    "marker": 24,
    "intL": "43.1 /pb",
    "initialLumi": "2.81e33 cm^{-2}/s",
    "date": "06/06/17",
    "comments": "",
    }

filepath = os.path.join(histdir, histfile)
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
#plots['h_ClusterStoN_vs_bx'] = {
#        'histname': 'h_ClusterStoN_vs_bx',
#        'class': 'TH2',
##        'rebin': 10,
#        'y-min': 20,
#        'y-max': 70,
##        'x-min': 0,
##        'x-max': 3600,
#        'x-custom': True,
#        'x-title': 'bx number',
#        'y-title': 'signal / noise',
#    }
plots['h_ClusterStoN_vs_bx_fit_lxg'] = {
        'histname': 'h_ClusterStoN_vs_bx_fit_lxg',
        'class': 'TGraphAssymmErrors',
        'y-min': 0,
        'y-max': 120,
        'x-custom': False,
        'x-title': 'bx number',
        'y-title': 'signal / noise',
    }
#plots['ClusterStoN'] = {
#        'histname': 'h_ClusterStoN',
#        'class': 'TH1',
#        'norm': '1',
#        'x-min': 0,
#        'x-max': 200,
#        'xrebin': 5,
#        'y-max': 0.255,
#        'y-log': False,
##        'y-max': 9.0,
##        'y-log': True,
#        'legendColumns': 1,
#        'x-title': 'signal / noise',
#    }
bxs_th2 = ['0-3600']
bxs_th1 = ['1001-1006']

ymin = None
ymax = None
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
            c2.cd()
            legend = TLegend(0.25, 0.72, 0.80, 0.93, "")
            legend.SetNColumns(2)
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
                            if DEBUG:
                                print 'DEBUG:\tkey= ', k
                                print 'DEBUG:\thistname= ', plots[plot]['histname']
                                print 'DEBUG:\tnEntries= ', h.GetEntries()
                            drawoptions = ''
                            if 'rebin' in plots[plot]:
                                h.RebinX(plots[plot]['rebin'])
                                if DEBUG:
                                    print "DEBUG:\trebinning"
                            if plots[plot]['x-custom']:
                                if DEBUG:
                                    print 'DEBUG:\tcustom rebinning (edges)'
                                h.rebinX(edges)
                            p = h.ProfileX()
                            p.SetLineColor(runs[run]['color'] + ilumisection + ibx*2)
                            p.SetMarkerColor(runs[run]['color'] + ilumisection + ibx*2)
                            p.SetMarkerStyle(runs[run]['marker'] + ilumisection + ibx*2)
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
                            if 'x-max' in plots[plot]:
                                p.GetXaxis().SetRangeUser(plots[plot]['x-min'], plots[plot]['x-max'])
                            c2.SetGrid()
                            if plots[plot].get('y-log', False):
                                c2.SetLogy(1)
                            else:
                                c2.SetLogy(0)
                            if irun > 0 or ilumisection > 0 or ibx > 0:
                                drawoptions += 'same'
                            legend.SetHeader(layer)
                            p.Draw(drawoptions)
                            legend.AddEntry(p.GetName(), '%i %s bx:%s' % (run, runs[run]['comments'], bx), 'lp')
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        # end of loop over histos
                    # end of loop over bx intervals
                # end of loop of lumisections
            # end of loop over runs
            mypoly = {}
            for i in xrange(0, len(edges), 2):
                if i+1 >= len(edges):
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
            c2.cd()
            legend = TLegend(0.25, 0.72, 0.80, 0.93, "")
            legend.SetNColumns(2)
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
                                h.rebinX(edges)
                            h.SetLineColor(runs[run]['color'] + ilumisection + ibx*2)
                            h.SetMarkerColor(runs[run]['color'] + ilumisection + ibx*2)
                            h.SetMarkerStyle(runs[run]['marker'] + ilumisection + ibx*2)
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
                            if 'x-max' in plots[plot]:
                                h.GetXaxis().SetRangeUser(plots[plot]['x-min'], plots[plot]['x-max'])
                            c2.SetGrid()
                            if plots[plot].get('y-log', False):
                                c2.SetLogy(1)
                            else:
                                c2.SetLogy(0)
                            if irun > 0 or ilumisection > 0 or ibx > 0:
                                drawoptions += 'same'
                            legend.SetHeader(layer)
                            h.Draw(drawoptions)
                            legend.AddEntry(h.GetName(), '%i %s bx:%s' % (run, runs[run]['comments'], bx), 'lp')
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        # end of loop over histos
                    # end of loop over bx intervals
                # end of loop of lumisections
            # end of loop over runs
            mypoly = {}
            for i in xrange(0, len(edges), 2):
                if i+1 >= len(edges):
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
            legend = TLegend(0.15, 0.72, 0.80, 0.93, "")
            legend.SetNColumns(2)
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
                            h.SetLineColor(runs[run]['color'] + ilumisection + ibx)
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
                                drawoptions ='same'
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
                            legend.AddEntry(h.GetName(), '%i %s bx:%s' % (run, runs[run]['comments'], bx), 'l')
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
            # end of work on TH2
        # end of loop over runs
    # end of loop over plots
# end of loop over layer 


