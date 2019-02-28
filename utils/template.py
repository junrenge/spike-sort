# -*- coding: utf-8 -*-
import traceback
import numpy as np
from scipy import spatial
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import pandas as pd

class template():
    def __init__(self):
        pass

    def getTemplateByKMeans(waveforms, length):
        pca = PCA(n_components=3)
        dim_redu_waveforms = pca.fit_transform(waveforms)
        y_pred = KMeans(n_clusters=3).fit_predict(dim_redu_waveforms)
        n, m = np.shape(waveforms)
        concat = np.zeros([n, m + 1])
        concat[:, : m] = waveforms
        concat[:, -1] = y_pred
        df = pd.DataFrame(concat)
        templates = df.groupby(df[length]).mean()
        return templates.values