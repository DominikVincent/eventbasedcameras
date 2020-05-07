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
@param[in] time_window time in ns of the timewindow
@param[in] number of neighbours number of neighbouring pixels that have to be active
@param[out] the events downscaled
"""
def downscaleTimeWindow(events, x_res, y_res, x_scale, y_scale, time_window, num_of_pixel=3):
    queue = [events[0]]
    newEvents = np.zeros_like(events)
    k = 0
    for j in tqdm(range(1, events.shape[0])):
        #print(j)
        event = events[j]
        #print(len(queue))
        
        queue.append(event)
        while not queue and queue[0][2] < (event[2] - time_window):
            #print("bitte was")
            queue.pop()
        #print(len(queue))
        toDelete = []
        neighboursC = []
        count = 0
        for q in queue:
            if neighbours(q, queue[-1]):
                count +=1
                neighboursC.append(q)
            
        # if count > num_of_pixel:
        #     newEvents[k] = queue[-1]
        #     newEvents[k][0] = newEvents[k][0]/x_scale
        #     newEvents[k][1] = newEvents[k][1]/y_scale
        #     k += 1
        #     queue.pop(-1)

        # for i in range(len(neighboursC)):
        #     count = 0
        #     for e in range(len(queue)):
        #         if neighbours(queue[e], queue[i]):
        #             count +=1
        #     if count > num_of_pixel:
        #         newEvents[k] = queue[i]
        #         newEvents[k][0] = newEvents[k][0]/x_scale
        #         newEvents[k][1] = newEvents[k][1]/y_scale
        #         k += 1
        #         toDelete.append(queue[i])
        # for f in toDelete:
        #     queue.remove(f)
       
    final = np.array((k,4))
    final = newEvents[:k,:]

    final.view('i4,i4,i4,i4').sort(order=['f2'], axis=0)
    return final


"""
returns a downscaled image by factor x_scale, y_scale. Events are taken if num_of_pixels of their neighbours are active during 
the time window

@param[in] events the events in format t,x,y,pol in rows stacked
@param[in] x_res 
@param[in] y_res 
@param[in] x_scale downscaling in x
@param[in] y_scale downscaling in y
@param[in] time_window time in ns of the timewindow
@param[in] number of neighbours number of neighbouring pixels that have to be active
@param[out] the events downscaled
"""
"""
def downscaleTimeWindow(events, x_res, y_res, x_scale, y_scale, time_window, num_of_pixel=3):
    queue = events[0][np.newaxis]
    print(queue)
    print(queue.shape)
    newEvents = np.zeros_like(events)
    k = 0
    for j in tqdm(range(1, events.shape[0])):
        #print(j)
        event = events[j]
        #print(queue.shape)
        queue = np.vstack((queue, event))
        while queue.shape[0] != 0 and queue[0][2] < (event[2] - time_window):
            #print("bitte was")
            queue = np.delete(queue, 0, axis=0)
        #print(len(queue))
        if queue.shape[0] != 0:
            pass
            #queue = np.vstack((queue, event))
        else:
            queue = event
        toDelete = []
        # for i in range(queue.shape[0]):
        #     count = 0
        #     for e in range(queue.shape[0]):
        #         if neighbours(queue[e], queue[i]):
        #             count +=1
        #     if count > num_of_pixel:
        #         newEvents[k] = queue[i]
        #         newEvents[k][0] = newEvents[k][0]/x_scale
        #         newEvents[k][1] = newEvents[k][1]/y_scale
        #         k += 1
        #         toDelete.append(i)
        queue = np.delete(queue, toDelete,  axis=0)
       
    final = np.array((k,4))
    final = newEvents[:k,:]

    final.view('i4,i4,i4,i4').sort(order=['f2'], axis=0)
    return final
