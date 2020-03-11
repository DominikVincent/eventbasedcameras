import matplotlib.pyplot as plt
import numpy as np
from os import listdir, getcwd, system
from os.path import isfile, join, isdir, normpath

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
            
            
            #countevents[ countevents==0 ] = np.nan
            print("plotting")
            plt.plot(countevents, linewidth = 1)
            plt.ylabel('number of events in'+str(timewindow))
            plt.xlabel("timewindow")
            plt.savefig(join(path, file_current[:-4]+"_figure.png"), orientation='landscape', format ="png", )
            plt.clf()
            plt.cla()
            print("saved file")
        
    #call for all subdirs
    subdirs = [join(path, o) for o in listdir(path) if isdir(join(path,o))] 
    print("subdirs are: ", subdirs)
    for x in subdirs:
        print("x: ", x)
        savefig(x, timewindow, maxdepth)




#for current dir
#startpath = getcwd()
#
testpath = "C:\\Users\\dominik\\OneDrive\\Dokumente\\TU\\KTH\\Module\\P3\\degreeProject\\cameraRecordings"
startpath = normpath(testpath)
timewindow = int(input("enter timewindow in \u03BCs:"))
savefig(startpath, timewindow, 5)


