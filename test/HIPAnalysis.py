import FWCore.ParameterSet.Config as cms

process = cms.Process("HIPAnalysis")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.GlobalTag.globaltag = "74X_dataRun2_Prompt_v1"

process.source = cms.Source("EmptySource",)

myFileList = []
filelist = "data/list_calibTrees_2015-12-11.txt"
with open(filelist) as f:
    for line in f:
        myFileList.append('root://eoscms.cern.ch//eos/cms' + line.strip('\n'));
print myFileList

# TEST FILE
# myFileList = ['root://cmsxrootd.fnal.gov//store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR15/calibTree_247243.root',]

print "len(myFileList)=", len(myFileList)
myFileSubList = []
for i in xrange(0, len(myFileList) / 10 + 1):
    myFileSubList.append(myFileList[i*10 : i*10 + 10])
print "len(myFileSubList)=", len(myFileSubList)

# In this analyser, maxEvents actually represents the number of input files...
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

process.HIPAnalysis = cms.EDAnalyzer('HIPAnalysis',
    maxEventsPerFile = cms.untracked.int64(-1),
#    InputFiles = cms.untracked.vstring(myFileSubList[0]),
    InputFiles = cms.untracked.vstring(myFileList),
    output = cms.string('output.root')
)

process.p = cms.Path(process.HIPAnalysis)
