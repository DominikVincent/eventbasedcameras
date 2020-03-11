from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
from scipy.stats import norm
import numpy as np


random_state = np.random.RandomState(seed=1)

X = np.concatenate([random_state.normal(-1, 1.5, 350),
                    random_state.normal(0, 1, 500),
                    random_state.normal(3, 0.5, 150)]).reshape(-1, 1)
X = np.sort(X, axis=0)
print(X)

plt.plot(X)
plt.show()
x = np.linspace(0, 100, 1000)


data = np.zeros_like(x)
data += data +norm.pdf(x,50,5)*100

#data += data + norm.pdf(x,50,10)*200
plt.plot(x, data)
plt.show()
newdata = []

for i in range(len(data)):
    newdata +=[i*100/1000]*int(data[i])

newdata = np.asarray(newdata).reshape(-1,1)
#print(data.reshape(-1,1))

plt.plot(newdata)
plt.show()
gaussModel = GaussianMixture(1,  covariance_type = "full")
gaussModel2 = GaussianMixture(3, covariance_type = "full")

#print(data.reshape(-1,1).shape)
gaussModel.fit(newdata)
gaussModel2.fit(X)
print("their cov: ", gaussModel2.covariances_)
print("their mean: ", gaussModel2.means_)
print(gaussModel.converged_)
print("our means: ",gaussModel.means_)
print("our cov:", gaussModel.covariances_)

x= np.linspace(0, 100, 100)
logprob = gaussModel.score_samples(x.reshape(-1, 1))
pdf = np.exp(logprob)
plt.plot(x, pdf)
plt.show()

for (mean, covariance) in zip(gaussModel.means_, gaussModel.covariances_):
    print(norm.pdf(x,mean,covariance))
    plt.plot(x, norm.pdf(x,mean,covariance).reshape(1000), color="c")

#plt.plot(x, data)
plt.show()