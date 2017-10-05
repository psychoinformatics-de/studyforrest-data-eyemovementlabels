#!/bin/bash

set -e
set -u


###input argument description
# 1. filename of the condor script to be edited
# 2. subject id
# 3. task id

condor_script="code/preprocess_eyegaze_recordings.submit"
condor_output_folder="condor_output/"

###initialize environment in condor submit file
initialization_string="universe = vanilla
executable=/usr/bin/python2.7
initialdir = /home/asimio/fg_eyegaze_preproc/
request_cpus = 1
request_memory = 8000
getenv = True"



#arguments="code/preprocess_eyegaze_recordings.py 0.0266711972026 inputs/raw_eyegaze/sub-35/beh/sub-35_task-movie_run-1_recording-eyegaze_physio.tsv.gz tocheck.gz"

echo "$initialization_string" > $condor_script

for sub in sub-01 sub-02 sub-03 sub-04 sub-05 sub-06 sub-09 sub-10 sub-14 sub-15 sub-16 sub-17 sub-18 sub-19 sub-20; do
  subid=$(echo "$sub" | cut -d '-' -f2-)
  mkdir -p sub-$subid
  for run in run-1 run-2 run-3 run-4 run-5 run-6 run-7 run-8; do
    runid=$(echo "$run" | cut -d '-' -f2-)
    echo "arguments= code/preprocess_eyegaze_recordings.py 0.0185581232561 inputs/raw_eyegaze/sub-${subid}/ses-movie/func/sub-${subid}_ses-movie_task-movie_run-${runid}_recording-eyegaze_physio.tsv.gz sub-${subid}/eyegaze_run-${runid}_preprocessed.tsv.gz" >> $condor_script
    echo "Queue" >> $condor_script
  done
done

for sub in sub-22 sub-23 sub-24 sub-25 sub-26 sub-27 sub-28 sub-29 sub-30 sub-31 sub-32 sub-33 sub-34 sub-35 sub-36; do
  subid=$(echo "$sub" | cut -d '-' -f2-)
  mkdir -p sub-$subid
  for run in run-1 run-2 run-3 run-4 run-5 run-6 run-7 run-8; do
    runid=$(echo "$run" | cut -d '-' -f2-)
    echo "arguments= code/preprocess_eyegaze_recordings.py 0.0266711972026 inputs/raw_eyegaze/sub-${subid}/beh/sub-${subid}_task-movie_run-${runid}_recording-eyegaze_physio.tsv.gz sub-${subid}/eyegaze_run-${runid}_preprocessed.tsv.gz" >> $condor_script
    echo "Queue" >> $condor_script
  done
done
