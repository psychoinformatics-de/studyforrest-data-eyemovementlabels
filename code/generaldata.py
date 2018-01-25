#!/usr/bin/python
#Assigning all the pieces of data per subject into a dictionary with the name of the subject/run as the dictionary key. Inside the dictionary they are saved as dataframes in pandas ready for analysis.

import glob
import pandas as pd
import seaborn as sns

list = glob.glob("*sub*")

dictofsamples = {}

for subject in list:

	allFiles = glob.glob(subject+"/events_run*.gz")
	frame = pd.DataFrame()
	
	for run in allFiles:
		df = pd.read_csv(run,index_col=None, header=None,delim_whitespace=True)
		df.columns = ["type","t_start","t_end","x_start","y_start","x_end","y_end","amplitude","peak_vel","avg_velocity","duration"]
		dictofsamples["{0}".format(run)]= df
	
