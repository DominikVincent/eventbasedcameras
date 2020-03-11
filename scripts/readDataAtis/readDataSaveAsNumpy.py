import matlab.engine
import numpy as np
from os import listdir, getcwd, system
from os.path import isfile, join, isdir, normpath
#for this to work the matlab with the correct script has to be opened
#you also need to execute the following in matlab console: matlab.engine.shareEngine

"""
@param engine is the matlab engine
@param path is the path were files are supposed to be transformed
@param filename the filename of the file to be transformed
@param maxdepth is the maxdepth of the transformation
"""
def transformInAllSubDirs(engine, path, filename, maxdepth = 3):
    if maxdepth == 0:
        return
    else:
        maxdepth -=1
    print("in: ", path)
    #get files in dir
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    rt = 1
    if filename not in onlyfiles and ("log.raw") in onlyfiles:
        rawToConvert = join(path, "log.raw")
        print(rawToConvert)
        #returns 0 if works
        rt = system('C:\\"Program Files"\\Prophesee\\PropheseePlayer\\prophesee_raw_to_dat.exe -i '+rawToConvert+' --cd')
        print("system returned: ",rt)
        converted = True
    if filename in onlyfiles or rt == 0:
        print("calling matlab")
        matlabarray = engine.load_atis_data(join(path, filename))
        print("got result from matlab")
        
        print("transforming to numpy array")
        
        nparrayonedim = np.asarray(matlabarray._data, dtype=np.int32)

        print("got the numpy array")

        print("now transforming to correct dimenstion")
        print("current dimension is ", nparrayonedim.shape, "the desired dimension is", nparrayonedim.shape[0]/4, ", ", 4)
        nparrayonedim = nparrayonedim.reshape(4, int(nparrayonedim.shape[0]/4)).T
        print("done")

        print("saving array now")
        np.save(join(path, filename), nparrayonedim)
    
    #call for all subdirs
    subdirs = [join(path, o) for o in listdir(path) if isdir(join(path,o))] 
    print("subdirs are: ", subdirs)
    for x in subdirs:
        print("x: ", x)
        transformInAllSubDirs(engine, x, filename, maxdepth)


matlabengines = matlab.engine.find_matlab()

#print("the found matlab engines are: ", matlabengines)
if len(matlabengines) >=1:
    print("connecting to: ", matlabengines[0])
    engine = matlab.engine.connect_matlab(matlabengines[0])



filename = "log_td.dat"

#for current dir
#startpath = getcwd()
#
testpath = "C:\\Users\\dominik\\OneDrive\\Dokumente\\TU\\KTH\\Module\\P3\\degreeProject\\cameraRecordings\\flashTest2.0\\propheseeFarBox"
startpath = normpath(testpath)
transformInAllSubDirs(engine, startpath, filename, 2)


