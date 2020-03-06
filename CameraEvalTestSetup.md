# Camera evaluation test setups

In this document we describe the test setups used to compare the dvs DVXplorer 640x480, davis blue 346x260, the Propesee 640x480 VGA and the Celex 1000x800 event cameras.

# Flash test
### Why flash test?
TODO


### Physical setup

We did two test setups for every camera. One with higher intensity with the flashed area closer and one lower intensity test with the flashed area farther away.

We setup a simple surface either about 15cm or 30cm centered in front of the center of the tripod mountpoint. The surface was the side of a small cardboard box with the width of 10cm and height of 14cm on the shown side. (Due to a mistake the tripod mountpoint was misplaced 2cm to the right of center of the cardboard box for all data taken in the high intensity test, this should however not have much impact on the validity of the test since the cardboard box was still fully in frame on all of the cameras.)

We also made sure to not have an immideate background that would also get illuminated by the camera, the wall being 3.5 meter back from the flashed area. 
We wanted to use the same lens with the same settings and the same tripod on every sensor, however we ran into compatibility issues. The lens we used on the prophesee camera was its default lens TODO (prophesee 640), with the settings open maxed out and distance maxed out.
For the celex, davis and the DVXplorer we instead used the DVXplorer default lens (TODO) with maximum open and near settings. We did however tweak wide/tele in order to achieve the sharp image that we ideally require, the Prophesee cameras lens lacked this setting and was sharp at the settings we tested it at.

Height of the tripod was about 10cm to the bottom of the camera housing.
We then flashed the built-in phone flashlight of a samsung a50 phone at a periodicity of 10hz, having it stay lit for about 1/4 of the time and be turned off for the rest using a phone app. (should we say that the lightsource doesnt matter?)
We positioned the phone flashlight 5 cm left of the center of the camera sensor and 4 cm over the camera mountpoint but at the same distance from the box, with the flashlight aimed parallel with the camera. 

The only thing that was changed between the tests were the cameras or the distance of the tripod and the light.

Due to the roughly similar sensor position of the cameras relative to the mounting point (only varying a couple of centimeters in total relative distance) and the simplicity of the test we are performing we determine that using the mounting point is good enough to achieve accurate results. 

### Software Settings
It is very difficult to determine what is a fair settings for the devices, due to the different available settings. Therefor we only tried to tweak the basic settings and see what results changed and kept the rest at default.

##### Prophesee
For the prophesee we tested changing the sensitivity metric since TODO ~~ that one seemed the most relevant of the basic settings
Default basic settings: Polarity 48 ~~
We changed sensitivities between 50, 60, 70, 80 and 90 for both test setups.
 
##### DVXplorer
For the DVXplorer we also changed its sensitivity metric since TODO.
We ran tests at very low, low, medium, high and very high settings for both test setups.

##### 346 DVS
For the 346 DVS we tried to enable / disable hardware filter isntead since that one did not have a sensitivity slider


#### Celex
For the Celex camera TODO


### Analysis

TODO



# Movement test

### Why do movement test?
TODO


### Physical setup
We use a simple tablefan with a removed front grill to test 


### Software settings
TODO

### Analysis
TODO
