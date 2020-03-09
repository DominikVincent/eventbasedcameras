#about twice as fast compared to slow


# run with python fast.py file1.csv
# or
# run with python fast.py file1.csv file2.csv


import sys;
import csv;
import numpy as np;


#only timer
print('started');
import time;
start_time = time.time();


# this is the data later
data_array = []; # = np.empty(len(sys.argv), dtype='int32');

i = 0;

for arg in sys.argv[1:]:
    dest_file = arg
    delimit = ','
    with open(dest_file,'r') as dest_f:
        data_iter = csv.reader(dest_f,
                            delimiter = delimit,
                            quotechar = '"')
        data = [data for data in data_iter];

    data_array.append(np.asarray(data, dtype = 'int32'));
    i = i + 1;
    #end timer
    print("--- %s seconds ---" % (time.time() - start_time));


print("done ");
