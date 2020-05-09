import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
import time
def drawimg(events):
    img = np.zeros((480,640))
    k = 0
    for event in events:
        if 30000 < event[2] < 31000:
            k +=1
            img[event[1], event[0]] +=1
    print(k)
    plt.imshow(img)
    plt.show()


"""
takes every xth and yth row

@param[in] events the events in format t,x,y,pol in rows stacked
@param[in] x every xth column to be taken
@param[in] y every yth row to be taken

@param[out] the events matching the rows and colums
"""
def everyIRow(events, x, y):
    events_rows = np.where( (events[:,0] % x == 0) & (events[:,1] % y == 0))
    events = events[events_rows]
    events[:,0] = events[:,0]/x
    events[:,1] = events[:,1]/y
    return events

"""
takes a ysize x xsize x 2 gt matrix and downscales it by scale
"""
def downscaleOF(events, x_scale, y_scale):
    events_dsample = events[::y_scale, ::x_scale, :]

    events_dsample[:,:,0] = events_dsample[:,:,0]/x_scale
    events_dsample[:,:,1] = events_dsample[:,:,1]/y_scale
    return events_dsample

"""
downscales by x and y without disarding anything

@param[in] events the events in format t,x,y,pol in rows stacked
@param[in] x downscaling in x
@param[in] y downscaling in y
@param[out] the events downscaled
"""
def everyEvent(events, x, y):
    events[:, 0] = events[:, 0]/x
    events[:, 1] = events[:, 1]/y
    return events.astype(np.int32)




    


"""
returns a downscaled image by factor x_scale, y_scale. Events are taken if num_of_pixels of their neighbours are active during 
the time window

@param[in] events the events in format t,x,y,pol in rows stacked
@param[in] x_res 
@param[in] y_res 
@param[in] x_scale downscaling in x
@param[in] y_scale downscaling in y
@param[in] time_window time in us or ns of the timewindow depending on the unit in the events array
@param[in] number of neighbours number of neighbouring pixels that have to be active
@param[out] the events downscaled
"""
def downscaleTimeWindow(events, x_res, y_res, x_scale, y_scale, time_window, num_of_pixel=2):
    
    newEvents = np.zeros_like(events)
    count_new = 0
    
    queue = []

    # Y x X x 2, last one determines whether off = 0 or on event = 1 
    active_events = np.zeros((y_res, x_res, 2))
    #active_events_pointers = np.zeros((int(y_res/y_scale), int(x_res/x_scale), 2))

    #start of queue
    queue_start = 0
    
    for j in tqdm(range(0, events.shape[0])):
        x, y, ts, p = events[j]
        
        # set element as active in matrix
        active_events[y, x, p] = 1
        #queue.append(events[j])
        # active_events_pointers[y,x,p] = j

        # remove old events from "queue"
        while queue_start <= j and events[queue_start][2] < (ts - time_window):
            remove_event = events[queue_start]
            queue_start += 1
            active_events[remove_event[1], remove_event[0], remove_event[3]] = 0

        # while not not queue and queue[0][2] < (ts - time_window):
        #     remove_event = queue.pop(0)
        #     queue_start += 1
        #     active_events[remove_event[1], remove_event[0], remove_event[3]] = 0

        # print("queue size: ", j-queue_start)
        # print("active events:", active_events.sum())

        # get the neighbours of the same kid which are active currently
        count_neighbours = numOfOnNeighbours(y, x, active_events[:,:,p])
            
        if count_neighbours >= num_of_pixel:
            active_events[y, x, p] = 0
            newEvents[count_new] = [x/x_scale,y/y_scale,ts, p]
            
            count_new += 1
            

        else:
            for k in [-1,0,1]:
                for h in [-1, 0, 1]:
                    if x + h < 0 or x+h >= x_res:
                        continue
                    if y + k < 0 or y+k >= y_res:
                        continue

                    if active_events[y+k, x+h, p] == 1:
                        count_neighbours = numOfOnNeighbours(y+k, x+h, active_events[:,:,p])
                        if count_neighbours >= num_of_pixel:
                            active_events[y+k, x+h, p] = 0

                            newEvents[count_new] = [(x+h)/x_scale,(y+k)/y_scale, ts, p]
                            count_new +=1


       
    #print(newEvents[:count_new,:])
    final = np.array((count_new,4))
    final = newEvents[:count_new,:]

    final.view('i4,i4,i4,i4').sort(order=['f2'], axis=0)
    return final.astype(np.int32)
   
            
def neighbours(e1, e2):
    return np.abs(e1[0] - e2[0]) <= 1 and np.abs(e1[1] - e2[1]) <= 1

"""
returns the number of pixels turned on in a 3x3 neighbourhood

@param[in] bitimage - the image saying if a pixel is active or not
"""
def numOfOnNeighbours(y, x, bitimage):
    y_low = max(0, y-1)
    y_max = min(bitimage.shape[0], y+2)

    x_low = max(0, x-1)
    x_max = min(bitimage.shape[0], x+2)

    return np.sum(bitimage[y_low:y_max, x_low:x_max])



def downsampledInAllSubdirs(startpath, fileending, x_scale, y_scale, time_window = 20, num_of_pixels = 3):
    for root, dirs, files in os.walk(startpath, topdown=False):
        for file in files:
            if file.endswith(fileending) and file[:6]=="events" and not "down" in file:
                print(file)
                events = np.load(os.path.join(root, file), allow_pickle = True)
                np.save(os.path.join(root, file), events, fix_imports=True)

                sample_type = "all"
                newEvents = everyEvent(events, x_scale,y_scale)
                np.save(os.path.join(root, file[:-4]+"_down_"+sample_type+".npy"), newEvents, fix_imports=True)
                
                sample_type = "every_i"
                events = np.load(os.path.join(root, file), allow_pickle = True)
                newEvents = everyIRow(events, x_scale,y_scale)
                np.save(os.path.join(root, file[:-4]+"_down_"+sample_type+".npy"), newEvents)

                sample_type = "complex"
                newEvents = downscaleTimeWindow(events, 640, 480, x_scale, y_scale, time_window, num_of_pixels)
                np.save(os.path.join(root, file[:-4]+"_down_"+sample_type+".npy"), newEvents)

            elif file == "vxGT.npy" or file == "vyGT.npy":
                vxGT = np.load(os.path.join(root, "vxGT.npy"), allow_pickle = True)
                vyGT = np.load(os.path.join(root, "vyGT.npy"), allow_pickle = True)
                vGT = np.stack((vxGT, vyGT), axis=2)
                np.save(os.path.join(root, "vGT.npy"), vGT)

                downGT = downscaleOF(vGT, x_scale, y_scale)
                np.save(os.path.join(root, "vGT_down.npy"), downGT)

# eventsArray = np.load("downsampling/test.npy", allow_pickle=True)
# print(eventsArray.shape)
# #drawimg(eventsArray)
# #newEvents = downscaleTimeWindow(eventsArray, 640, 480, 4, 4, 100, 3)
# newEvents = everyEvent(eventsArray, 2, 2)

# print(newEvents.shape)
# print(np.max(newEvents, axis=0))


# np.save("downsampling/downsampled.npy", newEvents)
path = "C:\\Users\dominik\OneDrive - Technische Universität Berlin\Dokumente\degreeProject\cameraRecordings\OFRecording\\rotatingBar\\tmp"
#sample_type = "every_i" # "ever_i" "complex" "all"
x_scale = 2
y_scale = 2

downsampledInAllSubdirs(path, ".npy", x_scale,y_scale)