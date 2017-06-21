#!/bin/env python
# Python imports
import os
import json
import numpy as np
import collections
# File location
#histdir = "/home/fynu/obondu/TRK/CMSSW_7_4_15/src/CalibTracker/HIPAnalysis/python/test_condor/condor/output/"
#histfile = "histos.root"
histdir = "/home/fynu/obondu/TRK/CMSSW_7_4_15/src/CalibTracker/HIPAnalysis/"
histfile = "histos_APVsettings_StdBunch_v3.root"

plotdir = "160902_perLayer"
# ROOT setup
import ROOT
from ROOT import TFile, TCanvas, TLatex, TLegend
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
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
#layers += ["TIDP_D%i" % i for i in xrange(1,4)]
#layers += ["TIDM_D%i" % i for i in xrange(1,4)]
#layers += ["TECP_W%i" % i for i in xrange(1,10)]
#layers += ["TECM_W%i" % i for i in xrange(1,10)]
#layers += ["TOB_L%i" % i for i in xrange(1,7)]
#layers += ["TIB_L%i" % i for i in xrange(1,5)]
layers = ["TOB_L%i" % i for i in xrange(1,2)] # to do only TOB_L1
#lumisections = [x * 100 for x in xrange(0,20)]
#lumisections = [x * 100 for x in xrange(0,5)]
lumisections = [
        [1,100],
    ]

print 'layers= ', layers
print 'lumisections= ', lumisections

runs = collections.OrderedDict()
#runs[257400] = {
#    "color": ROOT.kRed+1,
#    "marker": 20,
#    "intL": "62.19 /pb",
#    "initialLumi": "2.11e33 cm^{-2}/s",
#    "date": "15/09/24",
#    }
#runs[257487] = {
#    "color": ROOT.kMagenta+1,
#    "marker": 21,
#    "intL": "66.38 /pb",
#    "initialLumi": "2.84e33 cm^{-2}/s",
#    "date": "15/09/25",
#    }
#runs[257613] = {
#    "color": ROOT.kBlue+1,
#    "marker": 22,
#    "intL": "78.31 /pb",
#    "initialLumi": "2.63e33 cm^{-2}/s",
#    "date": "15/09/27",
#    }
#runs[257645] = {
#    "color": ROOT.kCyan+1,
#    "marker": 23,
#    "intL": "64.85 /pb",
#    "initialLumi": "2.91e33 cm^{-2}/s",
#    "date": "15/09/27",
#    }
#runs[257822] = {
#    "color": ROOT.kMagenta+1,
#    "marker": 21,
#    "intL": "77.92 /pb",
#    "initialLumi": "2.64e33 cm^{-2}/s",
#    "date": "15/09/29",
#    }
#runs[258158] = {
#    "color": ROOT.kBlue+1,
#    "marker": 22,
#    "intL": "108.77 /pb",
#    "initialLumi": "3.02e33 cm^{-2}/s",
#    "date": "15/10/02",
#    }
#runs[258177] = {
#    "color": ROOT.kOrange+1,
#    "marker": 26,
#    "intL": "120.82 /pb",
#    "initialLumi": "2.78e33 cm^{-2}/s",
#    "date": "15/10/03",
#    }
#runs[260627] = {
#    "color": ROOT.kBlue,
#    "marker": 23,
#    "intL": "186.11 /pb",
#    "initialLumi": "5.22e33 cm^{-2}/s",
#    "date": "15/11/02",
#    }

#runs[274968] = {
#    "color": ROOT.kGreen+1,
#    "marker": 24,
#    "intL": "192.10 /pb",
#    "initialLumi": "7.88e33 cm^{-2}/s",
#    "date": "15/06/12",
#    }

runs[278769] = {
    "color": ROOT.kGreen+1,
    "marker": 24,
    "intL": "192.10 /pb",
    "initialLumi": "7.88e33 cm^{-2}/s",
    "date": "15/06/12",
    "comments": "LS 1-100 ; new APV settings",
    }

runs[278770] = {
    "color": ROOT.kBlue+1,
    "marker": 25,
    "intL": "192.10 /pb",
    "initialLumi": "7.88e33 cm^{-2}/s",
    "date": "15/06/12",
    "comments": "LS 1-100 ; old APV settings",
    }

allInstLumi = {}
with open('live_lumi.json') as f:
    allInstLumi = json.load(f)

