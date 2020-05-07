import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# y
y = 7016 
x = 9933 
full = np.zeros((7016,int(9933/2)))
block = 16

for i in range(block):
    full[:, int(i*x/2 / block): int((i+1)*x/2/block)] = 1 - 1/block * i

full_flip = np.flip(full, axis=1)


full = np.hstack((full, full_flip))


plt.imshow(full)
plt.show()

im = Image.fromarray((full)*255)
im = im.convert('RGB')
im.show()
im.save("scripts/samplePictureGeneration/16blocks.jpeg", "JPEG")