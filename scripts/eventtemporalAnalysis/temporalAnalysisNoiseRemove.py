import matplotlib.pyplot as plt
import numpy as np
from os import listdir, getcwd, system
from os.path import isfile, join, isdir, normpath
from scipy.ndimage import gaussian_filter
from scipy.signal import find_peaks

def getFirstPeaks(peaks, timewindow):
    firstpeaks = []
    for i in range(len(peaks)):
        if i == len(peaks)-1 and len(firstpeaks) != 0 and firstpeaks[-1] != peaks[i-1]:
            firstpeaks.append(peaks[i])
            continue
        elif i== len(peaks) -1:
            break
        if peaks[i+1]-peaks[i] < 1/20 * (1000000/timewindow):
            firstpeaks.append(peaks[i])
    return firstpeaks

def getWidths(widths, peaks, firstpeaks, secondpeaks, timewindow):
    firstwidths = np.full_like(firstpeaks, -99999)
    secondwidths = np.full_like(secondpeaks, -99999)
    firstpeak_indx = 0
    secondpeak_indx = 0
    for (width, peak) in zip(widths, peaks):
        if(firstpeak_indx <= len(firstpeaks) -1 and peak == firstpeaks[firstpeak_indx]):
            firstwidths[firstpeak_indx] = width * (1000000/timewindow)
            firstpeak_indx +=1
            
        elif( secondpeak_indx <= len(secondpeaks) -1 and peak == secondpeaks[secondpeak_indx]):
            secondwidths[secondpeak_indx] = width * (1000000/timewindow)
            secondpeak_indx +=1
        else:
            pass

    return (firstwidths, secondwidths)

def getSecondPeaks(peaks, timewindow):
    secondpeaks = []
    for i in range(len(peaks)):

        if i == len(peaks)-1 and len(secondpeaks) != 0 and secondpeaks[-1] != peaks[i-1]:
            secondpeaks.append(peaks[i])
            continue
        elif i== len(peaks) -1:
            break
        if peaks[i+1]-peaks[i] >= 1/20 * (1000000/timewindow):
            secondpeaks.append(peaks[i])
    return secondpeaks

def savefig(path, timewindow, maxdepth = 3):
    if maxdepth == 0:
        return
    else:
        maxdepth -=1
    print("in: ", path)
    #get files in dir
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    
    for file_current in onlyfiles:
        if file_current[-3:] == "npy": #and file_current[:-4]+"_figure.png" not in onlyfiles:
            print("load np array dv tranform")
            nparray = np.load(join(path,file_current), allow_pickle=True)
            print("loaded array", nparray.shape)
            #change zeros to nan
            if(nparray.size == 0 or nparray.shape[0] == 0):
                continue
            
            
            
            v = (nparray[-1][2]/timewindow)
            print("length",v)
            countevents = np.zeros(int(np.ceil(v)))
            i = 0
            for e in np.nditer(nparray[:,2]):
                countevents[int(e/timewindow)] +=1#
            
            smoothedSignal = gaussian_filter(countevents, 1)
            min_height = np.max(smoothedSignal)/3.5
            peaks, properties = find_peaks(smoothedSignal, height=min_height, distance= int(np.ceil((1.0/80) * (1000000/timewindow))), \
                width=1, rel_height=0.6)
            

            firstpeaks = getFirstPeaks(peaks, timewindow)
            secondpeaks = getSecondPeaks(peaks, timewindow)
            #countevents[ countevents==0 ] = np.nan
            print("plotting")
            plt.plot(countevents, linewidth = 0.1, color = "r")
            plt.plot(smoothedSignal, linewidth = 0.2, color = "g")

            plt.plot(firstpeaks, smoothedSignal[firstpeaks], "x", color = "b")
            plt.plot(secondpeaks, smoothedSignal[secondpeaks], "x", color = "c")


            plt.plot(np.full_like(smoothedSignal, min_height), "--", color = "gray", linewidth = 0.2)
            plt.hlines(y=properties["width_heights"], xmin=properties["left_ips"], xmax=properties["right_ips"], color = "C1")
            plt.ylabel('number of events')
            plt.xlabel("timewindow  in"+str(timewindow)+" \u03BCs")
            plt.savefig(join(path, file_current[:-4]+"_figure_filtered.png"), dpi=200, orientation='landscape', format ="png", )
            plt.clf()
            plt.cla()
            print("saved file")


            #calculate the variances without gaussian mixture models
            first_widths, rightwidths = getWidths(properties["widths"], peaks, firstpeaks, secondpeaks, timewindow)
            spanfirst = np.average(first_widths)
            spansecond = np.average(rightwidths)

            heightfirst = np.average(smoothedSignal[firstpeaks])
            heightsecond = np.average(smoothedSignal[secondpeaks])
            stringToSafe =  "time window:                  "+str(timewindow) +" microseconds\n"\
                            "total peaks found:            "+ str(len(peaks)) +"\n"\
                            "first peaks average span:     "+str(spanfirst) +" microseconds\n"\
                            "second peaks average span:    "+str(spansecond) +" microseconds\n\n"\
                            "first peaks average height:   "+str(heightfirst)+" events per time window\n"\
                            "second peaks average height:  "+str(heightsecond) +" events per time window"
            f= open(join(path, file_current[:-4]+"_stats.txt"),"w+")
            f.write(stringToSafe)
            f.close()
        
    #call for all subdirs
    subdirs = [join(path, o) for o in listdir(path) if isdir(join(path,o))] 
    print("subdirs are: ", subdirs)
    for x in subdirs:
        print("x: ", x)
        savefig(x, timewindow, maxdepth)




#for current dir
#startpath = getcwd()
#
testpath = "C:\\Users\\dominik\\OneDrive\\Dokumente\\TU\\KTH\\Module\\P3\\degreeProject\\cameraRecordings\\flashTest2.0"
startpath = normpath(testpath)
timewindow = int(input("enter timewindow in \u03BCs:"))
savefig(startpath, timewindow, 5)


