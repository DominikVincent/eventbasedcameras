# -*- coding: utf-8 -*-
"""
This module contains classes, functions and an example (main) for handling AER vision data.
"""
import glob
#import cv2
import numpy as np
import matplotlib.pyplot as plt
#from win32api import GetSystemMetrics
#import timer
import os

class Events(object):
    """
    Temporal Difference events.
    data: a NumPy Record Array with the following named fields
        x: pixel x coordinate, unsigned 16bit int
        y: pixel y coordinate, unsigned 16bit int
        p: polarity value, boolean. False=off, True=on
        ts: timestamp in microseconds, unsigned 64bit int
    width: The width of the frame. Default = 304.
    height: The height of the frame. Default = 240.
    """
    def __init__(self, num_events, width=304, height=240):
        """num_spikes: number of events this instance will initially contain"""
        self.data = np.rec.array(None, dtype=[('x', np.uint16), ('y', np.uint16), ('p', np.bool_), ('ts', np.uint64)], shape=(num_events))
        self.width = width
        self.height = height

    def sort_order(self):
        """Generate data sorted by ascending ts
        Does not modify instance data
        Will look through the struct events, and sort all events by the field 'ts'.
        In other words, it will ensure events_out.ts is monotonically increasing,
        which is useful when combining events from multiple recordings.
        """
        #chose mergesort because it is a stable sort, at the expense of more
        #memory usage
        events_out = np.sort(self.data, order='ts', kind='mergesort')
        return events_out

    def extract_roi(self, top_left, size, is_normalize=False):
        """Extract Region of Interest
        Does not modify instance data
        Generates a set of td_events which fall into a rectangular region of interest with
        top left corner at 'top_left' and size 'size'
        top_left: [x: int, y: int]
        size: [width, height]
        is_normalize: bool. If True, x and y values will be normalized to the cropped region
        """
        min_x = top_left[0]
        min_y = top_left[1]
        max_x = size[0] + min_x
        max_y = size[1] + min_y
        extracted_data = self.data[(self.data.x >= min_x) & (self.data.x < max_x) & (self.data.y >= min_y) & (self.data.y < max_y)]

        if is_normalize:
            self.width = size[0]
            self.height = size[1]
            extracted_data = np.copy(extracted_data)
            extracted_data = extracted_data.view(np.recarray)
            extracted_data.x -= min_x
            extracted_data.y -= min_y

        return extracted_data

    def apply_refraction(self, us_time):
        """Implements a refractory period for each pixel.
        Does not modify instance data
        In other words, if an event occurs within 'us_time' microseconds of
        a previous event at the same pixel, then the second event is removed
        us_time: time in microseconds
        """
        t0 = np.ones((self.width, self.height)) - us_time - 1
        valid_indices = np.ones(len(self.data), np.bool_)

        #with timer.Timer() as ref_timer:
        i = 0
        for datum in np.nditer(self.data):
            datum_ts = datum['ts'].item(0)
            datum_x = datum['x'].item(0)
            datum_y = datum['y'].item(0)
            if datum_ts - t0[datum_x, datum_y] < us_time:
                valid_indices[i] = 0
            else:
                t0[datum_x, datum_y] = datum_ts

            i += 1
        #print('Refraction took %s seconds' % ref_timer.secs

        return self.data[valid_indices.astype('bool')]

    def write_j_aerOld(self, filename, downsampled):
        """
        writes the td events in 'td_events' to a file specified by 'filename'
        which is compatible with the jAER framework.
        To view these events in jAER, make sure to select the DAVIS640 sensor.
        """
        import time
        # if downsampled:
        #     y = 239 - self.data.y
        # else:
        #     y = 479 - self.data.y
        y = self.data.y
        #y = td_events.y
        y_shift = 22 + 32
        
        if downsampled:
            x = 319 - self.data.x
        else:
            x = 639 - self.data.x
        
        #x = self.data.x
        x_shift = 12 + 32

        p = self.data.p 
        p_shift = 11 + 32

        ts_shift = 0

        y_final = y.astype(dtype=np.uint64) << y_shift
        x_final = x.astype(dtype=np.uint64) << x_shift
        p_final = p.astype(dtype=np.uint64) << p_shift
        ts_final = self.data.ts.astype(dtype=np.uint64) << ts_shift
        vector_all = np.array(y_final + x_final + p_final + ts_final, dtype=np.uint64)
        aedat_file = open(filename, 'wb')

        version = '2.0'
        aedat_file.write('#!AER-DAT' + version + '\r\n')
        aedat_file.write('# This is a raw AE data file - do not edit\r\n')
        aedat_file.write \
            ('# Data format is int32 address, int32 timestamp (8 bytes total), repeated for each event\r\n')
        aedat_file.write('# Timestamps tick is 1 us\r\n')
        aedat_file.write('# created ' + time.strftime("%d/%m/%Y") \
            + ' ' + time.strftime("%H:%M:%S") \
            + ' by the Python function "write2jAER"\r\n')
        aedat_file.write \
            ('# This function fakes the format of DAVIS640 to allow for the full ATIS address space to be used (304x240)\r\n')
        ##aedat_file.write(vector_all.astype(dtype='>u8').tostring())
        to_write = bytearray(vector_all[::-1])
        to_write.reverse()
        aedat_file.write(to_write)
        #aedat_file.write(vector_all)
        #vector_all.tofile(aedat_file)
        aedat_file.close()

    def write_j_aer(self, filename):
        """
        writes the td events in 'td_events' to a file specified by 'filename'
        which is compatible with the jAER framework.
        To view these events in jAER, make sure to select the DAVIS640 sensor.
        """
        import time
        y = 479 - self.data.y
        #y = self.data.y

        #y = td_events.y
        y_shift = 22 + 32

        x = 639 - self.data.x
        #x = self.data.x 
        #print(x[x==-1])
        #x = td_events.x
        x_shift = 12 + 32

        p = self.data.p 
        p_shift = 11 + 32

        ts_shift = 0

        y_final = y.astype(dtype=np.uint64) << y_shift
        x_final = x.astype(dtype=np.uint64) << x_shift
        p_final = p.astype(dtype=np.uint64) << p_shift
        ts_final = self.data.ts.astype(dtype=np.uint64) << ts_shift
        vector_all = np.array(y_final + x_final + p_final + ts_final, dtype=np.uint64)
        aedat_file = open(filename, 'w')
        print(vector_all.shape)
        version = '2.0'
        aedat_file.write('#!AER-DAT' + version + '\r\n')
        aedat_file.write('# This is a raw AE data file - do not edit\r\n')
        aedat_file.write \
            ('# Data format is int32 address, int32 timestamp (8 bytes total), repeated for each event\r\n')
        aedat_file.write('# Timestamps tick is 1 us\r\n')
        aedat_file.write('# created ' + time.strftime("%d/%m/%Y") \
            + ' ' + time.strftime("%H:%M:%S") \
            + ' by the Python function "write2jAER"\r\n')
        aedat_file.write \
            ('# This function fakes the format of DAVIS640 to allow for the full ATIS address space to be used (304x240)\r\n')
        ##aedat_file.write(vector_all.astype(dtype='>u8').tostring())
        aedat_file.close()
        aedat_file = open(filename, 'ab')
        print(hex(vector_all[0]))
        to_write = bytearray(vector_all[::-1])
        print(vector_all[:10])
        print()
        
        to_write.reverse()
        aedat_file.write(to_write)
        #aedat_file.write(vector_all)
        #vector_all.tofile(aedat_file)
        aedat_file.close()

    

    def loadNParray(self, array):
        self.data.x = array[:, 0]
        self.data.y = array[:, 1]
        self.data.ts = array[:, 2]
        self.data.p = array[:, 3]

