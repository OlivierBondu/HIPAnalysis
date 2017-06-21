# HIPAnalysis

## First time setup

```bash
cmsrel CMSSW_9_2_3_patch2
cd CMSSW_9_2_3_patch2/src
cmsenv
git cms-init
cd ${CMSSW_BASE}/src 
git clone -o upstream git@github.com:blinkseb/TreeWrapper.git CalibTracker/TreeWrapper
git clone -o upstream git@github.com:OlivierBondu/HIPAnalysis.git CalibTracker/HIPAnalysis
cd ${CMSSW_BASE}/src/
scram b -j 4
```
