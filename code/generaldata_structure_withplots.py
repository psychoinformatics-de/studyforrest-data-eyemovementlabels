#!/usr/bin/python
#Assigning all the pieces of data per subject into a dictionary with the name of the subject/run as the dictionary key. Inside the dictionary they are saved as dataframes in pandas ready for analysis.

import glob
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
from numpy.polynomial import Polynomial


list = glob.glob("*sub*")

dictofsamples = {}

for subject in list:

	allFiles = glob.glob(subject+"/events_run*.gz")
	frame = pd.DataFrame()
	
	for run in allFiles:
		df = pd.read_csv(run,index_col=None, header=None,delim_whitespace=True)
		df.columns = ["type","t_start","t_end","x_start","y_start","x_end","y_end","amplitude","peak_vel","avg_velocity","duration"]
		dictofsamples["{0}".format(run)]= df
		
		
### Figure 5.1 demands plotting of saccade values of the entire dataset as a frequency distribution.

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

# Plotting
plt.figure()
saccadegraph = sns.distplot(saccadesonly.duration,kde=False,norm_hist=True)
plt.xlim(10, 100)
plt.ylim(0, 0.07)
saccadegraph.set(xlabel='Saccade Duration in ms')
plt.title('Saccade durations over all subjects')
plt.show()

### Figure A2 All peak velocities plotted against the amplitudes
plt.figure()
# Sort out data as above, but now for only subject 24, run 4
subject24_4 = dictofsamples['sub-24/events_run-4.tsv.gz']
a2saccades = subject24_4.type == "SACCADE"

a2saccadesonly = subject24_4[a2saccades] 

# Plotting
velampgraph = sns.regplot(a2saccadesonly.amplitude,a2saccadesonly.peak_vel,fit_reg = False,scatter_kws={"s": 1})
plt.title('Relationship between peak velocity and amplitude')
velampgraph.set(xlabel='Amplitude', ylabel= 'Peak Velocity')
# Inserting a fit for the scatter plot, degree = 5
p = Polynomial.fit(a2saccadesonly.amplitude,a2saccadesonly.peak_vel,5)
plt.plot(*p.linspace())
plt.show()

### Figure A3 All saccade amplitudes

plt.figure()
saccadeampgraph = sns.distplot(saccadesonly.amplitude,kde=False,norm_hist=True)
saccadeampgraph.set(xlabel='Saccade Amplitude in deg/s')
plt.xlim(0, 16)
plt.title('Saccade amplitudes over all subjects')
plt.show()

### Figure A4 All saccade peak velocities

plt.figure()
saccadepvgraph = sns.distplot(saccadesonly.peak_vel,kde=False,norm_hist=True)
saccadepvgraph.set(xlabel='Saccade peak velocity in deg/s')
plt.xlim(0, 800)
plt.title('Saccade peak velocities over all subjects')
plt.show()

### Figure A5 All saccade peak_vel * duration (done for Subject 24, run 4)

plt.figure()
product = a2saccadesonly.duration * a2saccadesonly.peak_vel
productgraph = sns.regplot(a2saccadesonly.amplitude, product,fit_reg = True,scatter_kws={"s": 1}, line_kws={"color":"r","lw":1})
productgraph.set(ylabel='Product of peak velocity and duration', xlabel = 'Amplitude in deg/s')
plt.xlim(0, 20)
plt.ylim(0, 30000)
plt.title('Relationship between amplitude and the product of peak velocity and duration ')
plt.show()

## Sorting out Data to yield the data for tables
## Table 5.1

# Input run_number (segment) will yield a dataframe with all the data in that segment (only!) across all subjects
def makelist(run_number):
	
	dataframe = pd.DataFrame()
	
	for i in dictofsamples.keys():
		if ("run-"+str(run_number)) in i:
			dataframe = dataframe.append(dictofsamples[i])
			
			
	return dataframe
	
def findvalues (segment):
	"""
	For the given segment (input a simple integer) a dataframe will be returned with means and std (as strings) to be printed on a table
	
	"""
	
	saccades = segmentlist['segment'+str(segment)].type == "SACCADE"
	saccadesonly = segmentlist['segment'+str(segment)][saccades]
	dur_mean,amp_mean,peak_velmean =  saccadesonly.duration.mean(), saccadesonly.amplitude.mean(),saccadesonly.peak_vel.mean()
	dur_std,amp_std,peak_velstd =  saccadesonly.duration.std(), saccadesonly.amplitude.std(),saccadesonly.peak_vel.std()
	df = pd.DataFrame ({'#' : ['{0}'.format(segment)],'Duration' : ["{0:.2f} ± {1:.2f}".format(dur_mean,dur_std)], 'Amplitude' : ["{0:.2f} ± {1:.2f}".format(amp_mean,amp_std)], 'Peak Velocity' : ["{0:.2f} ± {1:.2f}".format(peak_velmean,peak_velstd)]})
	
	return df

	
# Make a dictionary with all the subject data, assorted by the segment

segmentlist = {}
for run in range (1,9):
	segmentlist["segment{0}".format(run)]= makelist(run)
	
# Run through all segments, finding out values that are needed

data = pd.DataFrame()

for run in range (1,9):
	data = data.append(findvalues(run))