"""            
            
def neighbours(e1, e2):
    return np.abs(e1[0] - e2[0]) <= 1 and np.abs(e1[1] - e2[1]) <= 1
"""
returns a downscaled image by factor x_scale, y_scale. Events are taken if num_of_pixels of their neighbours are active during 
the time window

@param[in] events the events in format t,x,y,pol in rows stacked
@param[in] x_res 
@param[in] y_res 
@param[in] x_scale downscaling in x
@param[in] y_scale downscaling in y
@param[in] time_window time in ns of the timewindow
@param[in] number of neighbours number of neighbouring pixels that have to be active
@param[out] the events downscaled
"""
# def downscaleTimeWindow(events, x_res, y_res, x_scale, y_scale, time_window, num_of_pixel=3):
#     img_on = np.zeros((y_res, x_res))
#     img_off = np.zeros((y_res, x_res))

    

#     new_events = np.zeros_like(events)
#     k = 0
#     for x,y,time, p in tqdm(events):
        
#         if p == 1:
#             img_on[y,x] = time
#         else:
#             img_off[y,x] = time
        
#         on_pixels  = np.where(img_on  > max(time - time_window,0))
#         off_pixels = np.where(img_off > max(time - time_window,0))

#         active_on = np.zeros((y_res, x_res), dtype=np.bool)
#         active_off = np.zeros((y_res, x_res), dtype=np.bool)

#         active_on[on_pixels] = 1
#         active_off[off_pixels] = 1

#         #print("active",on_pixels[0].shape[0]+off_pixels[0].shape[0])
#         for on_pixel in zip(on_pixels[0],on_pixels[1]):
            
#             if numOfOnNeighbours(on_pixel[0], on_pixel[1], active_on) > num_of_pixel:
#                 event = np.array([x/x_scale, y/y_scale, time, 1])
#                 new_events[k] = event
#                 img_on[on_pixel[0], on_pixel[1]] = 0

#         for off_pixel in zip(off_pixels[0],off_pixels[1]):
#             if numOfOnNeighbours(off_pixel[0], off_pixel[1], active_off) > num_of_pixel:
#                 event = np.array([x/x_scale, y/y_scale, time, -1])
#                 new_events[k] = event
#                 img_off[off_pixel[0], off_pixel[1]] = 0

    
#     final = np.array((k,4))
#     final = new_events[:k,:]

#     final.view('i4,i4,i4,i4').sort(order=['f2'], axis=0)
#     return final

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



def downsampledInAllSubdirs(startpath, fileending, sample_type, x_scale, y_scale, time_window = 20, num_of_pixels = 3):
    for root, dirs, files in os.walk(startpath, topdown=False):
        for file in files:
            if file.endswith(fileending) and file=="events.npy":
                events = np.load(os.path.join(root, file), allow_pickle = True)
                np.save(os.path.join(root, file), events, fix_imports=True)

                sample_type = "all"
                newEvents = everyEvent(events, x_scale,y_scale)
                np.save(os.path.join(root, file[:-4]+"_down_"+sample_type+".npy"), newEvents, fix_imports=True)
                
                sample_type = "every_i"
                events = np.load(os.path.join(root, file), allow_pickle = True)
                newEvents = everyIRow(events, x_scale,y_scale)
                np.save(os.path.join(root, file[:-4]+"_down_"+sample_type+".npy"), newEvents)

                # sample_type == "complex"
                # newEvents = downscaleTimeWindow(events, 640, 480, x_scale, y_scale, time_window, num_of_pixels)
                # np.save(os.path.join(root, file[:-4]+"_down_"+sample_type+".npy"), newEvents)

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
path = "C:\\Users\dominik\OneDrive - Technische Universität Berlin\Dokumente\degreeProject\cameraRecordings\OFRecording\\translatingSquare\\test"
sample_type = "every_i" # "ever_i" "complex" "all"
x_scale = 2
y_scale = 2

downsampledInAllSubdirs(path, ".npy", sample_type, x_scale,y_scale)