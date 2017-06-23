from WMCore.Configuration import Configuration
config = Configuration()

config.section_('General')
config.General.requestName = 'CalibTreesLayerAnalysis'
config.General.workArea = 'tasks'
config.General.transferOutputs = True
config.General.transferLogs = True

config.section_('JobType')
config.JobType.outputFiles = ['histos.root']
config.JobType.disableAutomaticOutputCollection = True
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'CalibTreesLayerAnalysis.py'

config.section_('Data')
config.Data.publication = False
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 5
config.Data.totalUnits = 31 # list_calibTrees_Fill-5750_Run-296173.txt
config.Data.outLFNDirBase = '/store/user/obondu/'

config.section_('Site')
config.Site.storageSite = 'T2_BE_UCL'

config.section_('User')
config.section_('Debug')
