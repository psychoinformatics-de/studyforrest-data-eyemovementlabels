#!/bin/bash

set -e
set -u


for sub in sub-01 sub-02 sub-03 sub-04 sub-05 sub-06 sub-09 sub-10 sub-14 sub-15 sub-16 sub-17 sub-18 sub-19 sub-20; do
  subid=$(echo "$sub" | cut -d '-' -f2-)
  mkdir -p sub-$subid
  for run in run-1 run-2 run-3 run-4 run-5 run-6 run-7 run-8; do
    runid=$(echo "$run" | cut -d '-' -f2-)
    echo "code/detect_events.py inputs/raw_eyegaze/sub-${subid}/ses-movie/func/sub-${subid}_ses-movie_task-movie_run-${runid}_recording-eyegaze_physio.tsv.gz sub-${subid}/sub-${subid}_task-movie_run-${runid}_events.tsv 0.0185581232561 1000.0"
  done
done

for sub in sub-22 sub-23 sub-24 sub-25 sub-26 sub-27 sub-28 sub-29 sub-30 sub-31 sub-32 sub-33 sub-34 sub-35 sub-36; do
  subid=$(echo "$sub" | cut -d '-' -f2-)
  mkdir -p sub-$subid
  for run in run-1 run-2 run-3 run-4 run-5 run-6 run-7 run-8; do
    runid=$(echo "$run" | cut -d '-' -f2-)
    echo "code/detect_events.py inputs/raw_eyegaze/sub-${subid}/beh/sub-${subid}_task-movie_run-${runid}_recording-eyegaze_physio.tsv.gz sub-${subid}/sub-${subid}_task-movie_run-${runid}_events.tsv 0.0266711972026 1000.0"
  done
done
