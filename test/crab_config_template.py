from WMCore.Configuration import Configuration
config = Configuration()

config.section_('General')
config.General.requestName = 'HIPAnalysis_IJOB'
config.General.workArea = 'tasks'
config.General.transferOutputs = True
config.General.transferLogs = True

config.section_('JobType')
config.JobType.outputFiles = ['output.root']
config.JobType.disableAutomaticOutputCollection = True
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'HIPAnalysis_IJOB.py'

config.section_('Data')
config.Data.publication = False
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 1
config.Data.totalUnits = 1
config.Data.outLFNDirBase = '/store/user/obondu/'

config.section_('Site')
config.Site.storageSite = 'T2_BE_UCL'

config.section_('User')
config.section_('Debug')
