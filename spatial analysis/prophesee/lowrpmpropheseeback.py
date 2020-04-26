import matplotlib.pyplot as plt
import numpy as np
import math
from os import listdir, getcwd, system
from os.path import isfile, join, isdir, normpath



#draw box

testPath = "H:\\evs\\fixedSpinningWheel\\prophesee\\10rpm\\log.npy"

timewindow = 1;
startTime = 0;
startIndex = 0;
endTime = 0;
endIndex = 0;

print("load np array dv tranform")
nparray = np.load(testPath, allow_pickle=True)
print("loaded array", nparray.shape)



# find the action. Only run this once
v = ((1+nparray[-1][2])/timewindow)
print("length",v)
countevents = np.zeros(int(np.ceil(v)))
i = 0
for e in np.nditer(nparray[:,2]):
    break; #to make testing fast! Remove later
    countevents[int(e/timewindow)] += 1
    #10 event limit to detect start CHANGE for cameras
    if (countevents[int(e/timewindow)] > 10):
        if (startTime == 0):
            startTime = nparray[i][2];
            startIndex = i;
        else:
            endTime = nparray[i][2];
            endIndex = i;
    i = i + 1;
print(startTime)
print(startIndex)
print(endTime)
print(endIndex)

# radius in pixels, relative time in microseconds
# base angle should be 1cm off math simple, have that as baseline
def spinnerPosition(radius, time, rpm, startAngle):
    #Angle
    relativeTime = np.mod(time,  lapTime)
    angle = -( 2 * np.pi * relativeTime / lapTime);
    #add corrective angle to set startagnle
    angle += startAngle;
    #x and y coordinates, based on angle radius + relative to center
    x = radius * np.cos(angle) + camWidth /2 + xOffset
    # minus or plus for some?

    y =  (radius * np.sin(angle) + camHeight /2) + yOffset
    #return np.array([x,y]);
    return np.array([y,x]); #inverted



#margins
marginsmall = 3 # in pixels
marginlarge = 15 # in pixels


#constants
radiusDistCm = 24.5/2/2 # fixed for shorter


#----------------Presets--------------
#prophesee test
#outer box test Assuming height and width of camera same fov per pixel, top to bottom 24.5cm on 800, 1cm is 32.65 pixels, say 33
camWidth = 640
camHeight = 480



#manual fix settings!!
#474, 0, -6
#pixelSpinner = 300 #diameter in pixels, manually fixed
pixelSpinner = 474/2
#xOffset = -0.5 #actually yOffset here
#yOffset = -6 #inverted xOffset here
#xOffset = 4.5 #actually yOffset here
#yOffset = -5 #inverted xOffset here
xOffset =5  #actually yOffset here
yOffset = -8.5 #inverted xOffset here


#help thing
centimeter = math.ceil(474/24.5);


#test Experimental rpm measurements approximate...

#----TOP second lap start------
#rpm = 35.9 #0.9549027282632843
rpm = 36 # 0.955470697427738
#rpm = 36.1 #0.9554071727041712
#rpm = 36.2 #0.955439950536213
#rpm = 36.3 #0.9551871920655787
#rpm = 36.5 #0.9542633161512027
#rpm = 36.6 #0.9536729003154506
#rpm = 36.7 #0.953182166484993
#rpm = 36.8 #0.9525844349726303
#rpm = 36.9 #0.951870729855764
#rpm = 37.5 #0.9426279938475061



#startBigFrontAngle = np.arccos(1/radiusDistCm)
#startSmallFrontAngle = 0

startBigFrontAngle =  np.arccos(-1/radiusDistCm)
startSmallFrontAngle = np.pi



#place presets
#startIndex of event§§s 2029765
#startIndex = 2029765
#startIndex = 14776000 #for front
startIndex = 14790000 #for back

#startIndex = 4045000 - 1000 #to compensate for alignment window

startTime = nparray[startIndex][2]
print("startTime: ", startTime)
endIndex = 19324645



lapTime = (60 / rpm ) * 1000 * 1000;



#viewStep = 3000
viewStep = 50000
#viewStep = 1*lapTime/4


#distance between top and bottom of box in pixels.
frontDist = np.linalg.norm((spinnerPosition(pixelSpinner/2, 0, 10, startBigFrontAngle)) - spinnerPosition(centimeter, 0, 10, startSmallFrontAngle))




#------------------------------draw part here--------------------
#a = np.zeros((camHeight,camWidth)) #y, x format
a = np.zeros((camWidth, camHeight)) #x, y format

tempTime = startTime

