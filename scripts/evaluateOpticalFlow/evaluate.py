import numpy as np
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import xlsxwriter

"""
returns True if the event is outside of the disk
@param[in] vec - the coordinates of the pixel
@param[in] radius - the radius of the disk in m
@param[in] Z - the distance from the sensor to the disk in m
@param[in] focallength - the focallenght of the camera in m
"""
def outOfDisk(vec, radius, Z, focallength, px_size, x_res, y_res):
    length_vec = (radius/Z*focallength) / px_size
    
    vec[0] = vec[0] - x_res/2
    vec[1] = vec[1] - y_res/2
    norm =  np.linalg.norm(vec)
    if norm > length_vec:
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
    flow_mat = np.zeros((y_res, x_res, 2))

    for y in range(- (y_res//2) , (y_res//2), 1):
        y_m = y * px_size + 0.5 * px_size
        for x in range(- (x_res//2) , (x_res//2), 1):
            #print("x:",x, " y: ", y)
            x_m = x * px_size + 0.5 * px_size
            x_flow = w_z * y_m
            y_flow = w_z * x_m
            
            #convert to pixel speed
            x_flow = x_flow/px_size
            y_flow = y_flow/px_size

            flow_mat[y + y_res // 2, x + x_res // 2, 0] = x_flow
            flow_mat[y + y_res // 2, x + x_res // 2, 1] = y_flow
    for i in range(640):
        print(flow_mat[240, i, :])
    # print(flow_mat[240,:,:])
    return flow_mat

"""
returns a matrix giving the motion vector at the pixel (x,y)
if downsamping with factor 2 is used, double the pixel size.
@param[in] focalLength - the focal length of the camera in m
@param[in] Z - the distance between the canvas and the image sensor in m
@param[in] px_size - the pixel size of a pixel of the image sensor in m
@param[in] T_x - the translating speed in m/s
@param[in] x_res - resolution width
@param[in] y_res - resolution height
@param[out] motion_mat - X x Y x 2 matrix containing the motion vector at each pixel
"""
def getTranslatingFlowMatrix(focalLength, Z, T_x, px_size, x_res, y_res):
    x_flow_ms = focalLength/Z * T_x
    x_flow_px = x_flow_ms/px_size
    x = np.full((y_res,x_res), x_flow_px)
    y = np.zeros_like(x)

    motion_mat = np.stack((x,y), axis=2)
    print(motion_mat.shape)
    print(motion_mat)
    return motion_mat

"""
returns the groundtruth matrix for the rotating bar synthetic scene given the path to the GT generated 
by Matlab. 
@param[in] vxGT_path - the path to the matrix for the x direction flow
@param[in] vyGT_path - the path to the matrix for the y direction flow
@param[out] the stacked yres x xres x 2 matrix
"""
def getRotatingBarFlowMatrix(vxGT_path, vyGT_path):
    a = np.load(vxGT_path, allow_pickle=True)
    b = np.load(vyGT_path, allow_pickle=True)

    return np.stack((a,b), axis=2)

"""
returns the full flow groundtruth matrix for the translating square synthetic scene given the path to the GT generated 
by Matlab. 
@param[in] vGT_path - the path to the matrix for the motion flow - Y x X x 2
@param[out] the stacked yres x xres x 2 matrix
"""
def getTranslatingSquareFullFlowMatrix(vGT_path):
    a = np.load(vGT_path, allow_pickle=True)
    

    x_flow = a[a[:,:,0] != 0][0,0]
    y_flow = a[a[:,:,1] != 0][0,1]

    c = np.full( (a.shape[0], a.shape[1], 2), [x_flow,y_flow])

    return c

"""
returns the normal flow groundtruth matrix for the translating square synthetic scene given the path to the GT generated 
by Matlab. 
@param[in] vxGT_path - the path to the matrix for the x direction flow
@param[in] vyGT_path - the path to the matrix for the y direction flow
@param[out] the stacked yres x xres x 2 matrix
"""
def getTranslatingSquareNormalFlowMatrix(vGT_path):
    a = np.load(vGT_path, allow_pickle=True)
    
    return a

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

    cpa1 = np.where(errors < pa1)[0].shape[0] / errors.shape[0]
    cpa2 = np.where(errors < pa2)[0].shape[0] / errors.shape[0]
    cpa3 = np.where(errors < pa3)[0].shape[0] / errors.shape[0]

    return mean, std, cpa1, cpa2, cpa3

"""
calculates the angular error between two vectors. returns 181, if one of them is 0
@param[in] vec1 - first flow vector
@param[in] vec2 - second flow vector
@param[out] angular error or 181
"""
def calc_angular_error(vec1, vec2):
    if not vec1.any() or not vec2.any():
        return 181
    value = np.dot(vec1,vec2)/(np.linalg.norm(vec1) * np.linalg.norm(vec2)) 
    if value > 1:
        value = 1
    if value < -1:
        value = -1
    return np.degrees(np.arccos(value))

"""
calculates the angular error between two vectors. returns 181, if one of them is 0
@param[in] vec1 - first flow vector
@param[in] vec2 - second flow vector this has to be the ground truth
@param[out] endpoint error 
@param[out] relative endpoint error - 1
"""
def calc_endpoint_error(vec1, vec2):
    eep = np.linalg.norm(vec1-vec2) 

    if not vec1.any() or not vec2.any():
        rel_eep = -1
    else:
        rel_eep = eep/np.linalg.norm(vec2)
    
    return eep, rel_eep




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
    zero_vectors = 0
    for ofEvent in tqdm(arr):
        if outOfDisk(ofEvent[2:4], radius, Z, focallength, px_size, x_res, y_res):
            continue
        num_vectors += 1
        angular_error = calc_angular_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ])
        if  angular_error!= 181:
            angular_errors.append(angular_error)
        else:
            zero_vectors +=1
        eep, rel_eep = calc_endpoint_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ])
        endpoint_errors.append(eep)
        if rel_eep != -1:
            relative_endpoint_errors.append(rel_eep)
        
    stats = "TranlationFlow statistics:\n"
    stats += "Number of valid flow vectors: " + str(num_vectors) + " zero vectors: " + str(zero_vectors)+ "\n"
    pure_stats = ""+str(num_vectors)+" "
    stats_list = [num_of_vec, zero_vectors]

    for name in ["average_angular", "average endpoint", "rel endpoint"]:
        if name == "average_angular":
            per1, per2, per3 = pa1, pa2, pa3
            mean, std, p1, p2, p3 = compute_statistics(np.array(angular_errors), per1, per2, per3)
        elif name == "average endpoint":
            per1, per2, per3 =  pe1, pe2, pe3
            mean, std, p1, p2, p3 = compute_statistics(np.array(endpoint_errors), per1, per2, per3)
        elif name == "rel endpoint":
            per1, per2, per3 = pre1, pre2, pre3
            mean, std, p1, p2, p3 = compute_statistics(np.array(relative_endpoint_errors), per1, per2, per3)
        else:
            print("Error not known statistic")
        stats += name+ ": mean: "+str(mean)+ " std: "+ str(std)+ " p"+str(per1)+": "+str(p1)+\
                " p"+str(per2)+": "+str(p2)+" p"+str(per3)+": "+str(p3)+"\n"
        pure_stats = str(mean) +" "+ str(std) + " " + str(per1) + " " + str(p1) + " " +\
                     str(per2) +  " " + str(p2) + " "  + str(per3) + " " + str(p3) + "\n"
        stats_list.extend([mean, std, p1, p2, p3])
    with open(filename+"_disk_stats", "w") as file:
        file.write(stats+pure_stats)
        file.close()
    return stats_list

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
    zero_vectors = 0
    for ofEvent in tqdm(arr):
        angular_error = calc_angular_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ])
        if  angular_error!= 181:
            angular_errors.append(angular_error)
        else:
            zero_vectors += 1
        eep, rel_eep = calc_endpoint_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ]) 
        endpoint_errors.append(eep)
        if rel_eep != -1:
            relative_endpoint_errors.append(rel_eep)
        
    stats = "TranlationFlow statistics:\n"
    stats += "Number of valid flow vectors: " + str(num_of_vec) + " zero vectors: " + str(zero_vectors)+ "\n"
    pure_stats = ""+str(num_of_vec)+" "
    stats_list = [num_of_vec, zero_vectors]

    for name in ["average_angular", "average endpoint", "rel endpoint"]:
        if name == "average_angular":
            per1, per2, per3 = pa1, pa2, pa3
            mean, std, p1, p2, p3 = compute_statistics(np.array(angular_errors), per1, per2, per3)
        elif name == "average endpoint":
            per1, per2, per3 =  pe1, pe2, pe3
            mean, std, p1, p2, p3 = compute_statistics(np.array(endpoint_errors), per1, per2, per3)
        elif name == "rel endpoint":
            per1, per2, per3 = pre1, pre2, pre3
            mean, std, p1, p2, p3 = compute_statistics(np.array(relative_endpoint_errors), per1, per2, per3)
        else:
            print("Error not known statistic")
        stats += name+ ": mean: "+str(mean)+ " std: "+ str(std)+ " p"+str(per1)+": "+str(p1)+\
                " p"+str(per2)+": "+str(p2)+" p"+str(per3)+": "+str(p3)+"\n"
        pure_stats += str(mean) +" "+ str(std) + " " + str(per1) + " " + str(p1) + " " +\
                     str(per2) +  " " + str(p2) + " "  + str(per3) + " " + str(p3) + "\n"
        stats_list.extend([mean, std, p1, p2, p3])
    file_write_name = filename+"_transcart_stats.txt"
    with open(file_write_name, "w") as file:
        print("going to write file to:"+ file_write_name)
        file.write(stats+pure_stats)
        print("filewritten")
        file.close()
    return stats_list


