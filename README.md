# HIPAnalysis

#### Where am I?

This is a CMSSW 'analyzer' running onto tracker DPG `calibTree`, centrally produced, for analyses purposes. This package was designed for the investigation the SiStrip dynamic inefficiency in 2015-2016. Initially, the phenomenon was (incorrectly) believed to be due mainly to Heavy Ionizing Particles, aka HIP. Hence the name.

#### Why CMSSW and not a plain ROOT macro?

Because there are a lot of `calibTree` out there. So, to have a better scaling for analyzing a lot of them, and because I'm lazy and the trees are available on `eos`, I decided to have CRAB do the job handling, copying the output back to storage, etc. On the plus side, this also makes this code batch-system independent. So feel free to run this on lxplus or your local cluster, it does not matter.

#### CRAB, really? but `calibTree` are not EDM files?

Yes, the trick here is to have CRAB believes it is doing MC production, which gives some more freedom about this
. The analyzer will read one `calibTree` file per produced 'MC event'. This system do have some overhead, but I believe it's scaling much better.

#### Ok, let's go!



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
