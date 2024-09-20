import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm

def convert_to_float(s):
    s = str(s)
    if s.endswith('K') or s.endswith("%"):
        return float(s[:-1])  # 去除末尾的K并将其转换为整数
    else:
        return float(s)


# 读取CSV文件
df1 = pd.read_csv('PPI MoM_core.csv')
df2 = pd.read_csv('Core Inflation Rate YoY_core.csv')
df1 = df1.dropna()
df2 = df2.dropna()

# 计算差值
df1['NonFarmPayrolls_diff'] = df1['Consensus'].apply(convert_to_float) - df1['Current'].apply(convert_to_float)
df2['CoreInflationRate_diff'] = df2['Consensus'].apply(convert_to_float) - df2['Current'].apply(convert_to_float)
print(df1)
print(df2)
# 绘制图表
plt.scatter(df1['Current'][1:26], df2['Current'][14:39], label='Data', color='blue', marker='o')

plt.xlabel('NonFarmPayrolls Difference')
plt.ylabel('CoreInflationRate Difference')
plt.title('Difference between Consensus and Current')
plt.show()
