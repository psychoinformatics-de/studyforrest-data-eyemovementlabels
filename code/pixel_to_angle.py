# Sebastiaan Mathot (modified)
# -*- coding: iso-8859-15 -*-


from math import atan2, degrees
h = 52.2 # Monitor width in cm, this is the BEH screen
d = 85 # Distance between monitor and participant in cm
r = 1280 # Horizontal resolution of the monitor
size_in_px = 1 # The stimulus size in pixels
# Calculate the number of degrees that correspond to a single pixel. This will
# generally be a very small value, something like 0.03.
deg_per_px = degrees(atan2(.5*h, d)) / (.5*r)
print '%s degrees correspond to a single pixel' % deg_per_px
# Calculate the size of the stimulus in degrees
size_in_deg = size_in_px * deg_per_px
print 'The size of the stimulus is %s pixels and %s visual degrees' \
    % (size_in_px, size_in_deg)


#h = 26.5 # Monitor width in cm 
#d = 63 # Distance between monitor and participant in cm
#This is for the MRI screen

#Checking from paper
#MRI
#In [1]: 0.0185581232561*1280
#Out[1]: 23.754397767808
#BEH
#In [2]: 0.0266711972026*1280
#Out[2]: 34.139132419328

#Calculating the ratio
#In [7]: 0.0185581232561*0.01
#Out[7]: 0.000185581232561

#In [8]: 0.000185581232561/0.0266711972026
#Out[8]: 0.006958114071568895
