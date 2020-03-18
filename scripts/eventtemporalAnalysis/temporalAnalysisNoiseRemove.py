import matplotlib.pyplot as plt
import numpy as np
from os import listdir, getcwd, system
from os.path import isfile, join, isdir, normpath, pardir, abspath
from scipy.ndimage import gaussian_filter
from scipy.signal import find_peaks
from sklearn.mixture import GaussianMixture
from scipy.stats import norm
import csv

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

def getFirstMeansAndVars(peaks, vars, timewindow):
    firstpeaks = []
    firstvars = []
    for i in range(len(peaks)):
        if i == len(peaks)-1 and len(firstpeaks) != 0 and firstpeaks[-1] != peaks[i-1]:
            firstpeaks.append(peaks[i])
            firstvars.append(vars[i])
            continue
        elif i== len(peaks) -1:
            break
        if peaks[i+1]-peaks[i] < 1/20 * (1000000/timewindow):
            firstpeaks.append(peaks[i])
            firstvars.append(vars[i])
    return (firstpeaks, firstvars)

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

def getSecondMeansAndVars(peaks, vars, timewindow):
    secondpeaks = []
    secondvar = []
    for i in range(len(peaks)):

        if i == len(peaks)-1 and len(secondpeaks) != 0 and secondpeaks[-1] != peaks[i-1]:
            secondpeaks.append(peaks[i])
            secondvar.append(vars[i])
            continue
        elif i== len(peaks) -1:
            break
        if peaks[i+1]-peaks[i] >= 1/20 * (1000000/timewindow):
            secondpeaks.append(peaks[i])
            secondvar.append(vars[i])

    return (secondpeaks, secondvar)

def signalToPoints(signal):
    signal = signal.astype(np.int32)
    dpoints = []
    for i in range(len(signal)):
        dpoints += [i] * signal[i]
    return np.asarray(dpoints, dtype = np.int32)

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



def getNoise(peaks, signal, timewindow):
    indices = np.ones_like(signal, dtype=np.uint8)
    for peak in np.nditer(peaks):
        for i in range(int(peak - 1/30*(1000000/timewindow)), int(peak + 1/30*(1000000/timewindow))):
            if( 0<=i and i < signal.shape[0]):
                indices[i] = 0
    noise_values = signal[indices.astype(np.bool)]
    print("number of noise valuse: ", noise_values.shape, "from ", signal.shape)
    return np.average(noise_values)