"""
gets an array of optical flow vectors including their position and saves statistics as a file
@param[in] arr the array of flow vectors - normalized so that it the position ranges from (0,0) till (xres,yres)
@param[in] x resolution
@param[in] y resolution
@param[in] filename - the filename
@param[in] p* - the percentile values for angular, endpoint and relative enpoint error
"""
def evaluateRotatingBarFlow(arr, vxGT_path, vyGT_path, filename, \
                            pa1, pa2, pa3, \
                            pe1, pe2, pe3, \
                            pre1, pre2, pre3):

    flow_mat = getRotatingBarFlowMatrix(vxGT_path, vyGT_path)
    angular_errors = []
    endpoint_errors = []
    relative_endpoint_errors = []
    num_of_vec = arr.shape[0]
    zero_vectors = 0
    for ofEvent in tqdm(arr):
        angular_error = calc_angular_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ])
        if  angular_error!= 181:
            angular_errors.append(angular_error)
        else:
            zero_vectors += 1
        eep, rel_eep = calc_endpoint_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ]) 
        endpoint_errors.append(eep)
        if rel_eep != -1:
            relative_endpoint_errors.append(rel_eep)
        
    stats = "TranlationFlow statistics:\n"
    stats += "Number of valid flow vectors: " + str(num_of_vec) + " zero vectors: " + str(zero_vectors)+ "\n"
    pure_stats = ""+str(num_of_vec)+" "
    stats_list = [num_of_vec, zero_vectors]

    for name in ["average_angular", "average endpoint", "rel endpoint"]:
        if name == "average_angular":
            per1, per2, per3 = pa1, pa2, pa3
            mean, std, p1, p2, p3 = compute_statistics(np.array(angular_errors), per1, per2, per3)
        elif name == "average endpoint":
            per1, per2, per3 =  pe1, pe2, pe3
            mean, std, p1, p2, p3 = compute_statistics(np.array(endpoint_errors), per1, per2, per3)
        elif name == "rel endpoint":
            per1, per2, per3 = pre1, pre2, pre3
            mean, std, p1, p2, p3 = compute_statistics(np.array(relative_endpoint_errors), per1, per2, per3)
        else:
            print("Error not known statistic")
        stats += name+ ": mean: "+str(mean)+ " std: "+ str(std)+ " p"+str(per1)+": "+str(p1)+\
                " p"+str(per2)+": "+str(p2)+" p"+str(per3)+": "+str(p3)+"\n"
        pure_stats += str(mean) +" "+ str(std) + " " + str(per1) + " " + str(p1) + " " +\
                     str(per2) +  " " + str(p2) + " "  + str(per3) + " " + str(p3) + "\n"
        stats_list.extend([mean, std, p1, p2, p3])
    file_write_name = filename+"_rotating_bar_stats.txt"
    with open(file_write_name, "w") as file:
        print("going to write file to:"+ file_write_name)
        file.write(stats+pure_stats)
        print("filewritten")
        file.close()
    return stats_list


