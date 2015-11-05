#!/bin/bash
set -x
for ijob in `seq 0 28`
do
    echo "ijob= ${ijob}"
#    sed -e "s/IJOB/${ijob}/g" HIPAnalysis_template.py > HIPAnalysis_${ijob}.py
    sed -e "s/IJOB/${ijob}/g" crab_config_template.py > crab_HIPAnalysis_${ijob}.py
#    crab submit crab_config_${ijob}.py
#    sleep 2
done
