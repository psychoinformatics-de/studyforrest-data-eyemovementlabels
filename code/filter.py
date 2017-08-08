import numpy as np
from scipy.signal import savgol_filter
import os


path="D:\\BA - Kopie\\data\\lab\\"
dirs=os.listdir(path)
for file in dirs:
    a= open(os.path.join(path, file),"r")
    name= os.path.basename(a.name)
    run=(name[5:6]) if len(name)==10 else (name[8:9])
    out=open("D:\\BA - Kopie\\saccdata\\savgol\\lab\\"+name[0:2]+"sacc"+run+".txt","wb")

    xlist=[]
    ylist=[]
    count=0
    time=[]
    sec=0
    while True:
    	line=a.readline()
    	if not line: break
    	num=line.split()
    	sec+=1
    	if num[0]=="0.0":                       # indicates signal, including but not limited to blinks
    		count+=1

    		continue

    	elif count>20:                          # for signal loss exceeding 20 ms, additional 10 ms at beginning
    		for i in range(10):                  # and end are disregarded
    			if xlist and ylist and time:
    				xlist.pop()
    				ylist.pop()
    				time.pop()

    		for i in range(9):
    			line=a.readline()
    			sec+=1

    		count=0
    		continue

    	x=float(num[0])
    	y=float(num[1])
    	xlist.append(x)
    	ylist.append(y)
    	time.append(sec)

    a.close()

####### median filter #############

#    for i in range(len(xlist)-8):
#        xlist[i]=np.mean(xlist[i:i+9])
#        ylist[i]=np.mean(ylist[i:i+9])


###### savgol filter ##############
    xlist=savgol_filter(xlist,9,1)
    ylist=savgol_filter(ylist,9,1)


    #velocity calculation, exclude velocities over 1000

    vel=[float(0)]
    i=0
    while i<len(xlist)-1:
            d=((xlist[i]-xlist[i+1])**2+(ylist[i]-ylist[i+1])**2)**0.5
            d=d*0.01*1000
            if d<1000:
                vel.append(d)
            else:
                vel.append(vel[len(vel)-1])

            i+=1

    #acceleration calculation

    acc=np.diff(vel)/0.001
    acc=np.insert(acc,0,float(0))

    #save data to file

    data=np.array([vel, acc, time, xlist, ylist])
    data=data.T
    np.savetxt(out, data, fmt=['%.1f', '%.1f', '%d', '%.1f', '%.1f'])

    out.close()

