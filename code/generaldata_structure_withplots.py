# -*- coding: utf-8 -*-
#!/usr/bin/python
#Assigning all the pieces of data per subject into a dictionary with the name of the subject/run as the dictionary key. Inside the dictionary they are saved as dataframes in pandas ready for analysis.

#Run from root

import glob
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
from numpy.polynomial import Polynomial
from scipy import stats
import matplotlib.ticker as ticker

import pdb
#pdb.set_trace() to set breakpoint


fulllist = glob.glob("*sub*")
fulllist.sort()

#TODO: Assign inputs to determin this, or simply input at start of script input('Show results for? 1-both 2-Beh 3-MRI') followed by downstream changes
list = fulllist     #for both 
#list = fulllist[15:] #for beh
#list = fulllist[0:15] # for MRI

dictofsamples = {}


for subject in list:

	allFiles = glob.glob(subject+"/*.tsv")
	frame = pd.DataFrame()
	
	for run in allFiles:
		df = pd.read_csv(run,index_col=None, header=0,delim_whitespace=True)
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
pdb.set_trace() #DELETE
saccades = (allsubsrun.label == "SACC") | (allsubsrun.label == "ISAC")

# Seeking out only saccades from the dataset
saccadesonly = allsubsrun[saccades]

# Plotting
plt.figure()
# duration * 1000 to convert to ms
saccadegraph = sns.distplot(saccadesonly.duration*1000,kde=False,norm_hist=True,bins=100)
plt.xlim(0, 100)
#plt.ylim(0, 0.07)
saccadegraph.set(xlabel='Saccade Duration [ms]')
plt.title('Saccade durations over all subjects')
plt.draw()

### Figure A2 All peak velocities plotted against the amplitudes
plt.figure()
# Sort out data as above, but now for only subject 24, run 4
subject24_4 = dictofsamples['c24/sub-24_task-movie_run-4_events.tsv'] # currently manually replacing with random subject (9) in MRI
a2saccades = (subject24_4.label == "SACC") | (subject24_4.label == "ISAC")

a2saccadesonly = subject24_4[a2saccades] 

# Plotting 
velampgraph = sns.regplot(a2saccadesonly.amp,a2saccadesonly.peak_vel,fit_reg = False,scatter_kws={"s": 15})
#velampgraph = sns.scatterplot(x= "amp", y="peak_vel", data = a2saccadesonly) No idea why this doesn't work
plt.title('Relationship between peak velocity and amplitude (subject 24)')
velampgraph.set(xlabel='Amplitude', ylabel= 'Peak Velocity',yscale="log",xscale="log")


# Inserting a fit for the scatter plot, degree = 1
#p = Polynomial.fit(a2saccadesonly.amp,a2saccadesonly.peak_vel,1)
#plt.plot(*p.linspace())

plt.draw()

### Figure A3 All saccade amplitudes

plt.figure()
saccadeampgraph = sns.distplot(saccadesonly.amp,kde=False,norm_hist=True,bins=100)
saccadeampgraph.set(xlabel='Saccade Amplitude in deg')
#plt.xlim(0, 16)
plt.title('Saccade amplitudes over all subjects')
plt.draw()

### Figure A4 All saccade peak velocities

plt.figure()
saccadepvgraph = sns.distplot(saccadesonly.peak_vel,kde=False,norm_hist=True, bins  = 50)
saccadepvgraph.set(xlabel='Saccade peak velocity in deg/s')
#plt.xlim(0, 800)
saccadepvgraph.xaxis.set_major_locator(ticker.MultipleLocator(50))
saccadepvgraph.xaxis.set_major_formatter(ticker.ScalarFormatter())
plt.title('Saccade peak velocities over all subjects')
plt.draw()

### Figure A5 All saccade peak_vel * duration (done for Subject 24, run 4)

plt.figure()
product = a2saccadesonly.duration * 1000 * a2saccadesonly.peak_vel
productgraph = sns.regplot(a2saccadesonly.amp, product,fit_reg = True,scatter_kws={"s": 1}, line_kws={"color":"r","lw":1})
productgraph.set(ylabel='Product of peak velocity and duration', xlabel = 'Amplitude in deg')
#plt.xlim(0, 20)
#plt.ylim(0, 30000)
plt.title('Relationship between amplitude and the product of peak velocity and duration ')
plt.draw()

## Sorting out Data to yield the data for tables TODO: save as separate script

## Table 5.1

# Input run_number (segment) will yield a dataframe with all the data in that segment (only!) across all subjects

def makelist(run_number,dictionary):
	
	dataframe = pd.DataFrame()
	
	for i in dictionary.keys():
		if ("run-"+str(run_number)) in i:
			dataframe = dataframe.append(dictionary[i])
			
			
	return dataframe
	