def transform_all_subdirs(startpath):
    for root, dirs, files in os.walk(startpath, topdown=False):
            for file in files:
                if file.endswith(".npy") and "events" in file:
                    events = np.load(os.path.join(root, file), allow_pickle = True)
                    downsampled = "down" in file
                    if downsampled:
                        eventObj = Events(events.shape[0], 320, 240)
                    else:
                        eventObj = Events(events.shape[0], 640, 480)
                    eventObj.loadNParray(events)
                    eventObj.write_j_aerOld(os.path.join(root, file[:-4]+"_"+str(events.shape[0])+".aedat"), downsampled)


def drawing(events, start, window = 1000):
    img = np.zeros((480,640))
    k = 0
    for event in events:
        if start < event[2] < start + window:
            k +=1
            img[event[1], event[0]] +=1
    print(k)

    plt.pcolormesh(img)
    plt.show()

#arr = np.load("NPtoAedat/downsampled.npy", allow_pickle=True)

#drawing(arr, 30000)

# print(arr[:10])
# arr[arr[:,3] == -1, 3] = 0
# arr[arr[:,3] == 1, 3] = 2
# print(arr[:10])


# # arr = arr[:1]
# #print(arr[:10])
# print(arr.shape)
# eventClass = Events(arr.shape[0], 640, 480)

# eventClass.loadNParray(arr)
# eventClass.write_j_aer("test3New.aedat")
# eventClass.write_j_aerOld("test3Old.aedat")
# print("events:" ,arr.shape[0], " EPS: ", 1.0*arr.shape[0]/arr[-1,2])
# print("length: ", 1.0*arr[-1,2]-arr[0,2])
# print("start: ", arr[0,2], " last: ", arr[-10:,2])

path = "C:\Users\dominik\OneDrive - Technische Universität Berlin\Dokumente\degreeProject\cameraRecordings\OFRecording\\rotatingBar"
# path = os.path.normpath(path)
path = unicode(path, 'utf-8')
transform_all_subdirs(path)