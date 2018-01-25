#!/usr/bin/python
import glob
import pandas as pd

list = glob.glob("*sub*")

for subject in list:

	allFiles = glob.glob(subject+"/events_run*.gz")
	frame = pd.DataFrame()
	list_ = []
	for file_ in allFiles:
		df = pd.read_csv(file_,index_col=None, header=None,delim_whitespace=True)
		list_.append(df)
	frame = pd.concat(list_, ignore_index= True)
	frame.columns = ["type","t_start","t_end","x_start","y_start","x_end","y_end","amplitude","peak_vel","avg_velocity","duration"]
	frame.to_csv(subject+'/combined.csv', index = False)
