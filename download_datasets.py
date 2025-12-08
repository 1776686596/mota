"""下载测试数据集到 data 目录"""

import pandas as pd
import numpy as np
from pathlib import Path

# 创建 data 目录
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

print("开始下载/生成数据集...")

# 1. Iris 数据集（从 seaborn 数据源）
try:
    print("\n下载 iris.csv...")
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
    iris = pd.read_csv(url)
    iris.to_csv(data_dir / "iris.csv", index=False)
    print(f"✅ iris.csv 已保存 ({len(iris)} 行)")
except Exception as e:
    print(f"❌ iris.csv 下载失败: {e}")

# 2. Tips 数据集
try:
    print("\n下载 tips.csv...")
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
    tips = pd.read_csv(url)
    tips.to_csv(data_dir / "tips.csv", index=False)
    print(f"✅ tips.csv 已保存 ({len(tips)} 行)")
except Exception as e:
    print(f"❌ tips.csv 下载失败: {e}")

# 3. Diamonds 数据集（精简版，完整版太大）
try:
    print("\n下载 diamonds.csv...")
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv"
    diamonds = pd.read_csv(url)
    # 只保留前 10000 行以减小文件大小
    diamonds_sample = diamonds.head(10000)
    diamonds_sample.to_csv(data_dir / "diamonds.csv", index=False)
    print(f"✅ diamonds.csv 已保存 ({len(diamonds_sample)} 行，精简版)")
except Exception as e:
    print(f"❌ diamonds.csv 下载失败: {e}")

# 4. 生成科研相关数据集

# 4.1 细胞活力测试数据
print("\n生成 cell_viability.csv...")
np.random.seed(42)
treatments = ['Control', 'Drug_A', 'Drug_B', 'Drug_C'] * 30
concentrations = np.repeat([0, 10, 50, 100, 500], 24)
viability = []
for t, c in zip(treatments, concentrations):
    if t == 'Control':
        base = 100
    elif t == 'Drug_A':
        base = max(100 - c * 0.15, 20)
    elif t == 'Drug_B':
        base = max(100 - c * 0.10, 30)
    else:  # Drug_C
        base = max(100 - c * 0.20, 15)
    viability.append(base + np.random.normal(0, 5))

cell_data = pd.DataFrame({
    'Treatment': treatments,
    'Concentration_uM': concentrations,
    'Viability_%': viability,
    'Batch': np.random.choice(['Batch1', 'Batch2', 'Batch3'], 120),
    'Time_h': np.repeat([24, 48, 72], 40)
})
cell_data.to_csv(data_dir / "cell_viability.csv", index=False)
print(f"✅ cell_viability.csv 已保存 ({len(cell_data)} 行)")

# 4.2 酶活性分析数据
print("\n生成 enzyme_activity.csv...")
np.random.seed(43)
enzyme_types = ['Wild_Type', 'Mutant_A', 'Mutant_B'] * 40
temperatures = np.tile(np.arange(20, 80, 5), 10)
activities = []
for enz, temp in zip(enzyme_types, temperatures):
    if enz == 'Wild_Type':
        optimal = 37
        max_act = 100
    elif enz == 'Mutant_A':
        optimal = 45
        max_act = 120
    else:  # Mutant_B
        optimal = 30
        max_act = 80
    
    # 高斯型活性曲线
    act = max_act * np.exp(-0.01 * (temp - optimal)**2)
    activities.append(act + np.random.normal(0, 5))

enzyme_data = pd.DataFrame({
    'Enzyme': enzyme_types,
    'Temperature_C': temperatures,
    'Activity_U/mL': activities,
    'pH': np.random.choice([6.0, 6.5, 7.0, 7.5, 8.0], 120),
    'Substrate_mM': np.random.choice([1, 5, 10, 20], 120)
})
enzyme_data.to_csv(data_dir / "enzyme_activity.csv", index=False)
print(f"✅ enzyme_activity.csv 已保存 ({len(enzyme_data)} 行)")

# 4.3 材料测试数据
print("\n生成 material_test.csv...")
np.random.seed(44)
materials = ['Steel_A', 'Steel_B', 'Alloy_X', 'Alloy_Y'] * 25
strains = np.linspace(0, 0.05, 100)
stresses = []
for mat, strain in zip(materials, strains):
    if mat == 'Steel_A':
        E = 200000  # MPa
        yield_stress = 400
    elif mat == 'Steel_B':
        E = 210000
        yield_stress = 500
    elif mat == 'Alloy_X':
        E = 70000
        yield_stress = 300
    else:  # Alloy_Y
        E = 80000
        yield_stress = 350
    
    # 弹性-塑性曲线
    if strain < yield_stress / E:
        stress = E * strain
    else:
        stress = yield_stress + 1000 * (strain - yield_stress / E)
    
    stresses.append(stress + np.random.normal(0, 10))

material_data = pd.DataFrame({
    'Material': materials,
    'Strain': strains,
    'Stress_MPa': stresses,
    'Temperature_C': np.random.choice([25, 100, 200], 100),
    'Test_ID': [f'T{i:03d}' for i in range(100)]
})
material_data.to_csv(data_dir / "material_test.csv", index=False)
print(f"✅ material_test.csv 已保存 ({len(material_data)} 行)")

# 4.4 XRD 分析数据
print("\n生成 xrd_analysis.csv...")
np.random.seed(45)
two_theta = np.linspace(10, 80, 700)
samples = ['Sample_A', 'Sample_B', 'Sample_C']
xrd_data_list = []

for sample in samples:
    if sample == 'Sample_A':
        peaks = [28.4, 40.3, 50.1, 58.6]
        intensities = [1000, 600, 400, 300]
    elif sample == 'Sample_B':
        peaks = [25.3, 37.8, 48.5]
        intensities = [1200, 700, 500]
    else:  # Sample_C
        peaks = [30.2, 43.5, 53.8, 62.9]
        intensities = [900, 550, 350, 250]
    
    intensity = np.ones_like(two_theta) * 50  # 背景
    for peak, peak_int in zip(peaks, intensities):
        intensity += peak_int * np.exp(-0.5 * ((two_theta - peak) / 0.5)**2)
    
    intensity += np.random.normal(0, 20, len(two_theta))
    
    for tt, inten in zip(two_theta, intensity):
        xrd_data_list.append({
            'Sample': sample,
            '2Theta_deg': tt,
            'Intensity': max(0, inten),
            'Wavelength_A': 1.5406,  # Cu Kα
            'Scan_Speed_deg/min': 2.0
        })

xrd_data = pd.DataFrame(xrd_data_list)
xrd_data.to_csv(data_dir / "xrd_analysis.csv", index=False)
print(f"✅ xrd_analysis.csv 已保存 ({len(xrd_data)} 行)")

print("\n" + "="*50)
print("所有数据集已成功生成！")
print(f"数据保存在 {data_dir.absolute()} 目录下")
print("\n数据集列表：")
for csv_file in sorted(data_dir.glob("*.csv")):
    size = csv_file.stat().st_size / 1024
    print(f"  - {csv_file.name} ({size:.1f} KB)")