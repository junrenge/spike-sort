#coding=utf-8
import numpy as np
from scipy import signal
from sklearn.decomposition import PCA
from matplotlib import pyplot as pl
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import DBSCAN,KMeans
import pandas as pd

from utils.detect_peakes import detect_peaks

raw_signal=[]
with open('1ch.txt', 'r') as f1:
    test_data = f1.read(40000)
    arr = test_data.split(',')[:-1]
    for i in range(len(arr)):
        raw_signal.append(np.float32(arr[i]))
raw_signal=np.array(raw_signal)
# pl.plot(raw_signal)
#滤除10hz以下和400hz以上频率成分
b, a = signal.butter(8, [0.06,0.6], 'bandpass')
filtedData = signal.filtfilt(b, a, raw_signal)   #data为要过滤的信号
####
test = filtedData[404 - 3:404 + 2]
my_index=detect_peaks(test, mph=3, mpd=50, show=False)
print(my_index)
print(test[my_index])
print(filtedData[404])
####


# pl.plot(filtedData)
# pl.show()
peak_index=detect_peaks(filtedData, mph=3, mpd=50, show=False)
# print(peak_index,filtedData[peak_index])
# print(len(peak_index))

waveforms = []
w=pl.subplot(512)
for ind in peak_index:
    wave=filtedData[ind-20:ind+30]
    # print(wave)
    w.plot(wave)
    waveforms.append(wave)

#降维完成
pca=PCA(n_components=3)
dim_redu_waveforms=pca.fit_transform(waveforms)
# print(dim_redu_waveforms)

ax=pl.subplot(511,projection='3d')
ax.scatter(dim_redu_waveforms[:,0],dim_redu_waveforms[:,1],dim_redu_waveforms[:,2])#


#聚类
y_pred = KMeans(n_clusters=2).fit_predict(dim_redu_waveforms)
# y_pred = DBSCAN(eps = 0.0001,min_samples = 10).fit_predict(dim_redu_waveforms)
cluster_ax=pl.subplot(513,projection='3d')
cluster_ax.scatter(dim_redu_waveforms[:,0],dim_redu_waveforms[:,1],dim_redu_waveforms[:,2], c=y_pred)#
# pl.show()

#得到每个waveform的类别,并画出
color=['red','green','yellow']
clustered_w=pl.subplot(514)

for ind in range(len(peak_index)):
    clustered_w.plot(waveforms[ind],c=color[y_pred[ind]])
# pl.show()

#计算每一类waveform的模板：
#将waveforms和y_pred进行列拼接
n, m = np.shape(waveforms)
concat = np.zeros([n, m+1])
concat[:, : m] = waveforms
concat[:, -1] = y_pred
# print(np.shape(concat))

df=pd.DataFrame(concat)

templates=df.groupby(df[50]).mean()
# print(templates.values[0])
# print(templates.ix[0])
# for temp in templates.values:
#     print(temp)

template_w=pl.subplot(515)
for i in range(len(templates.values)):
    template_w.plot(templates.values[i],c=color[i])
# pl.show()

#匹配模板
#用检测到的peak去匹配template，检测到后和模板画在一起
from scipy import spatial
thresh_hold = 0.9
result_arr = []
print(len(result_arr))
for i in range(len(waveforms)):
    for j in range(len(templates.values)):
        result = 1 - spatial.distance.cosine(templates.values[j], waveforms[i])
        if result > thresh_hold:
            result_arr.append(j)

print(result_arr)