def findvalues (segment):
	"""
	For the given segment (input a simple integer) a dataframe will be returned with means and std (as strings) to be printed on a table
	
	"""
	
	saccades = (segmentlist['segment'+str(segment)].label == "SACC") | (segmentlist['segment'+str(segment)].label == "ISAC")
	saccadesonly = segmentlist['segment'+str(segment)][saccades]
	dur_mean,amp_mean,peak_velmean =  saccadesonly.duration.mean(), saccadesonly.amp.mean(),saccadesonly.peak_vel.mean()
	dur_std,amp_std,peak_velstd =  saccadesonly.duration.std(), saccadesonly.amp.std(),saccadesonly.peak_vel.std()
	df = pd.DataFrame ({'#' : ['{0}'.format(segment)],'Duration' : ["{0:.2f} ± {1:.2f}".format(dur_mean*1000,dur_std*1000)], 'Amplitude' : ["{0:.2f} ± {1:.2f}".format(amp_mean,amp_std)], 'Peak Velocity' : ["{0:.2f} ± {1:.2f}".format(peak_velmean,peak_velstd)]})
	
	return df
	
def saccadecount(run_number):
	"""
	Returns saccade count average and std in stated run across all subjects (as string)
	"""
	
	list = []
	
	for i in dictofsamples.keys():
		if ("run-"+str(run_number)) in i:
			saccades = (dictofsamples[i].label == "SACC")| (dictofsamples[i].label == "ISAC")
			saccadecount = np.sum(saccades)
			list.append(saccadecount)
			
	array = np.array(list)
	mean  = array.mean() 
	std   = array.std()
				
	return ("{0:.2f} ± {1:.2f}".format(mean, std))
	
def makecountlist(run_number,dictionary):
	"""
	Looks into preproc files to find nans and then determines sec per minute lost and percent of total lost
	"""
	nancount = 0.0
	linecount = 0.0
	
	for i in dictionary.keys():
		if ("run-"+str(run_number)) in i:
			linecount += dictionary[i]['Velocity'].size
			nancount += np.sum(np.isnan(dictionary[i].Velocity))
			
	secpermin_loss = (nancount*0.001)/(linecount*(0.001/60))
	percentlost   = (nancount/linecount) * 100
			
			
	return secpermin_loss, percentlost
	
def findamppeak (segment):
	"""
	For the given segment (input a simple integer) slope and r value of the regression line will be given 
	For the stats log of each is taken
	"""
	
	peakvel = segmentlist['segment'+str(segment)].peak_vel
	amplitude = segmentlist['segment'+str(segment)].amp
	
	# in the case erroneous data is found (amp = 0)
	if min(amplitude) == 0:
		print ("Number of 0 valued amplitudes found :", len(segmentlist['segment'+str(segment)].amp[segmentlist['segment'+str(segment)].amp==0]))
		cleanset = segmentlist['segment'+str(segment)]
		cleanset = cleanset[cleanset.amp != 0]
		peakvel =  cleanset.peak_vel
		amplitude = cleanset.amp	
	
	segmentlist['segment'+str(segment)].amp [segmentlist['segment'+str(segment)].amp == 0]
	
	slope, intercept, r_value, p_value, std_err = stats.linregress(np.log(amplitude),np.log(peakvel))
		
	return slope, r_value

def findvaluesG (segment):
	"""
	For the given segment (input a simple integer) a dataframe will be returned with means and std (as strings) to be printed on a table
	
	"""
	
	gliccades = (segmentlist['segment'+str(segment)].label == "LPSO") | (segmentlist['segment'+str(segment)].label == "HPSO")
	gliccadesonly = segmentlist['segment'+str(segment)][gliccades]
	dur_mean,amp_mean =  gliccadesonly.duration.mean(), gliccadesonly.amp.mean()
	df = pd.DataFrame ({'#' : ['{0}'.format(segment)],'Duration' : ["{0:.2f}".format(dur_mean*1000)], 'Amplitude' : ["{0:.2f}".format(amp_mean)]})
	
	return df

def findvaluesF (segment):
	"""
	For the given segment (input a simple integer) a dataframe will be returned with means and std (as strings) to be printed on a table
	
	"""
	
	fixs = segmentlist['segment'+str(segment)].label == "FIXA"
	fixsonly = segmentlist['segment'+str(segment)][fixs]
	dur_mean,velmean =  fixsonly.duration.mean(), fixsonly.avg_vel.mean()
	# Find the average number of fixes by dividing the number of FIX only by the total subjects (=30)
	fix_no = (fixsonly.shape[0])/30 
	df = pd.DataFrame ({'#' : ['{0}'.format(segment)],'Duration' : ["{0:.2f}".format(dur_mean*1000)], 'Fix Mean' : ["{0}".format(fix_no)], 'Average Velocity' : ["{0:.2f}".format(velmean)]})
	
	return df

	
