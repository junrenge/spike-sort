import numpy

from utils.detect_peakes import detect_peaks

#peak的最小值，>=mph就会被检测出来
arr = [1,2,3,2,1]
peak_index_arr = detect_peaks(arr, mph=3, mpd=5, show=True)
arr = [1,3,2,4,1]
peak_index_arr = detect_peaks(arr, mph=3, mpd=5, show=True)
arr = [1,2,1,1,1]
peak_index_arr = detect_peaks(arr, mph=2, mpd=5, show=True)
