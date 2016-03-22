#! /usr/bin/env python
""" Simple script to compute the luminosity of a set of samples """

import sys
import json
import pprint
import subprocess
import argparse

def get_options():
    parser = argparse.ArgumentParser(description='Compute luminosity of a set of samples.')

    parser.add_argument('--local', dest='local', action='store_true', help='Run brilcalc locally instead of on lxplus')

    parser.add_argument('--bootstrap', dest='bootstrap', action='store_true', help='Install brilcalc. Needs to be done only once')

    parser.add_argument('-n', '--username', dest='username', help='Remote lxplus username (local username by default)')
    parser.add_argument('--inputfile', type=str, nargs='+', dest='inputfiles', help='Input json file')

    options = parser.parse_args()

    if not options.bootstrap and options.inputfiles is None:
        parser.error('You must specify at least one sample id or sample name.')

    if options.username is None:
        import pwd, os
        options.username = pwd.getpwuid(os.getuid()).pw_name

    return options

def parse_luminosity_csv(result):
    """ Parse the CSV file produced by brilcalc, and return the total recorded luminosity in /pb """
    import csv
    import StringIO

    f = StringIO.StringIO(result)

    lumi = 0
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        if row[0][0] == '#':
            continue
        lumi += float(row[-1])

    return lumi / 1000. / 1000.

def compute_luminosity(d, options):
    lumi = 0
    if not options.local:
        print("Running brilcalc on lxplus... You'll probably need to enter your lxplus password in a moment")
        print('')

#        cmds = ['brilcalc', 'lumi', '--normtag', '~lumipro/public/normtag_file/OfflineNormtagV2.json', '--output-style', 'csv', '-i', '"%s"' % str(sample.processed_lumi.replace('"', ''))]
        cmds = ['brilcalc', 'lumi', '--output-style', 'csv', '-i', '"%s"' % str(d), '--byls']
        cmd = 'export PATH="$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.0.3/bin:$PATH"; ' + ' '.join(cmds)
        ssh_cmds = ['ssh', '%s@lxplus.cern.ch' % options.username, cmd]
        brilcalc_result = subprocess.check_output(ssh_cmds)
#        print brilcalc_result
        return brilcalc_result

#        lumi = parse_luminosity_csv(brilcalc_result)
    else:
        print("Running brilcalc locally...")
        # FIXME one day
        print("Error: running brilcalc locally is not supported for the moment.")
        return 0

def main():

    options = get_options()

    for inputfile in options.inputfiles:
        with open(inputfile) as f:
            d = json.load(f)
            d_ = {}
            for k in d:
                d_[int(k)] = d[k]
#            pprint.pprint(d)
#            pprint.pprint(d_)
            alllumi = compute_luminosity(d, options)
            with open('allcalibtrees.csv', 'w') as o:
                o.write(alllumi)

#
# main
#
if __name__ == '__main__':
    main()
