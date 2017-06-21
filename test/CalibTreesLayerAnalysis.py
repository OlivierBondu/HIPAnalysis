import FWCore.ParameterSet.Config as cms

process = cms.Process("CalibTreesLayerAnalysis")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.GlobalTag.globaltag = "92X_dataRun2_Prompt_v4"

process.source = cms.Source("EmptySource",)

myFileList = []
filelist = "/home/fynu/obondu/TRK/CMSSW_9_2_3_patch2/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_Fill-5750_Run-296173.txt"
#filelist = "/home/fynu/obondu/TRK/CMSSW_8_0_14/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_APVsettings.txt"

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
# for runs 278769 and 278770
#bx_list = [60, 116, 199, 255, 338, 394] #, 477, 533, 616, 672, 803, 589, 942]
#bxs += ["%i-%i" % (x   , x+16) for x in bx_list]
#bxs += ["%i-%i" % (x+16, x+32) for x in bx_list]
#bxs += ["%i-%i" % (x+32, x+48) for x in bx_list]
#bxs += ["%i-%i" % (x   , x+24) for x in bx_list]
#bxs += ["%i-%i" % (x+24, x+48) for x in bx_list]
# for runs 274968
bx_list = [112, 221, 330, 439]
bxs += ["%i-%i" % (x   , x+24) for x in bx_list]
bxs += ["%i-%i" % (x+24, x+48) for x in bx_list]
bxs += ["%i-%i" % (x+48, x+72) for x in bx_list]


process.CalibTreesLayerAnalysis = cms.EDAnalyzer('CalibTreesLayerAnalysis',
    debug = cms.bool(False),
    maxEventsPerFile = cms.untracked.int64(-1),
    InputFiles = cms.untracked.vstring(myFileList),
#    inputTreeName = cms.string("gainCalibrationTreeAagBunch/tree"),
#    output = cms.string('histos_APVsettings_AagBunch.root'),
    inputTreeName = cms.string("gainCalibrationTreeStdBunch/tree"),
    output = cms.string('histos_296173_v3.root'),
    runs = cms.untracked.vint32(296173), # note: override whatever is in the LuminosityBlockRange
#    runs = cms.untracked.vint32(278769, 278770), # note: override whatever is in the LuminosityBlockRange
    lumisections = cms.untracked.VLuminosityBlockRange(
        # First 100 LS
#        cms.LuminosityBlockRange("1:0-1:100"),
        # every 300 LS
        cms.LuminosityBlockRange("1:100-1:400"),
        cms.LuminosityBlockRange("1:400-1:700"),
        cms.LuminosityBlockRange("1:700-1:1000"),
#        cms.LuminosityBlockRange("1:1000-1:1300"),
#        cms.LuminosityBlockRange("1:1300-1:1700"),
#        cms.LuminosityBlockRange("1:1700-1:2000"),
        # every 100 LS
#        cms.LuminosityBlockRange("1:100-1:200"),
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
    bxs = cms.untracked.vstring(bxs)
)

process.TkDetMap = cms.Service("TkDetMap")
process.SiStripDetInfoFileReader = cms.Service("SiStripDetInfoFileReader")

process.p = cms.Path(process.CalibTreesLayerAnalysis)
