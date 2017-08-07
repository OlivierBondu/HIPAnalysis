from WMCore.Configuration import Configuration
config = Configuration()

config.section_('General')
config.General.requestName = 'anEffAnalysis'
config.General.workArea = 'tasks'
config.General.transferOutputs = True
config.General.transferLogs = True

config.section_('JobType')
config.JobType.outputFiles = ['histos.root']
config.JobType.disableAutomaticOutputCollection = True
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'anEffAnalysis.py'

config.section_('Data')
config.Data.publication = False
config.Data.splitting = 'EventBased'
# NB: unitsPerJob and totalUnits should be equal AND larger than the number of files for the longest run
# Protection to not run forever is now built in the CMSSW config file anEffAnalysis.py
config.Data.unitsPerJob = 50
config.Data.totalUnits = 50
config.Data.outLFNDirBase = '/store/user/obondu/'

config.section_('Site')
config.Site.storageSite = 'T2_BE_UCL'

config.section_('User')
config.section_('Debug')
