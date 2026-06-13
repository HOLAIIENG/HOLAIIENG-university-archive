import numpy as np
import matplotlib.pyplot as plt

# 输入电压范围
vIN_cutoff = 0.6    # 截止区临界
vIN_sat_end = -0.351# 饱和区临界
vIN = np.linspace(-2, 2, 1000)
vOUT = np.zeros_like(vIN)

# 分段计算输出
# 截止区
mask_cutoff = vIN > vIN_cutoff
vOUT[mask_cutoff] = 10

# 饱和区
mask_sat = (vIN >= vIN_sat_end) & (vIN <= vIN_cutoff)
vIN_sat = vIN[mask_sat]
vOUT[mask_sat] = 10 - 10 * (0.6 - vIN_sat)**2

# 非饱和区
mask_non_sat = vIN < vIN_sat_end
vIN_non = vIN[mask_non_sat]
delta = 400 * vIN_non**2 - 520 * vIN_non - 231
ID = (187 + 20*vIN_non - np.sqrt(delta)) / 400
vOUT[mask_non_sat] = 10 - 20 * ID

# 绘图
plt.figure(figsize=(10,6))
plt.plot(vIN, vOUT, 'b-', linewidth=2)
# 标注工作区
plt.axvspan(vIN_cutoff, 2, color='gray', alpha=0.2, label='截止区')
plt.axvspan(vIN_sat_end, vIN_cutoff, color='green', alpha=0.2, label='饱和区')
plt.axvspan(-2, vIN_sat_end, color='orange', alpha=0.2, label='非饱和区(三极管区)')
# 临界线
plt.axvline(x=vIN_cutoff, color='r', linestyle='--')
plt.axvline(x=vIN_sat_end, color='r', linestyle='--')

plt.xlabel('输入电压 vIN (V)')
plt.ylabel('输出电压 vOUT (V)')
plt.title('MOS分压偏置放大器传递特性')
plt.legend()
plt.grid(True)
plt.show()