instLumi = {}
for k in runs:
    instLumi[k] = {l: i / 1000. for r, l, i in allInstLumi[u'data'] if r == k}

if 274968 in runs and len(instLumi[274968]) == 0:
    instLumi[274968] = {}
    with open("274968.csv") as f:
        for line in f:
            if '#' in line:
                continue
#            print line.split(',')
            r, l, t, b, e, delivered, recorded, pu, source = line.split(',')
            instLumi[274968][int(l.split(':')[0])] = float(recorded) / 1000.
    
#print allInstLumi
#print instLumi[274968][100], "%.1f" % instLumi[274968][100]

#raise AssertionError

f = TFile(os.path.join(histdir, histfile))
def GetKeyNames( self, dir = "" ):
        self.cd(dir)
        return [key.GetName() for key in ROOT.gDirectory.GetListOfKeys()]
TFile.GetKeyNames = GetKeyNames

keyList = f.GetKeyNames('')
#print "\nKeys in file:", keyList
#for k in keyList:
#    print f.Get(k).ClassName(), k

plots = collections.OrderedDict()
#plots['meanChargeoverpath_vs_bx_zoomed'] = {
#        'histname': 'h_chargeoverpath_vs_bx',
#        'class': 'TH2',
#        'y-max': 800,
#        'y-min': 200,
#        'x-min': 50,
#        'x-max': 170,
#        'x-title': 'bx number',
#        'y-title': 'charge / cm',
#        'rebin': 1,
#    }
#plots['chargeoverpath_vs_bx'] = {
#        'histname': 'h_chargeoverpath_vs_bx',
#        'class': 'TH2',
#        'rebin': 10,
#        'y-max': 800,
#        'y-min': 200,
#        'x-min': 0,
#        'x-max': 3600,
#        'x-title': 'bx number',
#        'y-title': 'charge / cm',
#    }
plots['chargeoverpath'] = {
        'histname': 'h_chargeoverpath',
        'class': 'TH1',
        'norm': '1',
        'x-min': 0,
        'x-max': 1000,
        'xrebin': 10,
        'y-max': 0.06,
        'y-log': False,
#        'y-max': 9.0,
#        'y-log': True,
        'legendColumns': 1,
        'x-title': 'charge / cm',
    }
bx_list = [60] #, 116, 199, 255, 338, 394] #, 477, 533, 616, 672, 803, 589, 942]
bxs = []
#bxs = ['0-3600']
bxs += ["%i-%i" % (x   , x+16) for x in bx_list]
bxs += ["%i-%i" % (x+16, x+32) for x in bx_list]
bxs += ["%i-%i" % (x+32, x+48) for x in bx_list]
#bxs += ["%i-%i" % (x   , x+24) for x in bx_list]
#bxs += ["%i-%i" % (x+24, x+48) for x in bx_list]

for ilayer, layer in enumerate(layers):
    for iplot, plot in enumerate(plots):
        print "\nPLOT %i / %i" % (
                iplot
                + ilayer * len(plots)
                + 1
            , len(layers) * len(plots))
        # Do TH2 histos
        plotname = 'h_%s_%s' % (plot, layer)
        if 'TH2' in plots[plot]['class']:
            c2.cd()
            legend = TLegend(0.25, 0.72, 0.80, 0.93, "")
            legend.SetNColumns(2)
            legend.SetFillColor(ROOT.kWhite)
            legend.SetLineColor(ROOT.kWhite)
            legend.SetShadowColor(ROOT.kWhite)
            for irun, run in enumerate(runs):
                for ilumisection, lumisection in enumerate(lumisections):
                    for ibx, bx in enumerate(bxs):
#                    for ibx, bx in enumerate(bx_list):
                        for k in keyList:
                            if plots[plot]['histname'] not in k:
                                continue
                            if layer not in k or str(run) not in k:
                                continue
#                        if 'LS_%i-%i_%s' % (lumisection[0], lumisection[1], layer) not in k:
                            if '_%i-%i_%s' % (lumisection[0], lumisection[1], layer) not in k:
                                continue
                            if bx not in k:
                                continue
                            h = f.Get(k)
                            if h.GetEntries() == 0:
