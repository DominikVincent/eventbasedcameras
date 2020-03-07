from dv import AedatFile
import matplotlib.pyplot as plt
import numpy as np

with AedatFile("/home/dominik/dvSave-2020_03_06_14_51_35.aedat4") as f:
    # list all the names of streams in the file
    print(f.names)
    
    #timewindow in microseconds
    timeWindowMicroseconds = int(input("please enter the timewindow in microsecnods"))
    print("timewindow is:", timeWindowMicroseconds)

    events = []
    lasttimestamp = None
    count = 0
    # loop through the "events" stream
    for e in f['events']:
        if lasttimestamp == None or (e.timestamp - lasttimestamp) >timeWindowMicroseconds:
            # print("in if")
            lasttimestamp = e.timestamp
            events.append(count)
            count = 0
        else:
            count +=1
        
        # print(e.timestamp)
        # print("current timw windows", len(events))
    
npevents = np.array(events)
np.savetxt('test1.txt', npevents, fmt='%d')
   
plt.plot(events)
plt.ylabel('number of events')
plt.xlabel("timewindow")
plt.show()

