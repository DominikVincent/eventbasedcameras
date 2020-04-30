import matplotlib.pyplot as plt
import numpy as np
import math
from os import listdir, getcwd, system
from os.path import isfile, join, isdir, normpath



#draw box

testPath = "H:\\evs\\fixedSpinningWheel\\dvs346\\100rpm\\dvSave-2020_03_17_20_41_05events.npy"

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
    if (countevents[int(e/timewindow)] > 3):
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

    y = (radius * np.sin(angle) + camHeight /2) + yOffset
    #return np.array([x,y]);
    return np.array([y,x]); #inverted




#margins
marginsmall =2 # in pixels
marginlarge = 10 # in pixels




#----------------Presets--------------
#dvxplorer test
#outer box test Assuming height and width of camera same fov per pixel, top to bottom 24.5cm on 800, 1cm is 32.65 pixels, say 33
camWidth = 346
camHeight = 260



#constants
radiusDistCm = 24.5/2/2 # fixed for shorter


#manual fix settings!!
#pixelSpinner = 476/2 #diameter in pixels, now set to half
#pixelSpinner = 258
pixelSpinner = 258/2

#pixelSpinner = 300 #diameter in pixels, manually fixed

xOffset = 1.5 #actually yOffset here
yOffset = -1 #inverted xOffset here

#help thing
#pixelSpinner = 474 #diameter in pixels, manually fixed
centimeter = math.ceil(258/24.5);



#test Experimental rpm measurements approximate...

#----TOP second lap start------


#rpm = 440 #0.5050373988704014
#rpm = 445 #0.5107551841535128
#rpm = 448 #0.5133205913328392
#rpm = 449 #0.5139551246970526
#rpm = 449.5 #0.514507224245272
#rpm = 449.7 #0.5146148420970144
#rpm = 449.8 #0.5211207232483829

#rpm = 449.9 #0.514678791204484
#rpm = 450 #0.5148379003488964
#rpm = 460 #0.4960261427361117
#rpm = 464 #0.47747526776224347
#rpm = 468 #0.4575448207171315
#rpm = 470 #0.4465800359336481
#rpm = 472 #0.4380439809948282


rpm = 450 #0.6325841236845524
#rpm = 451  #0.6315378610460578
#rpm = 455 #0.6222893941385201

#rpm = 460 #0.6124783823333777





startBigFrontAngle = np.arccos(1/radiusDistCm)
#startBigFrontAngle = np.arccos(1.05/radiusDistCm) #manual modify
startSmallFrontAngle = 0

#place presets
#startIndex of events 4200
startIndex =5251000
startTime = nparray[startIndex][2]
print("startTime: ", startTime)
endIndex =8611688


#lapTime = abs((60 / rpm ) * 1000 * 1000);
lapTime = (60 / rpm ) * 1000 * 1000;

#viewStep = lapTime/4
viewStep = 4000



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
    #if(e[2] > (startTime +4*lapTime/4)):
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