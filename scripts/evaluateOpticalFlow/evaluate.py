import numpy as np





"""
returns True if the event is outside of the disk
@param[in] vec - the coordinates of the pixel
@param[in] radius - the radius of the disk in m
@param[in] Z - the distance from the sensor to the disk in m
@param[in] focallength - the focallenght of the camera in m
"""
def outOfDisk(vec, radius, Z, focallength):
    if np.linalg.norm(vec) > (radius/Z*focallength):
        return True
    return False


"""
calculates the motion flow induced by the rotation of the camera along the z-axis
@param[in] wz - the angular velocity in rad/s
@param[in] px_size - the pixel size
@param[in] x_res - the x resolution
@param[in] y_res - the y resolution
"""
def getRotationalMatrix(w_z, px_size, x_res, y_res):
    flow_mat = np.zeros((2,y_res, x_res))

    for y in range(- (y_res//2) , (y_res//2), 1):
        y_m = y * px_size + 0.5 * px_size
        for x in range(- (x_res//2) , (x_res//2), 1):
            x_m = x * px_size + 0.5 * px_size
            x_flow = w_z * y_m
            y_flow = w_z * x_m
            
            #convert to pixel speed
            x_flow = x_flow/px_size
            y_flow = y_flow/px_size

            flow_mat[0, y + y // 2, x + x // 2] = x_flow
            flow_mat[1, y + y // 2, x + x // 2] = y_flow
    return flow_mat



"""
computes statistics for a error and additional the percentail measurements

@param[in] errors - the np array of erros
@param[in] pa1 - the error measure for the first percentile
@param[in] pa2 - the error measure for the second percentile
@param[in] pa3 - the error measure for the third percentile
@param[out] mean - the mean error
@param[out] std  - the standard deviation of the erro
@param[out] cpa1 the number of values below pa1
"""
def compute_statistics(errors, pa1, pa2, pa3):
    mean = np.mean(errors)
    std  = np.std(errors)

    cpa1, _ = np.where(errors < pa1).shape[0] / errors.shape[0]
    cpa2, _ = np.where(errors < pa2).shape[0] / errors.shape[0]
    cpa3, _ = np.where(errors < pa3).shape[0] / errors.shape[0]

    return mean, std, cpa1, cpa2, cpa3

"""
calculates the angular error between two vectors. returns 181, if one of them is 0
@param[in] vec1 - first flow vector
@param[in] vec2 - second flow vector
@param[out] angular error or 181
"""
def calc_angular_error(vec1, vec2):
    if not vec1.any() or not vec1.any():
        return 181
    return np.arccos( np.dot(vec1,vec2)/(np.linalg.norm(vec1) * np.linalg.norm(vec2)) )

"""
calculates the angular error between two vectors. returns 181, if one of them is 0
@param[in] vec1 - first flow vector
@param[in] vec2 - second flow vector this has to be the ground truth
@param[out] endpoint error 
@param[out] relative endpoint error - 1
"""
def calc_endpoint_error(vec1, vec2):
    eep = np.linalg.norm(vec1-vec2) 

    if not vec1.any() or not vec1.any():
        rel_eep = -1
    else:
        rel_eep = eep/np.linalg.norm(vec2)
    
    return eep, rel_eep

"""
returns a matrix giving the motion vector at the pixel (x,y)
if downsamping with factor 2 is used, double the pixel size.
@param[in] focalLength - the focal length of the camera in m
@param[in] Z - the distance between the canvas and the image sensor in m
@param[in] px_size - the pixel size of a pixel of the image sensor in m
@param[in] T_x - the translating speed in m/s
@param[in] x_res - resolution width
@param[in] y_res - resolution height
@param[out] motion_mat - 2 x X x Y matrix containing the motion vector at each pixel
"""
def getTranslatingFlowMatrix(focalLength, Z, T_x, px_size, x_res, y_res):
    x_flow_ms = focalLength/Z * T_x
    x_flow_px = x_flow_ms/px_size
    x = np.full((y_res,x_res), x_flow_px)
    y = np.zeros_like(x)

    motion_mat = np.stack(x,y,axis=2)
    return motion_mat


"""
gets an array of optical flow vectors including their position and saves statistics as a file or the disktest
@param[in] the array of flow vectors - normalized so that it the position ranges from (0,0) till (xres,yres)
@param[in] wz - the angular velocity in w_z
@param[in] px_size - the pixel size, double it if the downsampling is halfing
@param[in] radius - the size of the disk in m
@param[in] focallength - focallength of camera/lense in m
@param[in] Z - the distance from the senor to the disk
@param[in] x resolution
@param[in] y resolution
@param[in] filename - the filename
@param[in] p* - the percentile values for angular, endpoint and relative enpoint error
"""
def evaluateRotationalFlow(arr, w_z, px_size, x_res, y_res, filename, \
                            radius, focallength, Z, \
                            pa1, pa2, pa3, \
                            pe1, pe2, pe3, \
                            pre1, pre2, pre3):

    flow_mat = getRotationalMatrix(w_z, px_size, x_res, y_res)
    angular_errors = []
    endpoint_errors = []
    relative_endpoint_errors = []
    num_vectors = 0
    for ofEvent in arr:
        if outOfDisk(ofEvent[1:3], radius, Z, focallength):
            continue
        num_vectors += 1
        angular_error = calc_angular_error(ofEvent[5:7], flow_mat[:, ofEvent[1], ofEvent[2] ])
        if  angular_error!= 181:
            angular_errors.append(angular_error)

        eep, rel_eep = calc_endpoint_error(ofEvent[5:7], flow_mat[:, ofEvent[1], ofEvent[2] ]) 
        endpoint_errors.append(eep)
        if rel_eep != -1:
            relative_endpoint_errors.append(rel_eep)
        
    stats = "TranlationFlow statistics:\n"
    stats += "Number of valid flow vectors: " + num_vectors +"\n"
    pure_stats = ""+num_vectors+" "
    for name in ["average_angular", "average endpoint", "rel endpoint"]:
        if name == "average_angular":
            mean, std, p1, p2, p3 = compute_statistics(np.array(angular_errors), pa1, pa2, pa3)
        elif name == "average endpoint":
            mean, std, p1, p2, p3 = compute_statistics(np.array(endpoint_errors), pe1, pe2, pe3)
        elif name == "rel endpoint":
            mean, std, p1, p2, p3 = compute_statistics(np.array(relative_endpoint_errors), pre1, pre2, pre3)
        else:
            print("Error not known statistic")
        stats += name+ ": mean: "+mean+ " std: ", std, " p"+pa1+": "+p1+" p"+pa2+": "+p2+" p"+pa3+": "+p3+"\n"
        pure_stats = mean +" "+ std + " " + p1 + " " + p2 + " " + p3 + "\n"

    with open(filename+"disk", "w") as file:
        file.write(stats+pure_stats)
        file.close()

"""
gets an array of optical flow vectors including their position and saves statistics as a file
@param[in] the array of flow vectors - normalized so that it the position ranges from (0,0) till (xres,yres)
@param[in] focalLength - focal length
@param[in] Z - the distance of the sensor to the canvas
@param[in] T_x - the x translation speed
@param[in] px_size - the pixel size, double it if the downsampling is halfing
@param[in] x resolution
@param[in] y resolution
@param[in] filename - the filename
@param[in] p* - the percentile values for angular, endpoint and relative enpoint error
"""
def evaluateTranlationFlow(arr, focalLength, Z, T_x, px_size, x_res, y_res, filename, \
                            pa1, pa2, pa3, \
                            pe1, pe2, pe3, \
                            pre1, pre2, pre3):

    flow_mat = getTranslatingFlowMatrix(focalLength, Z, T_x, px_size, x_res, y_res)
    angular_errors = []
    endpoint_errors = []
    relative_endpoint_errors = []
    num_of_vec = arr.shape[0]
    for ofEvent in arr:
        angular_error = calc_angular_error(ofEvent[5:7], flow_mat[:, ofEvent[1], ofEvent[2] ])
        if  angular_error!= 181:
            angular_errors.append(angular_error)

        eep, rel_eep = calc_endpoint_error(ofEvent[5:7], flow_mat[:, ofEvent[1], ofEvent[2] ]) 
        endpoint_errors.append(eep)
        if rel_eep != -1:
            relative_endpoint_errors.append(rel_eep)
        
    stats = "TranlationFlow statistics:\n"
    stats += "Number of valid flow vectors: " + num_of_vec +"\n"
    pure_stats = ""+num_of_vec+" "
    for name in ["average_angular", "average endpoint", "rel endpoint"]:
        if name == "average_angular":
            mean, std, p1, p2, p3 = compute_statistics(np.array(angular_errors), pa1, pa2, pa3)
        elif name == "average endpoint":
            mean, std, p1, p2, p3 = compute_statistics(np.array(endpoint_errors), pe1, pe2, pe3)
        elif name == "rel endpoint":
            mean, std, p1, p2, p3 = compute_statistics(np.array(relative_endpoint_errors), pre1, pre2, pre3)
        else:
            print("Error not known statistic")
        stats += name+ ": mean: "+mean+ " std: ", std, " p"+pa1+": "+p1+" p"+pa2+": "+p2+" p"+pa3+": "+p3+"\n"
        pure_stats = mean +" "+ std + " " + p1 + " " + p2 + " " + p3 + "\n"

    with open(filename+"translational", "w") as file:
        file.write(stats+pure_stats)
        file.close()


# path to file of OF-vectors
path = "file.npy"
focallength = 0.008
px_size = 1.5E-5
Z = 0.3
radius = 0.1
T_x = 0.01
rpm = 10
x_res = 480
y_res = 640
final_file_name = "of method: kanade"

#percentiles
pa1, pa2, pa3 = 2.5, 5, 15
pe1, pe2, pe3 = 1, 2, 5
pre1, pre2, pre3 = 1, 2, 5

w_z = 2 * np.pi * rpm /60
ofVecs = np.load(path, allow_pickle=True)

#call the evaluation
evaluateTranlationFlow(ofVecs, focallength, Z, T_x, px_size, x_res, y_res, final_file_name, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

evaluateRotationalFlow(ofVecs, w_z, px_size, x_res, y_res, final_file_name, radius, focallength, Z, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)
