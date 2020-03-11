import numpy as np
from os import listdir, getcwd, system
from os.path import isfile, join, isdir, normpath
from dv import AedatFile

"""
@param filename name/path to the file
@return a array of tupels, which contain the name of the stream in the file and the np array of events
"""
def transformaedat4(filename):

    with AedatFile(filename) as f:
        names = f.names
        print("the following streams are availible in the file", names)
        print("taking all")
        returnArrays = []

        
        for name in names:
            events = []
            print("now takeing: ", name)
            for e in f[name]:
                events.append([e.x, e.y, e.timestamp, e.polarity])


            rtarr = np.asarray(events)
            print(rtarr[0:3])
            print(rtarr.shape)

            returnArrays.append((name, rtarr))
    return returnArrays
            
        

"""

@param path is the path were files are supposed to be transformed
@param filename the filename of the file to be transformed
@param maxdepth is the maxdepth of the transformation
"""
def transformInAllSubDirs(path, maxdepth = 5):
    if maxdepth == 0:
        return
    else:
        maxdepth -=1
    print("in: ", path)
    #get files in dir
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    
    print(len(onlyfiles), " number of files in this folder.")
    for file_current in onlyfiles:
        if file_current[-6:] == "aedat4":
            print("calling dv tranform for ", file_current)
            nparrays = transformaedat4(join(path,file_current))
            print("got result from numpy transform")
            
            for res in nparrays:
                print("converting first stream to npint_32 to reduce storage size")
                #normalize the timestamps
                res[1][:,2] -= res[1][0,2]
                nparray = res[1].astype(np.int32)
                print("saving the array")
                nameappendix = res[0]
                if nameappendix == "events_1":
                    print("name is events_1, assuming events_1 is denoised and changing name")
                    nameappendix = "denoisedEvents"
                np.save(join(path, file_current[:-7]+nameappendix), nparray)

        
    #call for all subdirs

    print("in: ", path)

    subdirs = [join(path, o) for o in listdir(path) if isdir(join(path,o))] 
    print("subdirs are: ", subdirs)
    for x in subdirs:
        print("x: ", x)
        transformInAllSubDirs(x, maxdepth)




#for current dir
#startpath = getcwd()
#
testpath = "C:\\Users\\dominik\\OneDrive\\Dokumente\\TU\\KTH\\Module\\P3\\degreeProject\\cameraRecordings"
startpath = normpath(testpath)
transformInAllSubDirs(startpath, 5)


