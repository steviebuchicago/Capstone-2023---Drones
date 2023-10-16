import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Generate some sample data
data = [x + 3 * x % 5 for x in range(100)]
series = pd.Series(data)

# Calculate a moving average for Z-axis
moving_avg = series.rolling(window=5).mean().fillna(method='bfill')

# 3D Plot
fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(111, projection='3d')

# Data for 3D plot
x = series.index
y = series.values
z = moving_avg.values

ax.plot(x, y, z, label='Time Series with Moving Avg', color='b')
ax.set_xlabel('Time')
ax.set_ylabel('Original Values')
ax.set_zlabel('Moving Average')
ax.set_title('3D Visualization of Time Series')
ax.legend()

plt.show()

# Fit ARIMA model (p=1, d=1, q=1)
model = ARIMA(series, order=(1,1,1))
model_fit = model.fit()

# Summary
print(model_fit.summary())
