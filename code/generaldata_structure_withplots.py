#!/usr/bin/python
#Assigning all the pieces of data per subject into a dictionary with the name of the subject/run as the dictionary key. Inside the dictionary they are saved as dataframes in pandas ready for analysis.

import glob
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


list = glob.glob("*sub*")

dictofsamples = {}

for subject in list:

	allFiles = glob.glob(subject+"/events_run*.gz")
	frame = pd.DataFrame()
	
	for run in allFiles:
		df = pd.read_csv(run,index_col=None, header=None,delim_whitespace=True)
		df.columns = ["type","t_start","t_end","x_start","y_start","x_end","y_end","amplitude","peak_vel","avg_velocity","duration"]
		dictofsamples["{0}".format(run)]= df
		
		
# Figure 5.1 demands plotting of saccade values of the entire dataset as a frequency distribution.

# Making a list containg all the subjects and samples

listfor5_1 = dictofsamples.keys()

# Concatenate the dataframes into one big one

allsubsrun = pd.DataFrame()

for i in listfor5_1:
	
	allsubsrun = allsubsrun.append(dictofsamples[i])
	
	
# Extracting lines only that contrain type "SACCADE"

# Make a boolean series if SACCADE or not
saccades = allsubsrun.type == "SACCADE"

# Seeking out only saccades from the dataset
saccadesonly = allsubsrun[saccades]
saccadegraph = sns.distplot(saccadesonly.duration,kde=False,norm_hist=True)
plt.xlim(0, 100)
plt.ylim(0, 0.07)
saccadegraph.set(xlabel='Saccade Duration in ms')
plt.title('Saccade durations over all subjects')
plt.show()






#saccadegraph.figure.savefig("output.png")


	
