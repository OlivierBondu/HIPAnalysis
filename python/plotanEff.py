#!/bin/env python
# Python imports
import os
import sys
import json
import numpy as np
import collections
from array import array
# File location
# CRAB output dir: /storage/data/cms/store/user/obondu/CRAB_PrivateMC/crab_CalibTreesLayerAnalysis/170622_161745/0000/
histdir = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test"
#histfile = "histos_custom_all_296173.root"
#histfile = "histos_custom_one_296173.root"
#histfile = "histos_custom_one_297673.root"
#histfile = "histos_custom_one_299061.root"
#histfile = "histos_custom_three_299061.root"
histfile = "histos.root"

#plotdir = "170718_perLayer"
#plotdir = "170718_perLayer_297673"
plotdir = "170718_perLayer_297674"
#plotdir = "170718_perLayer_299061"
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
        [1, 100],
    ]
#edges = [0, 1, 2, 41, 53, 183, 231, 266, 314, 349, 397, 1077, 1125, 1160, 1208, 1243, 1291, 1971, 2019, 2054, 2102, 2137, 2185, 2865, 2913, 2948, 2996, 3031, 3079, 3563, 3600]
edges = [0, 56, 104, 111, 159, 190, 238, 245, 293, 300, 348, 379, 427, 434, 482, 489, 537, 568, 616, 623, 671, 678, 726, 761, 809, 816, 864, 895, 943, 950, 998, 1005, 1053, 1084, 1132, 1139, 1187, 1194, 1242, 1273, 1321, 1328, 1376, 1383, 1431, 1462, 1510, 1517, 1565, 1572, 1620, 1655, 1703, 1710, 1758, 1789, 1837, 1844, 1892, 1899, 1947, 1978, 2026, 2033, 2081, 2088, 2136, 2167, 2215, 2222, 2270, 2277, 2325, 2356, 2404, 2411, 2459, 2466, 2514, 2549, 2597, 2604, 2652, 2683, 2731, 2738, 2786, 2793, 2841, 2872, 2920, 2927, 2975, 2982, 3030, 3061, 3109, 3116, 3164, 3171, 3219, 3250, 3298, 3305, 3353, 3360, 3408, 3563, 3600]
#edges = [0, 65, 113, 120, 168, 175, 223, 254, 302, 309, 357, 364, 412, 443, 491, 498, 546, 553, 601, 770, 818, 825, 873, 880, 928, 959, 1007, 1014, 1062, 1069, 1117, 1148, 1196, 1203, 1251, 1258, 1306, 1337, 1385, 1392, 1440, 1447, 1495, 1579, 1580, 1664, 1712, 1719, 1767, 1774, 1822, 1853, 1901, 1908, 1956, 1963, 2011, 2042, 2090, 2097, 2145, 2152, 2200, 2231, 2279, 2286, 2334, 2341, 2389, 2558, 2606, 2613, 2661, 2668, 2716, 2747, 2795, 2802, 2850, 2857, 2905, 2936, 2984, 2991, 3039, 3046, 3094, 3125, 3173, 3180, 3228, 3235, 3283, 3563, 3600]



print 'layers= ', layers
print 'lumisections= ', lumisections

runs = collections.OrderedDict()
runs[296173] = {
    "color": ROOT.kGreen+1,
    "marker": 24,
    "intL": "43.1 /pb",
    "initialLumi": "2.81e33 cm^{-2}/s",
    "date": "06/06/17",
    "comments": "",
    }
runs[297673] = {
    "color": ROOT.kBlue+1,
    "marker": 24,
    "intL": "43.1 /pb",
    "initialLumi": "2.81e33 cm^{-2}/s",
    "date": "06/06/17",
    "comments": "",
    }
runs[297674] = {
    "color": ROOT.kBlue+1,
    "marker": 24,
    "intL": "43.1 /pb",
    "initialLumi": "2.81e33 cm^{-2}/s",
    "date": "06/06/17",
    "comments": "",
    }
runs[299061] = {
    "color": ROOT.kRed+1,
    "marker": 24,
    "intL": "43.1 /pb",
    "initialLumi": "2.81e33 cm^{-2}/s",
    "date": "06/06/17",
    "comments": "",
}


f = TFile(os.path.join(histdir, histfile))
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
plots['h_ClusterStoN_vs_bx'] = {
        'histname': 'h_ClusterStoN_vs_bx_custom2',
        'class': 'TH2',
#        'rebin': 10,
        'y-min': 20,
        'y-max': 70,
        'x-min': 0,
        'x-max': 3600,
        'x-title': 'bx number',
        'y-title': 'signal / noise',
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
#        'y-max': 9.0,
#        'y-log': True,
        'legendColumns': 1,
        'x-title': 'signal / noise',
    }
#bx_list = [60] #, 116, 199, 255, 338, 394] #, 477, 533, 616, 672, 803, 589, 942]
#bxs = []
bxs = ['0-3600']
#bxs = ['100-400']
#bxs += ["%i-%i" % (x   , x+16) for x in bx_list]
#bxs += ["%i-%i" % (x+16, x+32) for x in bx_list]
#bxs += ["%i-%i" % (x+32, x+48) for x in bx_list]
#bxs += ["%i-%i" % (x   , x+24) for x in bx_list]
#bxs += ["%i-%i" % (x+24, x+48) for x in bx_list]

ymin = None
ymax = None
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
#                            if '_%i-%i_%s' % (lumisection[0], lumisection[1], layer) not in k:
#                                continue
                            if bx not in k:
                                continue
                            h = f.Get(k)
                            if h.GetEntries() == 0:
#                            print 'empty histo, skipping'
                                continue
                            print 'key= ', k
                            print plots[plot]['histname']
                            print layer
#                            print '_%i-%i_%s' % (lumisection[0], lumisection[1], layer)
                            print h.GetEntries()
                            print ''
                            print ''
                            if 'TH2' not in h.ClassName():
                                continue
                            drawoptions = ''
                            print '\t', layer, run, h.ClassName(), k
                            if 'rebin' in plots[plot]:
                                h.RebinX(plots[plot]['rebin'])
#                                print "rebinning"
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
                            print ymin, ymax
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
#                            legend.AddEntry(p.GetName(), '%i %s ls:%i-%i bx:%s' % (run, runs[run]['comments'], lumisection[0], lumisection[1], bx), 'lp')
                            legend.AddEntry(p.GetName(), '%i %s bx:%s' % (run, runs[run]['comments'], bx), 'lp')
#                        legend.AddEntry(p.GetName(), '%i LS %i-%i (%.2f - %.2f e33 cm^{-2}/s)' % (run, lumisection[0], lumisection[1], instLumi[run][lumisection[0]], instLumi[run][lumisection[1]]), 'lp')
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
#                mypoly[i].SetFillColor(ROOT.kGray)
                mypoly[i].SetFillColorAlpha(ROOT.kGray, .35)
#                mypoly[i].SetFillStyle(3001)
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
#                            if '_%i-%i_%s' % (lumisection[0], lumisection[1], layer) not in k:
#                                continue
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
#                            legend.AddEntry(h.GetName(), '%i %s ls:%i-%i bx:%s' % (run, runs[run]['comments'], lumisection[0], lumisection[1], bx), 'l')
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


