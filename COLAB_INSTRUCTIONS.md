# Running ASR-MP on Google Colab

Use these steps to run the high-precision benchmark on free cloud resources (12GB+ RAM).

## 1. Setup Environment
Create a new notebook and run this in the first cell:

```python
# Clone the repository
!git clone https://github.com/justinarndt/qec.git
%cd qec

# Install dependencies
!pip install -r requirements.txt
```

## 2. Run the Benchmark
Run the stress test. You can use default workers (`-w 4`) on Colab.

```python
# Run d=5 and d=7 (Safe start, 4 workers ok)
!python scripts/benchmark_stress.py -d 5 7 -s 5000 --drift 0.3

# OR Run the full suite with HIGH DISTANCE (d=15)
# CAUTION: d=15 uses ~12GB RAM per worker. 
# Use -w 2 (or -w 1) to avoid crashing the 50GB RAM limit.
!python scripts/benchmark_stress.py -s 5000 -w 2
```

## 3. Visualize Results
```python
import pandas as pd
df = pd.read_csv('stress_benchmark.csv')
print(df)

# Or generate plots
!python scripts/generate_plots.py -i stress_benchmark.csv
```