#                            print 'empty histo, skipping'
                                continue
                            if 'TH2' not in h.ClassName():
                                continue
                            drawoptions = ''
                            print '\t', layer, run, h.ClassName(), k
                            if 'rebin' in plots[plot]:
                                h.RebinX(plots[plot]['rebin'])
    #                            print "rebinning"
                            p = h.ProfileX()
                            p.SetLineColor(runs[run]['color'] + ilumisection + ibx)
                            p.SetMarkerColor(runs[run]['color'] + ilumisection + ibx)
                            p.SetMarkerStyle(runs[run]['marker'] + ilumisection + ibx)
                            p.GetYaxis().SetTitle(h.GetYaxis().GetTitle())
                            if 'x-title' in plots[plot]:
                                p.GetXaxis().SetTitle(plots[plot]['x-title'])
                            if 'y-title' in plots[plot]:
                                p.GetYaxis().SetTitle(plots[plot]['y-title'])
                            if 'y-min' in plots[plot]:
                                p.SetMinimum(plots[plot]['y-min'])
                            if 'y-max' in plots[plot]:
                                p.SetMaximum(plots[plot]['y-max'])
                            if 'x-max' in plots[plot]:
                                p.GetXaxis().SetRangeUser(plots[plot]['x-min'], plots[plot]['x-max'])
                            c2.SetGrid()
                            if plots[plot].get('y-log', False):
                                c2.SetLogy(1)
                            else:
                                c2.SetLogy(0)
                            if irun > 0 or ilumisection > 0 or ibx > 0:
                                drawoptions ='same'
                            legend.SetHeader(layer)
                            p.Draw(drawoptions)
                            legend.AddEntry(p.GetName(), '%i %s bx:%s' % (run, runs[run]['comments'], bx), 'lp')
#                        legend.AddEntry(p.GetName(), '%i %s' % (run, runs[run]['initialLumi']), 'lp')
#                        legend.AddEntry(p.GetName(), '%i LS %i-%i (%.2f - %.2f e33 cm^{-2}/s)' % (run, lumisection[0], lumisection[1], instLumi[run][lumisection[0]], instLumi[run][lumisection[1]]), 'lp')
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        # end of loop over histos
                    # end of loop over bx intervals
                # end of loop of lumisections
            # end of loop over runs
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
        # Do TH1 histos
        if 'TH1' in plots[plot]['class']:
            c1.cd()
            legend = TLegend(0.15, 0.72, 0.80, 0.93, "")
            legend.SetNColumns(2)
            legend.SetFillColor(ROOT.kWhite)
            legend.SetLineColor(ROOT.kWhite)
            legend.SetShadowColor(ROOT.kWhite)
            for irun, run in enumerate(runs):
                for ilumisection, lumisection in enumerate(lumisections):
                    for ibx, bx in enumerate(bxs):
#                    for ibx, bx in enumerate(bx_list):
                        for k in keyList:
                            if plot not in k:
                                continue
                            if layer not in k or str(run) not in k:
                                continue
#                        if 'LS_%i-%i_%s' % (lumisection[0], lumisection[1], layer) not in k:
                            if '_%i-%i_%s' % (lumisection[0], lumisection[1], layer) not in k:
                                continue
                            if bx not in k:
                                continue
                            h = f.Get(k)
                            if h.GetEntries() == 0:
#                            print 'empty histo, skipping'
                                continue
                            if 'TH1' not in h.ClassName():
                                continue
                            drawoptions = ''
                            print '\t', layer, run, bx, h.ClassName(), k
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
                        #legend.AddEntry(h.GetName(), '%i %s' % (run, runs[run]['initialLumi']), 'l')
#                        legend.AddEntry(h.GetName(), '%i LS %i-%i (%.2f - %.2f e33 cm^{-2}/s)' % (run, lumisection[0], lumisection[1], instLumi[run][lumisection[0]], instLumi[run][lumisection[1]]), 'l')
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        # end of loop over histos
                    # end of loop over bx intervals
                # end of loop of lumisections
            # end of loop over runs
            latexLabel = TLatex()
            latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
            latexLabel.SetNDC()
            latexLabel.SetTextFont(42) # helvetica
#            latexLabel.DrawLatex(0.27, 0.96, layer)
            legend.Draw()
            c1.Print(plotdir + "/" + plotname + ".png")
            c1.Print(plotdir + "/" + plotname + ".pdf")
            c1.Clear()
            # end of work on TH2
        # end of loop over runs
    # end of loop over plots
# end of loop over layer 