# fill a with content
for e in nparray[startIndex:endIndex]:
    break; #for not drawing
    #1ms window
    #1 lap window
    #if(e[2] > (startTime +1*lapTime/4)):
    if(e[2] > tempTime+viewStep):
        #draw box start
        # start pos
        startTopXY = spinnerPosition(pixelSpinner/2, tempTime-startTime, rpm, startBigFrontAngle)
        startBotXY = spinnerPosition(centimeter, tempTime-startTime, rpm, startSmallFrontAngle)
        # end pos
        endTopXY = spinnerPosition(pixelSpinner/2, tempTime-startTime+viewStep, rpm, startBigFrontAngle)
        endBotXY = spinnerPosition(centimeter, tempTime-startTime+viewStep, rpm, startSmallFrontAngle)
        #a[spinTopY,spinTopX] = -1
        #a[spinBotY,spinBotX] = -1
        #print(abs(math.floor(startTopXY[0] - startBotXY[0])))
        #print(abs(math.floor(endTopXY[0] - endBotXY[0])))

        #draw line for box, start
        #x_values = [camWidth - 1 - startTopXY[0], camWidth - 1  - startBotXY[0]]
        startX_values = [startTopXY[0], startBotXY[0]]
        #y_values = [camHeight- 1 - startTopXY[1],camHeight- 1 - startBotXY[1]]
        startY_values = [startTopXY[1], startBotXY[1]]
        endX_values = [endTopXY[0], endBotXY[0]]
        endY_values = [endTopXY[1], endBotXY[1]]

        plt.plot(endX_values, endY_values)

        plt.plot(startX_values, startY_values)
        plt.imshow(a)
        plt.show()

        tempTime = tempTime + viewStep;
        #a = np.zeros((camHeight,camWidth)) #y, x format
        a = np.zeros((camWidth, camHeight)) #x, y format


    if(tempTime > startTime+viewStep*5):
        break;

    #inversion
    #a[camHeight-1-e[0], camWidth-1-e[1]] += 1;
    a[e[0], e[1]] += 1;



# triangle area with height margins
smalltriangle = frontDist * marginsmall / 2
largetriangle = frontDist * marginlarge / 2


# radius top pos
topRad = math.sqrt((pixelSpinner/2)**2)
botRad = math.sqrt((centimeter)**2)




print("----------------------starting generating ratio---------")
#counters
evsProcessed = 0;
frontSmall = 0;
frontBig = 0;
extra = 0;
discarded = 0;
#for e in eventarr:
for a in nparray[startIndex:endIndex]:
    if(a[2]> startTime+lapTime/8):
        print(evsProcessed)
        break;
    evsProcessed += 1
    #inverted
    #evPos = [camWidth-1-a[1], camHeight-1-a[0]];
    evPos = [a[1], a[0]]

    #must generate the place of the virtual spinner at that time
    topPos = spinnerPosition(topRad, a[2]-startTime, rpm, startBigFrontAngle);
    botPos = spinnerPosition(botRad, a[2]-startTime, rpm, startSmallFrontAngle);

    #herons
    s = (np.linalg.norm(topPos - evPos) +  np.linalg.norm(evPos -botPos) + np.linalg.norm(topPos -botPos))/2
    area = math.sqrt(s * (s - np.linalg.norm(topPos - evPos)) * (s - np.linalg.norm(evPos - botPos)) * (s-np.linalg.norm(topPos - botPos)))

    #things used to decide if too far out or too far in
    vector = [topPos[0] - botPos[0], topPos[1] - botPos[1]]
    pointBehind= [botPos[0] - vector[0]/10000, botPos[1] -   vector[1]/10000]
    distPointBehind = math.sqrt((pointBehind[0] - evPos[0])**2 + (pointBehind[1] - evPos[1])**2)
    distPointBot = math.sqrt((botPos[0] - evPos[0])**2 + (botPos[1] - evPos[1])**2)
    pointFront = [topPos[0] + vector[0]/10000, topPos[1] +  vector[1]/10000]
    distPointFront = math.sqrt((pointFront[0] - evPos[0])**2 + (pointFront[1] - evPos[1])**2)
    distPointTop = math.sqrt((topPos[0] - evPos[0])**2 + (topPos[1] - evPos[1])**2)


    #if(NOT BEHIND IT && NOT OUTSIDE CIRCLE (RADIUS 2 HIGH)):
    if(distPointBehind >= distPointBot and  distPointFront >= distPointTop):
        if(area <= smalltriangle ):
            frontSmall += 1;
            frontBig +=1;
        elif (area <= largetriangle):
            frontBig +=1;
        elif (area <= largetriangle * 2):
            extra +=1
    else:
        discarded +=1


print("ratio")
print(frontSmall/frontBig)
print(frontSmall)
print(frontBig)
print(extra)
print(discarded)