"""
gets an array of optical flow vectors including their position and saves statistics as a file
@param[in] arr the array of flow vectors - normalized so that it the position ranges from (0,0) till (xres,yres)
@param[in] x resolution
@param[in] y resolution
@param[in] filename - the filename
@param[in] p* - the percentile values for angular, endpoint and relative enpoint error
"""
def evaluateTranslatingSquareFullFlow(arr, vGT_path, filename, \
                            pa1, pa2, pa3, \
                            pe1, pe2, pe3, \
                            pre1, pre2, pre3):

    flow_mat = getTranslatingSquareFullFlowMatrix(vGT_path)
    angular_errors = []
    endpoint_errors = []
    relative_endpoint_errors = []
    num_of_vec = arr.shape[0]
    zero_vectors = 0
    for ofEvent in tqdm(arr):
        angular_error = calc_angular_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ])
        if  angular_error!= 181:
            angular_errors.append(angular_error)
        else:
            zero_vectors += 1
        eep, rel_eep = calc_endpoint_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ]) 
        endpoint_errors.append(eep)
        if rel_eep != -1:
            relative_endpoint_errors.append(rel_eep)
    stats = "TranlationFlow statistics:\n"
    stats += "Number of valid flow vectors: " + str(num_of_vec) + " zero vectors: " + str(zero_vectors)+ "\n"
    pure_stats = ""+str(num_of_vec)+" "
    stats_list = [num_of_vec, zero_vectors]

    for name in ["average_angular", "average endpoint", "rel endpoint"]:
        if name == "average_angular":
            per1, per2, per3 = pa1, pa2, pa3
            mean, std, p1, p2, p3 = compute_statistics(np.array(angular_errors), per1, per2, per3)
        elif name == "average endpoint":
            per1, per2, per3 =  pe1, pe2, pe3
            mean, std, p1, p2, p3 = compute_statistics(np.array(endpoint_errors), per1, per2, per3)
        elif name == "rel endpoint":
            per1, per2, per3 = pre1, pre2, pre3
            mean, std, p1, p2, p3 = compute_statistics(np.array(relative_endpoint_errors), per1, per2, per3)
        else:
            print("Error not known statistic")
        stats += name+ ": mean: "+str(mean)+ " std: "+ str(std)+ " p"+str(per1)+": "+str(p1)+\
                " p"+str(per2)+": "+str(p2)+" p"+str(per3)+": "+str(p3)+"\n"
        pure_stats += str(mean) +" "+ str(std) + " " + str(per1) + " " + str(p1) + " " +\
                     str(per2) +  " " + str(p2) + " "  + str(per3) + " " + str(p3) + "\n"
        stats_list.extend([mean, std, p1, p2, p3])
    file_write_name = filename+"_translating_square_fullf_stats.txt"
    with open(file_write_name, "w") as file:
        print("going to write file to:"+ file_write_name)
        file.write(stats+pure_stats)
        print("filewritten")
        file.close()

    return stats_list


