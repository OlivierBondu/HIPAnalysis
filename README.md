# HIPAnalysis

## First time setup

```c++
export SCRAM_ARCH=slc6_amd64_gcc491
cmsrel CMSSW_7_4_15
cd CMSSW_7_4_15/src
cmsenv
git cms-init
cd ${CMSSW_BASE}/src 
git clone -o upstream git@github.com:blinkseb/TreeWrapper.git CalibTracker/TreeWrapper
git clone -o upstream git@github.com:OlivierBondu/HIPAnalysis.git CalibTracker/HIPAnalysis
cd ${CMSSW_BASE}/src/
scram b -j 4
```
