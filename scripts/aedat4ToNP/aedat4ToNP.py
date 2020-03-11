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
            # events will be a named numpy array
            events = np.hstack([packet for packet in f[name].numpy()])
            
            # Access information of all events by type
            x, y, timestamps, polarities = events['x'], events['y'], events['timestamp'],  events['polarity']
            print(events.shape)
            print(events[0:3])
            returnArrays.append((name, events))
    return returnArrays
            
        

"""

@param path is the path were files are supposed to be transformed
@param filename the filename of the file to be transformed
@param maxdepth is the maxdepth of the transformation
"""
def transformInAllSubDirs(path, maxdepth = 3):
    if maxdepth == 0:
        return
    else:
        maxdepth -=1
    print("in: ", path)
    #get files in dir
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    rt = 1
    
    for file_current in onlyfiles:
        if file_current[-6:] == "aedat4":
            print("calling dv tranform")
            nparrays = transformaedat4(join(path,file_current))
            print("got result from numpy transform")
            
            for res in nparrays:
                print("converting first stream to npint_32 to reduce storage size")
                #normalize the timestamps
                res[1][:,2] -= res[1][2]
                nparray = res[1].astype(np.int32)
                print("saving the array")
                nameappendix = res[0]
                if nameappendix == "events_1":
                    print("name is events_1, assuming events_1 is denoised and changing name")
                    nameappendix = "denoisedEvents"
                np.save(join(path, file_current+nameappendix), nparray)

        
        #call for all subdirs
        subdirs = [join(path, o) for o in listdir(path) if isdir(join(path,o))] 
        print("subdirs are: ", subdirs)
        for x in subdirs:
            print("x: ", x)
            transformInAllSubDirs(x, maxdepth)




#for current dir
#startpath = getcwd()
#
testpath = "C:\\Users\\dominik\\OneDrive\\Dokumente\\TU\\KTH\\Module\\P3\\degreeProject\\cameraRecordings\\noiseTest\\noiseTest\\dvsExplorer"
startpath = normpath(testpath)
transformInAllSubDirs(startpath, 2)


