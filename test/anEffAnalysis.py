import FWCore.ParameterSet.Config as cms
import json

RUN_NUMBER = 299061
N_FILES = 1
SPLITTRAIN = 0
INFOJSON = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_Fill-5950_Run-299061.json"

data = None
with open(INFOJSON, 'r') as f:
    data = json.load(f)

process = cms.Process("anEffAnalysis")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.GlobalTag.globaltag = "92X_dataRun2_Prompt_v4"

process.source = cms.Source("EmptySource",)

myFileList = []
filelist = data['files']

for f in filelist:
    if 'store' not in f:
        continue
    myFileList.append(('root://eoscms.cern.ch//eos/cms' + f).encode('ascii'));

myFileSubList = []
for i in xrange(0, len(myFileList) / 10 + 1):
    myFileSubList.append(myFileList[i*10 : i*10 + 10])

# In this analyser, maxEvents actually represents the number of input files...
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(N_FILES) ) 
# Sanity check, just in case
if (process.maxEvents.input < 0) or (process.maxEvents.input > len(myFileList)):
    process.maxEvents.input = cms.untracked.int32(len(myFileList))

bxs = []
for train in data['scheme']:
    if SPLITTRAIN > 0 and len(train) > SPLITTRAIN:
        for i in xrange(len(train) / SPLITTRAIN):
            bxs.append('%i-%i' % (train[i * SPLITTRAIN], train[(i + 1) * SPLITTRAIN - 1]))
        if len(train) % SPLITTRAIN != 0:
            bxs.append('%i-%i' % (train[len(train) / SPLITTRAIN * SPLITTRAIN], train[-1]))
    else:
        bxs.append('%i-%i' % (train[0], train[-1]))

bxs_th1 = bxs
bxs_th2 = ['0-3600']
print 'Will fill %i TH1 and %i TH2' % (len(bxs_th1), len(bxs_th2))

process.anEffAnalysis = cms.EDAnalyzer('anEffAnalysis',
    debug = cms.bool(False),
    maxEventsPerFile = cms.untracked.int64(-1),
    InputFiles = cms.untracked.vstring(myFileList),
    inputTreeName = cms.string("anEff/traj"),
    output = cms.string('histos.root'),
    runs = cms.untracked.vint32(RUN_NUMBER), # note: override whatever is in the LuminosityBlockRange
    # FIXME: LUMISECTION IS NOT IN THE TREE
    lumisections = cms.untracked.VLuminosityBlockRange(
        cms.LuminosityBlockRange("1:0-1:100"),
        ),
    layers = cms.untracked.vstring(["TOB_L1"]),
    bxs_th1 = cms.untracked.vstring(bxs_th1),
    bxs_th2 = cms.untracked.vstring(bxs_th2),
# expression to filter out the input tree to speed things up
    filter_exp = cms.string(''),
    perform_fit = cms.bool(True),
    verbose_fit = cms.bool(False),
)
filter_exp = ''
# filter on runs
for ir, r in enumerate(process.anEffAnalysis.runs):
    if ir == 0:
        filter_exp += '('
    elif ir <= len(process.anEffAnalysis.runs) - 1:
        filter_exp += ' || '
    filter_exp += 'run == %i' % r
    if ir == len(process.anEffAnalysis.runs) - 1:
        filter_exp += ')'
# filter on lumisections: FIXME is not available in the anEff tree
# for il, l in enumerate(process.anEffAnalysis.lumisections):
#    print il, l
#     print l.start(), l.startSub(), l.end(), l.endSub()
# filter on bxs from th2
for ib, b in enumerate(process.anEffAnalysis.bxs_th2):
    if ib == 0:
        if len(filter_exp) > 0:
            filter_exp += ' && '
        filter_exp += '('
    elif ib <= len(process.anEffAnalysis.bxs_th2) - 1:
        filter_exp += ' || '
    tmp = b.split('-')
    tmp = map(int, tmp)
    filter_exp += '(%i <= bunchx && bunchx <= %i)' % (tmp[0], tmp[1])
    if ib == len(process.anEffAnalysis.bxs_th2) - 1:
        filter_exp += ')'
# filter on layers: FIXME is not available in the anEff tree
# put the final string into the argument to be passed to the analyzer
if len(filter_exp) == 0:
    process.anEffAnalysis.filter_exp = cms.string('(ModIsBad == 0) && (SiStripQualBad == 0) && (withinAcceptance == 1) && (trajHitValid == 1) && (layer == 5)')
#    process.anEffAnalysis.filter_exp = cms.string('1')
else:
    filter_exp += ' && (ModIsBad == 0) && (SiStripQualBad == 0) && (withinAcceptance == 1) && (trajHitValid == 1) && (layer == 5)'
    process.anEffAnalysis.filter_exp = cms.string(filter_exp)

process.TkDetMap = cms.Service("TkDetMap")
process.SiStripDetInfoFileReader = cms.Service("SiStripDetInfoFileReader")

process.p = cms.Path(process.anEffAnalysis)
