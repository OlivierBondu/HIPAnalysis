import FWCore.ParameterSet.Config as cms

process = cms.Process("HIPAnalysis")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.GlobalTag.globaltag = "74X_dataRun2_Prompt_v1"

process.source = cms.Source("EmptySource",)

myFileList = []
#filelist = "data/list_calibTrees_2015-12-11.txt"
#filelist = "data/list_calibTrees_SDV_HIP_2016-05-16_00.txt"
#filelist = "data/list_calibTrees_SDV_HIP_2016-05-16_01.txt"
#filelist = "/home/fynu/obondu/TRK/CMSSW_7_4_15/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_SDV_HIP_2016-05-16_02.txt"
#filelist = "/home/fynu/obondu/TRK/CMSSW_7_4_15/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_2015-12-11_test_1000LS.txt"
filelist = "/home/fynu/obondu/TRK/CMSSW_7_4_15/src/CalibTracker/HIPAnalysis/test/data/list_calibTrees_2015-12-11_1000LS.txt"
with open(filelist) as f:
    for line in f:
        if '#' in line:
            continue
        myFileList.append('root://eoscms.cern.ch//eos/cms' + line.strip('\n'));
        myFileList.append(line.strip('\n'));
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

process.HIPAnalysis = cms.EDAnalyzer('HIPAnalysis',
    debug = cms.bool(False),
    fillPerEvent = cms.bool(False),
    fillPerLayer = cms.bool(True),
    fillPerCluster = cms.bool(False),
    maxEventsPerFile = cms.untracked.int64(-1),
#    InputFiles = cms.untracked.vstring(myFileSubList[0]),
    InputFiles = cms.untracked.vstring(myFileList),
    output = cms.string('output_debug.root')
#    output = cms.string('output_SDV_HIP_2016-05-16_00.root')
#    output = cms.string('output_SDV_HIP_2016-05-16_01.root')
)

process.TkDetMap = cms.Service("TkDetMap")
process.SiStripDetInfoFileReader = cms.Service("SiStripDetInfoFileReader")

process.p = cms.Path(process.HIPAnalysis)
