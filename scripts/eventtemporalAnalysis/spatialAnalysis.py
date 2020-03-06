from dv import AedatFile
import matplotlib.pyplot as plt

with AedatFile(<Path to aedat file>) as f:
    # list all the names of streams in the file
    print(f.names)
    
    #timewindow in microseconds
    timeWindowMicroseconds = int(intput("please enter the timewindow in microsecnods"))
    print("timewindow is:", timeWindowMicroseconds)

    xyDvision = int(input("enter the number of pieces you want to have in the frame per window: "))
    print("xyDvision: ", xyDvision)

    events = []
    lasttimestamp = None
    count = 0
    # loop through the "events" stream
    for e in f['events']:
        if lasttimestamp == None or (e.timestamp - lasttimestamp):
            lasttimestamp = e.timestamp
            events += count
            count = 0
        else:
            count +=1
        
        print(e.timestamp)
        print("current timw windows", len(events))
    
        
plt.plt(events)
plt.ylabel('number of events')
plt(xlable("timewindow"))
plt.show()

