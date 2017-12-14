import numpy as np
import os

BASE_DIR = os.path.abspath(os.path.realpath('.'))

base_result = np.loadtxt(BASE_DIR + '/2017-12-14.csv', delimiter=',')
# 删除第一列
result = np.delete(base_result, 0, axis=1)
print(result[:, 0].sum()/1730)
print(result[:, 1].sum()/1730)
print(result[:, 2].sum()/1730)
