import numpy as np
import os



path="D:\\BA - Kopie\\saccdata\\savgol\\lab"
dirs=os.listdir(path)
for file in dirs:
    f= open(os.path.join(path, file),"r")
    name= os.path.basename(f.name)
    vp=int(name[0:2])
    #run=int(name[6:7])
    run=int(name[5:6]) if len(name)<11 else int(name[8:9])
    out=open("D:\\BA - Kopie\\output saccades\\new\\includefix\\smooth\\"+str(vp)+"run"+str(run)+".txt", "w")

    newThr=200


    file=[]
    line=f.readline()
    while line:
        num=line.split()
        file.append(num)
        line=f.readline()
    f.close()

#####get threshold function #######
    def getThresh(cut):
        temp=[]
        i=0
        while i<len(file):
            if float((file[i])[0])<cut:
                temp.append(float((file[i])[0]))
            i+=1

        avg=np.mean(temp)
        sd=np.std(temp)
        return avg+6*sd, avg, sd

###### threshold function #########


    avg=0
    sd=0
    dif=2

    while dif>1:
        oldThr=newThr
        newThr, avg, sd=getThresh(oldThr)
        dif=abs(oldThr-newThr)

    threshold=newThr
    print("after thr selection", threshold)


####get peaks####
    peaks=[]

    for i in range(len(file)-1):
        if float((file[i])[0])<threshold and float((file[i+1])[0])>threshold:
            peaks.append(i+1)

    p=0
    fix=[]
    while p<len(peaks):
        idx=peaks[p]
        pval=[]
        while float((file[idx])[0])>avg+3*sd and idx!=0:
            pval.append(float((file[idx])[0]))
            idx-=1
        idx+=1
        ts=float((file[idx])[2])                     ###saccade onset
        xs=float((file[idx])[3])
        ys=float((file[idx])[4])
        fix.append(-idx)

        temp=[]
        for i in range (1,41):
            temp.append(float((file[idx-i])[0]))
        offAvg=np.mean(temp)
        offSd=np.std(temp)

        idx=peaks[p]+1
        while idx<len(file) and float((file[idx])[0])>(0.7*(avg+3*sd)+0.3*(offAvg+3+offSd)):
            pval.append(float((file[idx])[0]))
            idx+=1
        idx-=1
        te=float((file[idx])[2])                     ###saccade offset
        xe=float((file[idx])[3])
        ye=float((file[idx])[4])
        fix.append(idx)

        if len(pval)>9 and len(pval)+10>(te-ts+1):      ####minimum duration 9 ms and no blinks allowed
            pv=max(pval)
            amp=(((xs-xe)**2+(ys-ye)**2)**0.5)*0.01
            amp= "%.2f" % amp
            avVel=np.mean(pval)
            s= " "
            seq=("SACC", str(ts), str(te), str(xs), str(ys), str(xe), str(ye), amp, str(pv), str(avVel), '\n')
            out.write(s.join(seq))


####### end of saccade detection = begin of glissade detection ########
        idx+=1
        below=False
        offset=False
        pval=[]
        for d in range(40):
            if idx+d>=len(file)-1: break
            pval.append(float((file[idx+d])[0]))
            if float((file[idx+d])[0])<avg+3*sd and float((file[idx+d-1])[0])>avg+3*sd:
                below=True
            if below and float((file[idx+d])[0])-float((file[idx+d+1])[0])<=0:
                ts=float((file[idx+d])[2])
                xs=float((file[idx+d])[3])
                ys=float((file[idx+d])[4])
                offset=True
        idx=idx+d
        if offset and len(pval)+11>ts-te+1:      #not more than 10 ms of signal loss in glissades
            pv=max(pval)
            amp=(((xs-xe)**2+(ys-ye)**2)**0.5)*0.01
            amp= "%.2f" % amp
            avVel=np.mean(pval)
            s= " "
            seq=("GLISS", str(te), str(ts), str(xe), str(ye), str(xs), str(ys), amp, str(pv), str(avVel), '\n')
            out.write(s.join(seq))
            fix.pop()
            fix.append(idx)

######## end of glissade detection #######

        if idx>peaks[p]:
            while p<len(peaks) and idx>=peaks[p]:
                p+=1
        else:
            p+=1
######## fixation detection after everything else is identified ########

    j=0

    while j<len(fix)-1:
        if fix[j]>0 and abs(fix[j+1])-fix[j]>40:          #onset of fixation
              ts=float((file[fix[j]])[2])
              xs=float((file[fix[j]])[3])
              ys=float((file[fix[j]])[4])

              te=float((file[abs(fix[j+1])])[2])
              xe=float((file[abs(fix[j+1])])[3])
              ye=float((file[abs(fix[j+1])])[4])

              pval=[]
              for i in range(fix[j],abs(fix[j+1])):
                  pval.append(float((file[i])[0]))

              #pv=max(pval)
              amp=(((xs-xe)**2+(ys-ye)**2)**0.5)*0.01

              avVel=np.mean(pval)
              if avVel<6.58 and amp<2 and len(pval)+11>(te-ts)+1:
                  amp= "%.2f" % amp
                  s= " "
                  seq=("FIX", str(ts), str(te), str(xs), str(ys), str(xe), str(ye), amp, str(avVel), '\n')
                  out.write(s.join(seq))
        j+=1


    out.close()
    print ("done")

