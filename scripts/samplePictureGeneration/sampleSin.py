import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# y
y = 7016 
x = 9933 

x_sin = np.sin(np.linspace(0, 16 * np.pi, x))
full = np.full((y,x), x_sin)


# plt.imshow(full)
# plt.show()

im = Image.fromarray((full+1.0)*255/2)
im = im.convert('RGB')
im.show()
im.save("scripts/samplePictureGeneration/sin16pi.jpeg", "JPEG")