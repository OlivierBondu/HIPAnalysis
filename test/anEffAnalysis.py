import FWCore.ParameterSet.Config as cms

process = cms.Process("anEffAnalysis")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.GlobalTag.globaltag = "92X_dataRun2_Prompt_v4"

process.source = cms.Source("EmptySource",)

myFileList = []
#filelist = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_Fill-5750_Run-296173.txt"
#filelist = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_Fill-5883_Run-297673.txt"
#filelist = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_Fill-5883_Run-297674.txt"
filelist = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_Fill-5950_Run-299061.txt"
#filelist = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test/data/"

with open(filelist) as f:
    for line in f:
        if '#' in line:
            continue
        myFileList.append('root://eoscms.cern.ch//eos/cms' + line.strip('\n'));
#        myFileList.append(line.strip('\n'));
#print myFileList

# TEST FILE
# myFileList = ['root://cmsxrootd.fnal.gov//store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR15/calibTree_247243.root',]

#print "len(myFileList)=", len(myFileList)
myFileSubList = []
for i in xrange(0, len(myFileList) / 10 + 1):
    myFileSubList.append(myFileList[i*10 : i*10 + 10])
#print "len(myFileSubList)=", len(myFileSubList)

# In this analyser, maxEvents actually represents the number of input files...
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) ) 

bxs = ['0-3600']
# FIXME: design a way to extract the bunch filling scheme from runregistry / cmsweb

process.anEffAnalysis = cms.EDAnalyzer('anEffAnalysis',
    debug = cms.bool(False),
    maxEventsPerFile = cms.untracked.int64(-1),
    InputFiles = cms.untracked.vstring(myFileList),
#    inputTreeName = cms.string("gainCalibrationTreeAagBunch/tree"),
#    output = cms.string('histos_APVsettings_AagBunch.root'),
    inputTreeName = cms.string("anEff/traj"),
    output = cms.string('histos.root'),
    runs = cms.untracked.vint32(299061), # note: override whatever is in the LuminosityBlockRange
    # FIXME: LUMISECTION IS NOT IN THE TREE
    lumisections = cms.untracked.VLuminosityBlockRange(
        # First 100 LS
        cms.LuminosityBlockRange("1:0-1:100"),
        # every 300 LS
#        cms.LuminosityBlockRange("1:100-1:400"),
#        cms.LuminosityBlockRange("1:400-1:700"),
#        cms.LuminosityBlockRange("1:700-1:1000"),
        # every 100 LS
        cms.LuminosityBlockRange("1:100-1:200"),
#        cms.LuminosityBlockRange("1:200-1:300"),
#        cms.LuminosityBlockRange("1:300-1:400"),
#        cms.LuminosityBlockRange("1:400-1:500"),
#        cms.LuminosityBlockRange("1:500-1:600"),
#        cms.LuminosityBlockRange("1:600-1:700"),
#        cms.LuminosityBlockRange("1:700-1:800"),
#        cms.LuminosityBlockRange("1:800-1:900"),
#        cms.LuminosityBlockRange("1:900-1:1000"),
#        cms.LuminosityBlockRange("1:1000-1:1100"),
#        cms.LuminosityBlockRange("1:1100-1:1200"),
#        cms.LuminosityBlockRange("1:1200-1:1300"),
#        cms.LuminosityBlockRange("1:1300-1:1400"),
#        cms.LuminosityBlockRange("1:1400-1:1500"),
#        cms.LuminosityBlockRange("1:1500-1:1600"),
#        cms.LuminosityBlockRange("1:1600-1:1700"),
#        cms.LuminosityBlockRange("1:1700-1:1800"),
#        cms.LuminosityBlockRange("1:1800-1:1900"),
        ),
    layers = cms.untracked.vstring(["TOB_L1"]),
    bxs = cms.untracked.vstring(bxs),
# expression to filter out the input tree to speed things up
    filter_exp = cms.string(''),
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
# filter on bxs
for ib, b in enumerate(process.anEffAnalysis.bxs):
    if ib == 0:
        if len(filter_exp) > 0:
            filter_exp += ' && '
        filter_exp += '('
    elif ib <= len(process.anEffAnalysis.bxs) - 1:
        filter_exp += ' || '
    tmp = b.split('-')
    tmp = map(int, tmp)
    filter_exp += '(%i < bunchx && bunchx < %i)' % (tmp[0], tmp[1])
    if ib == len(process.anEffAnalysis.bxs) - 1:
        filter_exp += ')'
# filter on layers: FIXME is not available in the anEff tree
# put the final string into the argument to be passed to the analyzer
if len(filter_exp) == 0:
    process.anEffAnalysis.filter_exp = cms.string('trajHitValid == 1')
else:
    filter_exp += ' && (trajHitValid == 1)'
    process.anEffAnalysis.filter_exp = cms.string(filter_exp)

process.TkDetMap = cms.Service("TkDetMap")
process.SiStripDetInfoFileReader = cms.Service("SiStripDetInfoFileReader")

process.p = cms.Path(process.anEffAnalysis)
