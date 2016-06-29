from WMCore.Configuration import Configuration
config = Configuration()

config.section_('General')
config.General.requestName = 'HIPAnalysis'
config.General.workArea = 'tasks'
config.General.transferOutputs = True
config.General.transferLogs = True

config.section_('JobType')
config.JobType.outputFiles = ['output.root']
config.JobType.disableAutomaticOutputCollection = True
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'HIPAnalysis.py'

config.section_('Data')
config.Data.publication = False
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 5
config.Data.totalUnits = 453 # list_calibTrees_2015-12-11_1000LS.txt
#config.Data.totalUnits = 2340 # list_calibTrees_2015-12-11.txt
#config.Data.totalUnits = 287 # list_calibTrees_2015-11-05.txt
config.Data.outLFNDirBase = '/store/user/obondu/'

config.section_('Site')
config.Site.storageSite = 'T2_BE_UCL'

config.section_('User')
config.section_('Debug')