# Make a dictionary with all the subject data, assorted by the segment

segmentlist = {}
for run in range (1,9):
	segmentlist["segment{0}".format(run)]= makelist(run,dictofsamples)
	
# Run through all segments, finding out values that are needed 
# TO DO: FIND A WAY TO PUT THESE IN A PRINTABLE TABLE FORMAT

data = pd.DataFrame()

for run in range (1,9):
	data = data.append(findvalues(run))

# Determining means and std of all the runs and making it into a single column

counts = []

for run in range (1,9):
	counts.append(saccadecount(run))
	
allsaccadecounts = pd.DataFrame ({'No of saccades' : counts})

# Time to put together the two components of Table 5.1

# Change indexes to match one another

data.index= range(1,9)
allsaccadecounts.index = range (1,9)

finaltable5_1 = pd.concat([data, allsaccadecounts], axis=1)
print ("Table 5.1")
print (finaltable5_1)


## Table 5.2 

# Nan lines will be counted as the ones 'removed'. For viewing the majority of the nan members
# we will use preproc files and make all the data available via a dictionary

#dictofsamples_preproc = {}
#
#for subject in list:
#
#	allFiles = glob.glob(subject+"/eyegaze_run*preprocessed.tsv.gz") 
#	frame = pd.DataFrame()
#	
#	for run in allFiles:
#		df = pd.read_csv(run,index_col=None, header=None,delim_whitespace=True)
#		df.columns = ["Velocity","Acceleration","x","y"]
#		dictofsamples_preproc["{0}".format(run)]= df


# Making two lists, one for sec per min loss and second total percent of loss. Didnt append like
# before because of the lack of memory to manage a billion (!) line array 

#secperminlist=[]
#totallostlist=[]
 
#for run in range (1,9):
#	
#	secpermin, totallost = makecountlist(run,dictofsamples_preproc)
#	secperminlist.append(secpermin)
#	totallostlist.append(totallost)
	
#TODO: make into dataframe (see line 134) TODO: AVERAGE SLOPE INSTEAD OF REGRESSION LINE SLOPE

slopelist = []
rvaluelist = []

for run in range (1,9):
	slope, rval = findamppeak (run)
	slopelist.append(slope)
	rvaluelist.append(rval)
	
# Now to make table 5.2 as a dataframe
segs = range(1,9) 

Table5_2 = pd.DataFrame ()
	
for i in range(0,8):
	
	#new_data = pd.DataFrame ({'#' : ['{0}'.format(segs[i])],'Lost Signal' : ["{0:.1f}".format(secperminlist[i])], 'r sqrd' : ["{0:.3f}".format(rvaluelist[i])], 'Samples Removed (%)' : ["{0:.2f}".format(totallostlist[i])],'Slope' : ['{0:.2f}'.format(slopelist[i])]})
	new_data = pd.DataFrame ({'#' : ['{0}'.format(segs[i])], 'r sqrd' : ["{0:.3f}".format(rvaluelist[i])],'Slope' : ['{0:.2f}'.format(slopelist[i])]})

	Table5_2 = Table5_2.append(new_data)



#Table5_2 = Table5_2 [['#', 'Lost Signal','r sqrd', 'Samples Removed (%)', 'Slope']]
Table5_2 = Table5_2 [['#','r sqrd','Slope']]

Table5_2.index= range(1,9)
print ("  ")
print ("Table 5.2")
print (Table5_2)

## Table 5.3 - Gliccade and Fixation data

Table5_3G = pd.DataFrame ()
Table5_3F = pd.DataFrame ()

for run in range (1,9):
	
	new = findvaluesG (run)
	Table5_3G = Table5_3G.append(new)
	
	new = findvaluesF (run)
	Table5_3F = Table5_3F.append(new)

#Getting nutty about specific layouts
Table5_3G = Table5_3G [['#','Duration','Amplitude']]
Table5_3G.index= range(1,9)
Table5_3F.index= range(1,9)

print ("  ")
print ("Table 5.3 - Gliccades")
print (Table5_3G)

print ("  ")

print ("Table 5.3 - Fixations")
print (Table5_3F)



# Show plots 
plt.show()
	
# manually save tables
#finaltable5_1.to_csv('5.1_MRI')
#Table5_2
#Table5_3G
#Table5_3F


