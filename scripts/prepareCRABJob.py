#!/bin/env python
import argparse
import os
import subprocess
from CRABAPI.RawCommand import crabCommand
import json

def get_options():
    parser = argparse.ArgumentParser(description='Return the list of calib trees for a given run')
    parser.add_argument('--run', action='store', dest='run', default=[296172], nargs='+', type=int,
                        help='Run number')
    parser.add_argument('--split', action='store', dest='split', default=[0], nargs='+', type=int,
                        help='Splitting bunch trains in SPLIT bunch crossings')
    parser.add_argument('--submit', action='store_true', dest='submit',
                        help='Submit the task through CRAB once created')
    options = parser.parse_args()
    return options


def calibTree_list_exist(run):
    CMSSW_BASE = os.environ['CMSSW_BASE']
    calibTree_list_path = os.path.join(CMSSW_BASE, 'src/', 'CalibTracker/HIPAnalysis', 'test/data')
    list_file = [os.path.join(calibTree_list_path, x) for x in os.listdir(calibTree_list_path) if str(run) in x]
    if len(list_file) == 0:
        return 0
    list_file = list_file[0]
    data = None
    with open(list_file, 'r') as f:
        data = json.load(f)
    return list_file, len(data['files'])


def prepare_CMSSW_config(run, split, list_file, n_files):
    CMSSW_BASE = os.environ['CMSSW_BASE']
    original_config = os.path.join(CMSSW_BASE, 'src/', 'CalibTracker/HIPAnalysis', 'test/anEffAnalysis.py')
    new_config = original_config.replace('anEffAnalysis', 'anEffAnalysis_run_%i_split_%i' % (run, split))
    with open(new_config, 'w') as outf:
        with open(original_config, 'r') as inf:
            for line in inf:
                if line.startswith('RUN_NUMBER'):
                    outf.write('RUN_NUMBER = %i\n' % run)
                elif line.startswith('N_FILES'):
                    outf.write('N_FILES = %i\n' % n_files)
                elif line.startswith('SPLITTRAIN'):
                    outf.write('SPLITTRAIN = %i\n' % split)
                elif line.startswith('INFOJSON'):
                    outf.write('INFOJSON = \"%s\"\n' % list_file)
                else:
                    outf.write(line)
    return new_config


def prepare_CRAB_config(run, split, n_files):
    CMSSW_BASE = os.environ['CMSSW_BASE']
    original_config = os.path.join(CMSSW_BASE, 'src/', 'CalibTracker/HIPAnalysis', 'test/crab_anEffAnalysis.py')
    new_config = original_config.replace('anEffAnalysis', 'anEffAnalysis_run_%i_split_%i' % (run, split))
    with open(new_config, 'w') as outf:
        with open(original_config, 'r') as inf:
            for line in inf:
                if line.startswith('config.General.requestName') or line.startswith('config.JobType.psetName'):
                    outf.write(line.replace('anEffAnalysis', 'anEffAnalysis_run_%i_split_%i' % (run, split)))
                elif line.startswith('config.Data.unitsPerJob'):
                    outf.write('config.Data.unitsPerJob = %i\n' % n_files)
                elif line.startswith('config.Data.totalUnits'):
                    outf.write('config.Data.totalUnits = %i\n' % n_files)
                else:
                    outf.write(line)
    return new_config 


def launch_CRAB(crab_config):
    base_crab_config = os.path.basename(crab_config)
    if os.path.isfile(base_crab_config):
        res = crabCommand('submit', config = base_crab_config)
        print res
    else:
        print 'You do not seem to be in the correct directory for submitting jobs'
    return


def prepareCRABJob(run, split, submit):
    list_file, n_files = calibTree_list_exist(run)
    cmssw_config = prepare_CMSSW_config(run, split, list_file, n_files)
    crab_config = prepare_CRAB_config(run, split, n_files)
    print 'CMSSW config: %s' % cmssw_config
    print 'CRAB config: %s' % crab_config
    if submit:
        launch_CRAB(crab_config)
    return


if __name__ == '__main__':
    options = get_options()
    submit = options.submit
    for run in options.run:
        for split in options.split:
            prepareCRABJob(run, split, submit)
            print ''


