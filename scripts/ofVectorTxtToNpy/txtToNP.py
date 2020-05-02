import numpy as np
import os
from os import listdir, getcwd, system
from os.path import isfile, join, isdir, normpath
from dv import AedatFile

"""
@param filename name/path to the file
"""
def transformtxt(filename, newname):
    #a = np.zeros((camWidth, camHeight))
    #nparray = np.zeros((8, 0));

    #count file length, slow
    filesize = 0
    with open(filename, 'r') as f:

        for line in f:
            filesize += 1
            #break
    #fp.close();
    print('filesize was ', filesize)
    nparray = np.zeros((filesize - 2, 9)); #skip first 2 lines

    with open(filename, 'r') as fp:
        #skip first 2 lines
        fp.readline()
        fp.readline()

        line = fp.readline()
        cnt = 0
        while line:
            tmparray = np.zeros((1, 9))

            #take first part
            w1 = line.split(',',1)[0]
            w2 = line.split(' ',1)[0].split(',', 1)[1]
            #take rest of line, note index 0 contains w1&w2
            rest = line.split()
            #print(w1)
            #print(w2)
            #print(rest)
            tmparray[0,0] = w1
            tmparray[0,1] = w2
            index = 2
            fake = 0
            for w in rest[1:]:
                #print(w)
                #print(index)
                # if index==8:
                #     #print(w)
                #     if int(w) == 0:
                #         #print('!1fake')
                #         fake = 1
                #     continue
            
                tmparray[0][index] = w.replace(',','.') #slow
                index+=1

            
            #print(tmparray)
            nparray[cnt] = tmparray
            line = fp.readline() #go next
            cnt += 1

            #break
            # events will be a named numpy array
            #events = np.hstack([packet for packet in f[name].numpy()])

            # Access information of all events by type
            #x, y, timestamps, polarities = events['x'], events['y'], events['timestamp'],  events['polarity']
            #print(events.shape)
            #print(events[0:3])
            #returnArrays.append((name, events))
    #return returnArrays
    #saving
    zero_flow_vec = nparray[nparray[:,7] == 0].shape[0]
    nparray = nparray[nparray[:,8] == 1][:,:8]
    
    print('saving as ', newname)
    np.save(newname[:-4]+ "zeroVec_"+str(zero_flow_vec)+".npy", nparray)
    print('saved')



def transformAllSubdirs(startpath):
    for root, dirs, files in os.walk(startpath, topdown=False):
        for file in files:
            if file.endswith(".txt") and "ofvec" in file:
                transformtxt(os.path.join(root, file), os.path.join(root, file[:-4] + ".npy"))
#for current dir
#startpath = getcwd()
#
path = "C:\\Users\dominik\Documents\KTH\P3\degreeProject\eventbasedcameras\cameraRecordings\dropTest\DVS640\mousepad"
transformAllSubdirs(path)