def savefig(path, timewindow, maxdepth = 3):
    filename = "_filteredAndGaussianMixture"
    if maxdepth == 0:
        return
    else:
        maxdepth -=1
    print("in: ", path)
    #get files in dir
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    
    for file_current in onlyfiles:
        if file_current == "dvSave-2020_03_06_18_31_21events.npy": #and file_current[:-4]+"_figure.png" not in onlyfiles:
            print("current file: ", file_current)
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
            
            #cut first
            cutfirst = 0
            cutlast = 1
            #print(countevents)
            countevents = countevents[cutfirst:]
            countevents = countevents[:-cutlast]
            smoothedSignal = gaussian_filter(countevents, 1)
            #smoothedSignal = countevents

            min_height = np.max(smoothedSignal)/3.5
            peaks, properties = find_peaks(smoothedSignal, distance= int(np.ceil((1.0/120) * (1000000/timewindow))),height=min_height,  \
                width=1, rel_height=0.6)


            noise = getNoise(peaks, smoothedSignal, timewindow) *1.00
            print("noise:", noise)
            if not np.isnan(noise):
                smothedwithoutnoise = np.subtract(smoothedSignal, int(noise))
                smothedwithoutnoise[smothedwithoutnoise < 0] = 0
            else:
                smothedwithoutnoise = smoothedSignal

            firstpeaks = getFirstPeaks(peaks, timewindow)
            secondpeaks = getSecondPeaks(peaks, timewindow)
            #fit gaussian models
            #peaks = np.append(peaks, 0)
            gaussModel = GaussianMixture(peaks.shape[0], covariance_type="full", means_init=peaks.reshape(-1,1) )
            print("fitting the model with inital guess, ", peaks)
            gaussModel.fit(signalToPoints(smothedwithoutnoise).reshape(-1, 1))
            
            print("plotting the guassians")
            x = np.arange(smothedwithoutnoise.shape[0])
            logprob = gaussModel.score_samples(x.reshape(-1, 1))
            print("SUM:",sum(np.exp(logprob)))
            pdf = np.exp(logprob)
            #normalize
            pdf = pdf * max(smothedwithoutnoise) / max(pdf)
            plt.plot(x, pdf, linewidth = 0.2, color = "g")

            #countevents[ countevents==0 ] = np.nan
            print("plotting others ")
            plt.plot(smoothedSignal, linewidth = 0.1, color = "r")
            #plt.plot(smoothedSignal, linewidth = 0.2, color = "g")
            plt.plot(smothedwithoutnoise, linewidth = 0.3, color= "m")
            

            plt.plot(firstpeaks, smoothedSignal[firstpeaks], "x", color = "b")
            plt.plot(secondpeaks, smoothedSignal[secondpeaks], "x", color = "c")

            #min height
            plt.plot(np.full_like(smoothedSignal, min_height), "--", color = "blue", linewidth = 0.2)
            
            #noise
            plt.plot(np.full_like(smoothedSignal, noise), "--", color="black", linewidth = 0.3)

            #peak span
            plt.hlines(y=properties["width_heights"], xmin=properties["left_ips"], xmax=properties["right_ips"], color = "C1")
            plt.ylabel('number of events')
            plt.xlabel("timewindow  in"+str(timewindow)+" \u03BCs")
            plt.title(file_current[:-4]+" "+filename)
            plt.savefig(join(path, file_current[:-4]+filename+".png"), dpi=200, orientation='landscape', format ="png", )
            plt.show()
            plt.clf()
            plt.cla()
            print("saved file")


            
            #calculate the variances without gaussian mixture models
            first_widths, second_widths = getWidths(properties["widths"], peaks, firstpeaks, secondpeaks, timewindow)
            spanfirst = np.average(first_widths)
            spanstd_first = np.std(first_widths)
            spansecond = np.average(second_widths)
            spanstd_second = np.std(second_widths)

            heightfirst = np.average(smoothedSignal[firstpeaks])
            heightstd_first = np.std(smoothedSignal[firstpeaks])
            heightsecond = np.average(smoothedSignal[secondpeaks])
            heightstd_second = np.std(smoothedSignal[secondpeaks])


            (firstmeans, firstvars) = getFirstMeansAndVars(gaussModel.means_, gaussModel.covariances_, timewindow)

            (secondmeans, secondvars) = getSecondMeansAndVars(gaussModel.means_, gaussModel.covariances_, timewindow)

            averageFirstVar = np.average(firstvars)
            stdFristVar = np.std(firstvars)

            averageSecondVar = np.average(secondvars)
            stdSecondVar = np.std(secondvars)


            stringToSafe =  "time window:                     "+str(timewindow)       +" microseconds\n"\
                            "total peaks found:               "+str(len(peaks))       +"\n"\
                            "average noise:                   "+str(noise)            +"\n"\
                            "first peaks average span:        "+str(spanfirst)        +" microseconds\n"\
                            "first peaks average span std:    "+str(spanstd_first)    +" microseconds\n"\
                            "second peaks average span:       "+str(spansecond)       +" microseconds\n"\
                            "second peaks average span std:   "+str(spanstd_second)   + " microseconds\n\n"\
                            "first peaks average height:      "+str(heightfirst)      +" events per time window\n"\
                            "first peaks avearage std heigh:  "+str(heightstd_first)  + " events per time window\n"\
                            "second peaks average height:     "+str(heightsecond)     +" events per time window\n"\
                            "second peaks average std height: "+str(heightstd_second) +" events per time window\n\n"\
                            "GAUSSIAN MIXTURE MODEL ESTIMATION \n"\
                            "average first var:               "+str(averageFirstVar)  +" unit is i dont know\n"\
                            "standard deviation first var:    "+str(stdFristVar)      +" \n"\
                            "average second var:              "+str(averageSecondVar) + "\n"\
                            "standard deviation second var:   "+str(stdSecondVar)     +"\n\n"\
                            
            #safe to csv to parentdir
            with open(join(path, file_current[:-4]+filename+".csv"),  mode='w') as safeFile:
                safeFileWriter = csv.writer(safeFile, delimiter=',', dialect='excel', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                safeFileWriter.writerow([str(timewindow), \
                str(len(peaks)), \
                str(noise), \
                str(spanfirst),       \
                str(spanstd_first),   \
                str(spansecond),      \
                str(spanstd_second),  \
                str(heightfirst),     \
                str(heightstd_first), \
                str(heightsecond),    \
                str(heightstd_second)])\

            for (mean, covariance) in zip(gaussModel.means_, gaussModel.covariances_):
                stringToSafe += "mean: " +str(mean)+ " variance: "+ str(covariance) +"\n"

            f= open(join(path, file_current[:-4]+filename+"_stats.txt"),"w+")
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
testpath = 'C:\\Users\\dominik\\OneDrive - Technische Universität Berlin\\Dokumente\\degreeProject\\cameraRecordings\\flashTest2.0\\DVS346NearBox'
startpath = normpath(testpath)
timewindow = int(input("enter timewindow in \u03BCs:"))
savefig(startpath, timewindow, 5)


