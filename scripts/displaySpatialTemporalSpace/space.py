import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
path = r"C:\Users\dominik\OneDrive - Technische Universität Berlin\Dokumente\degreeProject\cameraRecordings\OFRecording - fixed complex\roatatingDisk\10.08rpm\run1\log_td.dat.npy"
num_of_events = 100000
every_i = 750
num_of_events = num_of_events* every_i

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

a = np.load(path, allow_pickle=True)

xs = a[:num_of_events:every_i, 2]
ys = a[:num_of_events:every_i, 0]
zs = a[:num_of_events:every_i, 1]

c = np.linspace(0, 13, xs.shape[0])
cmap = cm.jet
ax.scatter(xs, ys, zs, marker="o", s=2, c=c, cmap=cmap)
ax.set_xlabel('ts')
ax.set_ylabel('X')
ax.set_zlabel('Y')

plt.show()