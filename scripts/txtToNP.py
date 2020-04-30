import numpy as np
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
            filesize += 1;
            #break
    #fp.close();
    print('filesize was ', filesize)
    nparray = np.zeros((filesize - 2, 8)); #skip first 2 lines

    with open(filename, 'r') as fp:
        #skip first 2 lines
        fp.readline();
        fp.readline();

        line = fp.readline()
        cnt = 0
        while line:
            tmparray = np.zeros((1, 8));

            #take first part
            w1 = line.split(',',1)[0];
            w2 = line.split(' ',1)[0].split(',', 1)[1];
            #take rest of line, note index 0 contains w1&w2
            rest = line.split();
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
                if index==8:
                    #print(w)
                    if int(w) == 0:
                        #print('!1fake')
                        fake = 1
                    continue;
                else:
                    tmparray[0][index] = w.replace(',','.') #slow
                    index+=1;

            if fake != 1:
                #print(tmparray)
                nparray[cnt] =  tmparray
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
    print('saving as ', newname)
    np.save(newname, nparray)
    print('saved')

#for current dir
#startpath = getcwd()
#
#testpath = "C:\\Users\\dominik\\OneDrive\\Dokumente\\TU\\KTH\\Module\\P3\\degreeProject\\cameraRecordings\\noiseTest\\noiseTest\\dvsExplorer"
testpath = "H:\\evs\\last\\localPlanes-2020-04-29T17-26-04+0200.txt"
#testpath = "H:\\evs\\last\\test.txt"
filename = 'insertname'
#set filepath and name
transformtxt(testpath, filename)