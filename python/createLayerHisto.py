#!/bin/env python
# Python imports
import os
import sys
import numpy as np
import argparse
# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:] 
sys.argv = []
# ROOT setup
import ROOT
from ROOT import TChain, TCanvas, TLatex
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.TGaxis.SetMaxDigits(3)
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv


def get_options():
    parser = argparse.ArgumentParser(description='Create histos per layer and per run')
    parser.add_argument('--layer', action='store', dest='layer',
                        default='TOB_L1',
                        help='Layer on which to run (TIDP_D1, TIDM_D1, TECP_W1, TECM_W1, TOB_L1, TIB_L1)')
    parser.add_argument('--run', action='store', dest='run',
                        default=257400,
                        help='run on which to run')
    parser.add_argument('--outdir', action='store', dest='outdir',
                        default='TEST_perLayerPlots',
                        help='output directory')
    parser.add_argument('--outfile', dest='outfile',
                        default='histos.root',
                        help='output file')
    parser.add_argument('--inputdir', action='store', dest='inputdir',
                        default='/storage/data/cms/store/user/obondu/CRAB_PrivateMC/crab_HIPAnalysis/160616_162801/0000/',
                        help='input directory')
    parser.add_argument('--inputfile', dest='inputfiles', nargs='*',
                        default=['output_1.root'],
                        help='input file')
    options = parser.parse_args()
    return options

def main(layer, run, outdir, outfile, inputdir, inputfiles):
    
    chain = TChain("layertree")
    inputfiles = [os.path.join(inputdir, x) for x in inputfiles]
    for f in inputfiles:
        print f
        chain.Add(f)
    print "chain.GetEntries()=", chain.GetEntries()

    c1 = TCanvas()
    if len(outdir) > 0 and not os.path.exists(outdir):
        os.makedirs(outdir)
        outdir += '/'
    f = ROOT.TFile(outdir + outfile, "recreate")    
    
    layers = []
    layers += ["TIDP_D%i" % i for i in xrange(1,4)]
    layers += ["TIDM_D%i" % i for i in xrange(1,4)]
    layers += ["TECP_W%i" % i for i in xrange(1,10)]
    layers += ["TECM_W%i" % i for i in xrange(1,10)]
    layers += ["TOB_L%i" % i for i in xrange(1,7)]
    layers += ["TIB_L%i" % i for i in xrange(1,5)]
#    layers = [layer] # artifacts to keep the same code for creating the histos themselves

    runs = [
            257400, 257487, 257613, 257645, 257822, 258158, 258177, 260627, # 2015 runs
            274968, # 2016 runs
            ]
#    runs = [run]
    plots = {
    "meanChargeoverpath__": {
        "name": "meanChargeoverpath",
        "title": "#Events:< charge / path >",
        "binning": "(800, 0, 800)",
        "norm": "1",
        "ylog": False,
        },
    "meanChargeoverpath__:bx__": {
        "name": "meanChargeoverpath_vs_bx", 
        "title": "< charge / path >:bx",
        "binning": "(3500, 0, 3500, 2000, 0, 2000)"
        },
    }
    
   
    allcuts = {
        "LS_0-1000":    "0      <= lumi__ && lumi__ <= 1000",
        "LS_1000-2000": "1000   <= lumi__ && lumi__ <= 2000",
        "LS_0-2000":    "0      <= lumi__ && lumi__ <= 2000",

        "LS_0-100":     "0      <= lumi__ && lumi__ <= 100 ",
        "LS_100-200":   "100    <= lumi__ && lumi__ <= 200 ",
        "LS_200-300":   "200    <= lumi__ && lumi__ <= 300 ",
        "LS_300-400":   "300    <= lumi__ && lumi__ <= 400 ",
        "LS_400-500":   "400    <= lumi__ && lumi__ <= 500 ",
        "LS_500-600":   "500    <= lumi__ && lumi__ <= 600 ",
        "LS_600-700":   "600    <= lumi__ && lumi__ <= 700 ",
        "LS_700-800":   "700    <= lumi__ && lumi__ <= 800 ",
        "LS_800-900":   "800    <= lumi__ && lumi__ <= 900 ",
        "LS_900-1000":  "900    <= lumi__ && lumi__ <= 1000",
        "LS_1000-1100": "1000   <= lumi__ && lumi__ <= 1100",
        "LS_1100-1200": "1100   <= lumi__ && lumi__ <= 1200",
        "LS_1200-1300": "1200   <= lumi__ && lumi__ <= 1300",
        "LS_1300-1400": "1300   <= lumi__ && lumi__ <= 1400",
        "LS_1400-1500": "1400   <= lumi__ && lumi__ <= 1500",
        "LS_1500-1600": "1500   <= lumi__ && lumi__ <= 1600",
        "LS_1600-1700": "1600   <= lumi__ && lumi__ <= 1700",
        "LS_1700-1800": "1700   <= lumi__ && lumi__ <= 1800",
        "LS_1800-1900": "1800   <= lumi__ && lumi__ <= 1900",
        "LS_1900-2000": "1900   <= lumi__ && lumi__ <= 2000",
    }
    cuts = {}
    for cut in allcuts:
        for l in layers:
            x = cut + '_' + l
            cuts[x] = '(%s) && (layer__ == \"%s\")' % (allcuts[cut], l)
    h = {}
    
    runs = [x for x in runs if chain.GetEntries('run__ == %i' % x) > 0]
    print runs

    for icut, cut in enumerate(cuts):
        print "cut= ", cut, '(%i / %i)' % (icut + 1, len(cuts))
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
                hname = "h_%s_%s_%s" % (plots[plot]['name'], run, cut)
                print "\t\thname= ", hname
                chain.Draw(plot + ">>%s%s" % (hname, binning), totalcut, options)
                h[hname] = ROOT.gDirectory.Get(hname)
                h[hname].SetTitle("")
                extrafilename = ''
                if ':' in plot: # this is a 2D plot
                    h[hname].SetContour(1000) # for prettier contours
                norm = plots[plot].get('norm', None)
                if norm == '1':
                    h[hname].GetYaxis().SetTitle('Norm. to unity')
                else:
                    h[hname].GetYaxis().SetTitle(plots[plot]['title'].split(':')[0])
                h[hname].GetXaxis().SetTitle(plots[plot]['title'].split(':')[1])
                h[hname].SetDirectory(0)
                h[hname].Draw(options)
                h[hname].Write()
            c1.Clear()
    f.Write()
    f.Close()
    
if __name__ == '__main__':
    options = get_options()
    main(
        layer = options.layer, 
        run = options.run,
        outdir = options.outdir,
        outfile = options.outfile,
        inputdir = options.inputdir,
        inputfiles = options.inputfiles
        )
