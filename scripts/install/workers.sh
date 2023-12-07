#!/bin/bash
set -eo pipefail

echo "Installing workers and their dependencies..."
echo "**********************************"
echo

target=$1

for WORKER in $(ls -d augur/tasks/data_analysis/*/)
do
    if [[ \
      $WORKER != *"spdx_worker"* \
   && $WORKER != *"template_worker"* \
   && $WORKER != *"metric_status_worker"* \
   && $WORKER != *"__pycache__"* \
   && $WORKER != *"contributor_breadth_worker"* \
   ]]; then

      # make it pretty for formatting
      FORMATTED_WORKER=$(basename $WORKER)

      echo
      echo "**********************************"
      echo "Installing $FORMATTED_WORKER..."
      echo "**********************************"
      echo

      cd $WORKER
      rm -rf build/*;
      rm -rf dist/*;
      if [[ $target == *"prod"* ]]; then
          pip install .
      else
          pip install -e .[dev]
      fi
      cd ../../../../
    fi

done
