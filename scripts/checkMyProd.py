#! /usr/bin/env python

import os
import sys
import glob
import json
import argparse

# import CRAB3 stuff
from CRABAPI.RawCommand import crabCommand

# import CMSSW stuff
CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE,'bin', SCRAM_ARCH))

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

# import SAMADhi stuff

def get_options():
    """
    Parse and return the arguments provided by the user.
    """
    parser = argparse.ArgumentParser(description='Babysit-helper for CRAB3 jobs')
    parser.add_argument('--new', action='store_true', help='Start monitoring a new production', dest='new')
    parser.add_argument('-j', '--json', type=str, action='store', dest='outjson', default='prod_default.json',
                        help='json file storing the status of your on-going production') 
    options = parser.parse_args()
    return options

def main():
    #####
    # Initialization
    #####
    options = get_options()
    alltasks = [t for t in os.listdir('tasks') if os.path.isdir(os.path.join('tasks', t))]
    assert len(alltasks) > 0, "No task to monitor in the tasks/ directory"
        
    tasks = {}
    # CRAB3 status
    tasks['COMPLETED'] = []
    tasks['SUBMITFAILED'] = []
    tasks['NEW'] = []
    tasks['SUBMITTED'] = []
    tasks['UNKNOWN'] = []
    tasks['QUEUED'] = []
    tasks['FAILED'] = []
    # GRIDIN status
    tasks['GRIDIN-INDB'] = []
    
    FWHash = "hop"
    AnaRepo = "hop"
    AnaHash = "hop"

    #####
    # Figure out what is the name of the file things should be written into
    #####
    outjson = options.outjson
    if options.new:
#        # NB: assumes all the on-going tasks are for the same analyzer
#        module = runPostCrab.load_file(alltasks[0] + '.py')
#        psetName = module.config.JobType.psetName
#        print "##### Figure out the code(s) version"
#        # first the version of the framework
#        FWHash, FWRepo, FWUrl = runPostCrab.getGitTagRepoUrl( os.path.join(CMSSW_BASE, 'src/cp3_llbb/Framework') )
#        # then the version of the analyzer
#        AnaHash, AnaRepo, AnaUrl = runPostCrab.getGitTagRepoUrl( os.path.dirname( psetName ) )
        outjson = 'prod_' + FWHash + '_' + AnaRepo + '_' + AnaHash + '.json'
        print "The output json will be:", outjson
    else:
        newestjson = max(glob.iglob('prod_*.json'), key=os.path.getctime)
        if outjson == 'prod_default.json' and newestjson != 'prod_default.json':
            outjson = newestjson
            FWHash, AnaRepo, AnaHash = outjson.strip('prod_').strip('.json').split('_')

    #####
    # Read the json if it exists, then check if COMPLETED samples have been entered in SAMADhi since the script was last run
    #####
    data = {}
    if os.path.isfile(outjson):
        with open(outjson) as f:
            data = json.load(f)
    
#        for t in data[u'COMPLETED']:
#            if t in data[u'GRIDIN-INDB']:
#                continue
#            s = str(t).strip('crab_') + '_' + FWHash + '_' + AnaRepo + '_' + AnaHash
#            s_id = get_sample(unicode(s))
#            if len(s_id) > 0:
#                data['GRIDIN-INDB'].append(t)
    
    outputs ={}
    #####
    # Loop over the tasks and perform a crab status
    #####
    for task in alltasks:
#        if len(data) > 0 and unicode(task) in data[u'COMPLETED']:
#            tasks['GRIDIN-INDB'].append(task)
#            continue
        taskdir = os.path.join('tasks/', task)
        print ""
        print "#####", task, "#####"
        status = crabCommand('status', dir = taskdir)
    # {'status': 'COMPLETED', 'schedd': 'crab3-3@submit-4.t2.ucsd.edu', 'saveLogs': 'T', 'jobsPerStatus': {'finished': 1}, 'jobs': {'1': {'State': 'finished'}}, 'publication': {'disabled': []}, 'taskWarningMsg': [], 'publicationFailures': {}, 'outdatasets': None, 'statusFailureMsg': '', 'taskFailureMsg': '', 'failedJobdefs': 0, 'ASOURL': 'https://cmsweb.cern.ch/couchdb', 'totalJobdefs': 0, 'jobSetID': '151022_173830:obondu_crab_HWminusJ_HToWW_M125_13TeV_powheg_pythia8_MiniAODv2', 'jobdefErrors': [], 'collector': 'cmssrv221.fnal.gov,vocms099.cern.ch', 'jobList': [['finished', 1]]}
        tasks[status['status']].append(task)
        if status['status'] == 'COMPLETED':
            outputs[task] = "/storage/data/cms/store/user/obondu/CRAB_PrivateMC/" + task + "/" + status['jobSetID'].split(':')[0] + "/0000/output_1.root"
    
    #####
    # Dump the crab status into the output json file
    #####
    with open(outjson, 'w') as f:
        json.dump(tasks, f)
    
    #####
    # Print summary
    #####
    print "##### ##### Status summary (" + str(len(alltasks)), " tasks) ##### #####"
    for key in tasks:
        if len(tasks[key]) == 0:
            continue
        line = key + ": " + str(len(tasks[key]))
        print line
    
    #####
    # Suggest some actions depending on the crab status
    #    * COMPLETED -> suggest the runPostCrab.py command
    #    * SUBMITFAILED -> suggest to rm -r the task and submit again
    #####
    print "##### ##### Suggested actions ##### #####"
    if len(tasks['COMPLETED']) + len(tasks['SUBMITFAILED']) > 0:
        if len(tasks['COMPLETED']) > 0:
            print "##### COMPLETED tasks #####"
            for task in tasks['COMPLETED']:
                if not os.path.isfile("alloutputs/" + task + ".root"):
                    print "ln -s", outputs[task], "alloutputs/" + task + ".root"
#                print "runPostCrab.py", task + ".py"
        if len(tasks['SUBMITFAILED']) > 0:
            print "##### SUBMITFAILED tasks #####"
            for task in tasks['SUBMITFAILED']:
                print "rm -r tasks/" + task + "; crab submit " + task + ".py"
    else:
        print "None"

if __name__ == '__main__':
    main()
