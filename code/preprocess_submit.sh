#!/bin/bash

set -e
set -u


###input argument description
# 1. filename of the condor script to be edited
# 2. subject id
# 3. task id

#subject_list="$1"
#req_task_list="$2"
#mask_image_list="$3"
#filename="$4"


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
    echo "arguments= code/preprocess_eyegaze_recordings.py 0.0185581232561 /home/asimio/fg_eyegaze_preproc/inputs/raw_eyegaze/sub-${subid}/ses-movie/func/sub-${subid}_ses-movie_task-movie_run-${runid}_recording-eyegaze_physio.tsv.gz sub-${subid}/eyegaze_run-${runid}_preprocessed.tsv.gz" >> $condor_script
    echo "Queue" >> $condor_script
  done
done

for sub in sub-22 sub-23 sub-24 sub-25 sub-26 sub-27 sub-28 sub-29 sub-30 sub-31 sub-32 sub-33 sub-34 sub-35 sub-36; do
  subid=$(echo "$sub" | cut -d '-' -f2-)
  mkdir -p sub-$subid
  for run in run-1 run-2 run-3 run-4 run-5 run-6 run-7 run-8; do
    runid=$(echo "$run" | cut -d '-' -f2-)
    echo "arguments= code/preprocess_eyegaze_recordings.py 0.0266711972026 /home/asimio/fg_eyegaze_preproc/inputs/raw_eyegaze/sub-${subid}/beh/sub-${subid}_task-movie_run-${runid}_recording-eyegaze_physio.tsv.gz sub-${subid}/eyegaze_run-${runid}_preprocessed.tsv.gz" >> $condor_script
    echo "Queue" >> $condor_script
  done
done

#IFS=', ' read -a subject_array <<< "$subject_list"
#IFS=', ' read -a task_array <<< "$req_task_list"
#IFS=', ' read -a mask_array <<< "$mask_image_list"
#declare -a filter_type=('lp' 'hp' 'bp' 'bs')

#for mask in "${mask_array[@]}"; do
#    for subject in "${subject_array[@]}"; do
#        echo 'Processing : ' $subject
#        for task in "${task_array[@]}"; do
#            for filter in "${filter_type[@]}"; do        
#                for FWHM in {1..1}; do
#                    echo $subject
#
#                    echo "arguments = \"$MVPA_call\"" | sed -e s/'subject'/$subject/g -e s/'req_task'/$task/g -e s/'req_filter'/$filter/g -e s/'FWHM'/$FWHM/g -e s/'req_mask'/$mask/g >> $condor_script
#                    echo "error  = $condor_output_folder/$subject.$filter.$FWHM.err" >> $condor_script
#                    echo "output = $condor_output_folder/$subject.$filter.$FWHM.out" >> $condor_script
#                    echo "log = $condor_output_folder/$subject.$filter.$FWHM.log" >> $condor_script
#                   echo "Queue" >> $condor_script
#
#
#
#                done
#            done
#        done
#    done
#done

condor_submit $condor_script
#echo "mysubmitfilecontent" | condor_submit -
watch condor_q spark




















###subject_list=$1
###session_list="$2"
###pval="$3"
###zthresh="$4"
###filename="$5"
###fsf_folder="GLM/fsf_folder"
###fsf_file=$fsf_folder"/"$filename
###condor_script="code/condor/run_GLM.submit"
###condor_output_folder="condor_output/GLM"
###mkdir -p $condor_output_folder
###rm -f $condor_script

######initialize environment in condor submit file
###initialization_string="universe = vanilla
###executable = /usr/bin/fsl5.0-feat
###initialdir = /home/data/psyinf/multires7T/analysis
###request_cpus = 1
###request_memory = 8000
###getenv = True"


###echo "$initialization_string" > $condor_script


###IFS=', ' read -a subject_list <<< "$subject_list"
###IFS=', ' read -a session_list <<< "$session_list"


###for subject in "${subject_list[@]}"; do
###    echo 'Processing : ' $subject

###    for session in "${session_list[@]}"; do
###        ###if [ $filename != 'design_level_2.fsf' ]; then
###        if [ $filename != 'design_surface_level_2.fsf' ]; then     
###            for run_id in {1..10}; do
###                #run_folder=$fsf_folder"/"$subject"/"$session"/task-orientation_run-$(zeropad $run_id 2)"
###                mkdir -p $fsf_folder'/'$subject'/'$session
###                run_fsf_file=$fsf_folder"/"$subject"/"$session"/task-orientation_run-$(zeropad $run_id 2)_"$filename
###                cp $fsf_file $run_fsf_file
###                sed -i s/'sub'/$subject/g $run_fsf_file
###                sed -i s/'sess'/$session/g $run_fsf_file
###                sed -i s/'run'/"run-$(zeropad $run_id 2)"/g $run_fsf_file
###                sed -i s/'pval'/$pval/g $run_fsf_file
###                sed -i s/'zthresh'/$zthresh/g $run_fsf_file
###                #~ 
###                #~ 
###                echo "arguments = $run_fsf_file" >> $condor_script
###                echo "error  = $condor_output_folder/$subject.$session.$run_id.err" >> $condor_script
###                echo "output = $condor_output_folder/$subject.$session.$run_id.out" >> $condor_script
###                echo "log = $condor_output_folder/$subject.$session.$run_id.log" >> $condor_script
###                echo "Queue" >> $condor_script
###            done
###        else
###            #run_folder=$fsf_folder"/"$subject"/"$session"/task-orientation_run-$(zeropad $run_id 2)"
###            mkdir -p $fsf_folder'/'$subject'/'$session
###            level2_fsf_file=$fsf_folder"/"$subject"/"$session"/"$filename
###            cp $fsf_file $level2_fsf_file
###            sed -i s/'sub'/$subject/g $level2_fsf_file
###            sed -i s/'sess'/$session/g $level2_fsf_file
###            sed -i s/'pval'/$pval/g $level2_fsf_file
###            sed -i s/'zthresh'/$zthresh/g $level2_fsf_file
###            #~ 
###            #~ 
###            echo "arguments = $level2_fsf_file" >> $condor_script
###            echo "error  = $condor_output_folder/$subject.$session.err" >> $condor_script
###            echo "output = $condor_output_folder/$subject.$session.out" >> $condor_script
###            echo "log = $condor_output_folder/$subject.$session.log" >> $condor_script
###            echo "Queue" >> $condor_script        
###    
###        fi
###    done
###done

###condor_submit $condor_script
####watch condor_q spark