"""
gets an array of optical flow vectors including their position and saves statistics as a file
@param[in] arr the array of flow vectors - normalized so that it the position ranges from (0,0) till (xres,yres)
@param[in] x resolution
@param[in] y resolution
@param[in] filename - the filename of the stats
@param[in] p* - the percentile values for angular, endpoint and relative enpoint error
"""
def evaluateTranslatingSquareNormalFlow(arr, vGT_path, filename, \
                            pa1, pa2, pa3, \
                            pe1, pe2, pe3, \
                            pre1, pre2, pre3):

    flow_mat_orig = getTranslatingSquareNormalFlowMatrix(vGT_path)
    angular_errors = []
    endpoint_errors = []
    relative_endpoint_errors = []
    num_of_vec = arr.shape[0]
    zero_vectors = 0
    ts_last = arr[0,1]
    tmpMat = np.zeros((y_res, x_res))
    rotate_by = int( ((ts_last // (25000*downampling))//downampling) +1 )
    flow_mat = np.roll(flow_mat_orig, (rotate_by,rotate_by), axis=(0,1))
    for ofEvent in tqdm(arr):
        if ofEvent[1] > ts_last+1000:
            plt.subplot(3,1,1)
            plt.imshow(tmpMat)
            plt.subplot(3,1,2)
            plt.imshow(np.sum(flow_mat, axis=2))
            plt.subplot(3,1,3)
            plt.imshow(np.sum(flow_mat, axis=2)*tmpMat)
            
            debug_mat = flow_mat.sum(axis=2)
            debug_ind = np.where(debug_mat != 0)
            debug_ind = np.stack((debug_ind[0], debug_ind[1]), axis=1)

            debug_mat_tmp = tmpMat
            debug_ind_tmp = np.where(debug_mat_tmp != 0)
            debug_ind_tmp = np.stack((debug_ind_tmp[0], debug_ind_tmp[1]), axis=1)

            print(debug_ind_tmp)
            print(debug_ind)
            plt.show()

            tmpMat = np.zeros((y_res, x_res))
            rotate_by = int( ((ofEvent[1] // (25000*downampling))//downampling) +1 )
            flow_mat = np.roll(flow_mat_orig, (rotate_by,rotate_by), axis=(0,1))
            ts_last = ofEvent[1]
        else:
            tmpMat[int(ofEvent[3]), int(ofEvent[2])] += 1
        # plt.pcolormesh(np.sum(flow_mat, axis=2))
        # plt.plot(int(ofEvent[2]), int(ofEvent[3]) , color='green', marker='o', markersize=1)

        plt.show()
        angular_error = calc_angular_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ])
        if  angular_error != 181:
            angular_errors.append(angular_error)
        else:
            zero_vectors += 1
        eep, rel_eep = calc_endpoint_error(ofEvent[5:7], flow_mat[int(ofEvent[3]), int(ofEvent[2]), : ]) 
        endpoint_errors.append(eep)
        if rel_eep != -1:
            relative_endpoint_errors.append(rel_eep)
    stats = "TranlationFlow statistics:\n"
    stats += "Number of valid flow vectors: " + str(num_of_vec) + " zero vectors: " + str(zero_vectors)+ "\n"
    pure_stats = ""+str(num_of_vec)+" "
    stats_list = [num_of_vec, zero_vectors]
    for name in ["average_angular", "average endpoint", "rel endpoint"]:
        if name == "average_angular":
            per1, per2, per3 = pa1, pa2, pa3
            mean, std, p1, p2, p3 = compute_statistics(np.array(angular_errors), per1, per2, per3)
        elif name == "average endpoint":
            per1, per2, per3 =  pe1, pe2, pe3
            mean, std, p1, p2, p3 = compute_statistics(np.array(endpoint_errors), per1, per2, per3)
        elif name == "rel endpoint":
            per1, per2, per3 = pre1, pre2, pre3
            mean, std, p1, p2, p3 = compute_statistics(np.array(relative_endpoint_errors), per1, per2, per3)
        else:
            print("Error not known statistic")
        stats += name+ ": mean: "+str(mean)+ " std: "+ str(std)+ " p"+str(per1)+": "+str(p1)+\
                " p"+str(per2)+": "+str(p2)+" p"+str(per3)+": "+str(p3)+"\n"
        pure_stats += str(mean) +" "+ str(std) + " " + str(per1) + " " + str(p1) + " " +\
                     str(per2) +  " " + str(p2) + " "  + str(per3) + " " + str(p3) + "\n"
        stats_list.extend([mean, std, p1, p2, p3])
    file_write_name = filename+"_translating_square_normalf_stats.txt"
    with open(file_write_name, "w") as file:
        print("going to write file to:"+ file_write_name)
        file.write(stats+pure_stats)
        print("filewritten")
        file.close()
    return stats_list




def transform_all_subdirs(startpath):
    workbook = xlsxwriter.Workbook(os.path.join(startpath, "stats.xlsx"))
    worksheet = workbook.add_worksheet()
    # write header
    first_line = ["Full", "", "", "angular error", "", "", "","","endpoint error", "", "", "","","rel endpoint", "", "", "","",]
    second_line = ["Name", "Number of OF-Vectors", "ZeroVectors", "mean", "std", "p2.5", "p10", "p30", "mean", "std", "p1", "p7.5", "p20", "mean", "std", "p0.1", "p0.3", "p0.6"]
    
    for i in range(len(first_line)):
        worksheet.write_string(0, i, first_line[i])
        worksheet.write_string(1, i, second_line[i])
    all_stats = []
    for root, dirs, files in os.walk(startpath, topdown=False):
            for file in files:
                if file.endswith(".npy") and "ofvec" in file:
                    print("File is:", file)
                    file_split = file[:-4].split("_")
                    name_of_method = file_split[0] + "_" + file_split[1]
                    zero_vectors = int( file_split[file_split.index("zeroVec") + 1] )
                    if "full" in file:
                        
                        ofVectors = np.load(os.path.join(root, file), allow_pickle = True)
                        stats = evaluateTranlationFlow(ofVectors, focallength, Z, T_x, px_size, x_res, y_res, final_file_name, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

                        #stats = evaluateRotationalFlow(ofVecs, w_z, px_size, x_res, y_res, final_file_name, radius, focallength, Z, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

                        # stats = evaluateTranslatingSquareNormalFlow(ofVectors, vGT_path, os.path.join(root, file[:-4]), pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

                        # stats = evaluateTranslatingSquareFullFlow(ofVectors, vGT_path, os.path.join(root, file[:-4]), pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)
                        
                    elif "all" in file:
                        ofVectors = np.load(os.path.join(root, file), allow_pickle = True)
                        #stats = evaluateTranlationFlow(ofVecs, focallength, Z, T_x, px_size, x_res, y_res, final_file_name, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

                        #stats = evaluateRotationalFlow(ofVecs, w_z, px_size, x_res, y_res, final_file_name, radius, focallength, Z, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

                        stats = evaluateTranslatingSquareNormalFlow(ofVectors, vGT_path, os.path.join(root, file[:-4]), pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

                        # stats = evaluateTranslatingSquareFullFlow(ofVectors, vGT_path, os.path.join(root, file[:-4]), pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)
                        # pass
                    elif "everyI" in file:
                        pass
                    elif "window" in file:
                        pass
                    else:
                        print("file:", file, " is unknown")
                    
                    stats[1] += zero_vectors
                    stats.insert(0,name_of_method)
                    all_stats.append(stats)


    # creating xlsx
    for i in range(len(all_stats)):
        stat = all_stats[i]
        for j in range(len(stat)):
            if j == 0:
                worksheet.write_string(2+i, j, stat[j])
            else:    
                worksheet.write_number(2+i, j, stat[j])
    workbook.close()




# path to file of OF-vectors
base_path = "C:\\Users\dominik\OneDrive - Technische Universität Berlin\Dokumente\degreeProject\cameraRecordings\OFRecording\\translatingSquare\\downEveryEvent"
vGT_name = "vGT_down.npy"
vGT_path = os.path.join(base_path, vGT_name)

focallength = 0.008
px_size = 1.5E-5
Z = 0.3
radius = 0.1
T_x = 0.01
rpm = 10
x_res = 320
y_res = 240
# 1 if no, 2 if yes 
downampling = 2
#percentiles
pa1, pa2, pa3 = 2.5, 10, 30
pe1, pe2, pe3 = 1, 7.5, 20
pre1, pre2, pre3 = 0.1, 0.3, 0.6

w_z = 2 * np.pi * rpm /60

transform_all_subdirs(base_path)

#call the evaluation

#evaluateTranlationFlow(ofVecs, focallength, Z, T_x, px_size, x_res, y_res, final_file_name, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

#evaluateRotationalFlow(ofVecs, w_z, px_size, x_res, y_res, final_file_name, radius, focallength, Z, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)

#evaluateTranslatingSquareNormalFlow(ofVecs, vxGT_path, vyGT_path, final_file_name, pa1, pa2, pa3, pe1, pe2, pe3, pre1, pre2, pre3)