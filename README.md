# **Adaptive Soft-Reliability Message Passing (ASR-MP) Kernel**

**Version:** 1.0.0-alpha **Status:** Strategic Research Prototype / Pre-RTL Validation **Target Architecture:** Riverlane Deltaflow (FPGA / QECi)

## **1\. Overview**

The **Adaptive Soft-Reliability Message Passing (ASR-MP)** kernel is a high-precision quantum error correction decoder designed to bridge the gap between "MegaQuOp" and "Tera-Quop" fault tolerance. Unlike static decoders (MWPM, LCD) that rely on fixed graph approximations, ASR-MP utilizes **Belief Propagation (BP)** with **Ordered Statistics Decoding (OSD)** to perform dynamic, soft-decision inference.  
This repository contains the benchmarking suite and Python decoding kernel verifying ASR-MP's performance on Rotated Surface Codes under hostile, drift-heavy noise conditions.

### **Strategic Capabilities**

* **Software-Defined Fidelity:** Achieves a **2x reduction in logical error rates** at d=3 compared to MWPM.  
* **Drift Resilience:** Maintains exponential error suppression under \pm 30\% control parameter drift, where static decoders fail.  
* **Hardware Compatibility:** Algorithm structure is O(N) parallelizable, targeting sub-1 \mu s latency on Deltaflow FPGA architectures via systolic array synthesis.

## **2\. Technical Architecture**

### **2.1 The Kernel**

The decoder wraps the optimized ldpc (v2.4.1) library, implementing a custom fault-tolerant configuration:

* **Algorithm:** Sum-Product Belief Propagation with OSD Post-Processing.  
* **BP Method:** product_sum (Exact arithmetic for handling high-degeneracy quantum codes).  
* **OSD Configuration:**  
  * **Offline Mode:** osd_order=35 (Deep Search) for establishing theoretical code capacity limits.  
  * **Online Mode:** osd_method="osd_cs" (Combination Sweep) for latency-constrained real-time decoding.  
* **Input:** Soft-decision Log-Likelihood Ratios (LLRs) or Hard Syndromes.

### **2.2 Precision Baseline (Standard Noise)**

Under standard circuit-level depolarizing noise, ASR-MP demonstrates its raw correction power.

| Metric | MWPM (Baseline) | ASR-MP (Kernel) | Improvement |
| :---- | :---- | :---- | :---- |
| **Logical Error (d=3)** | 2.1 \times 10^{-3} | 1.0 \times 10^{-3} | **2.1x Reduction** |
| **Logical Error (d=5)** | 1.2 \times 10^{-4} | < 1.0 \times 10^{-5} | **>10x (Noise Floor)** |

### **2.3 Stress Test (Drift & Burst)**

The following benchmarks simulate the "hostile" environment of a real quantum processor, including time-varying noise drift and correlated burst events (Drift +/- 30%, Burst=0.05).

| Metric | MWPM (Baseline) | ASR-MP (Kernel) | Improvement |
| :---- | :---- | :---- | :---- |
| **Drift Sensitivity** | High (Threshold Collapse) | Low (Adaptive) | **Stable Operation** |

*(Data derived from notebooks/qec4dv2.ipynb using stim circuit simulation)*

## **3\. Repository Structure**

```
riverlane-asr-mp/
├── README.md               # This documentation
├── assets/
│   ├── performance_plot.png
│   └── architecture_diagram.svg
├── notebooks/
│   └── qec4dv2.ipynb       # Core benchmarking logic (High-Stress Mode)
├── src/
│   ├── decoder.py          # ASR-MP class wrapping ldpc.bp_osd
│   └── noise_models.py     # Drift and Burst noise generators (stim)
├── scripts/
│   ├── benchmark_standard.py
│   └── benchmark_stress.py
├── requirements.txt        # Dependencies (stim, sinter, ldpc, pymatching)
└── LICENSE                 # Proprietary / Internal
```

## **4\. Installation & Usage**

### **Prerequisites**

* Python 3.10+  
* stim (Circuit simulation)  
* sinter (Monte Carlo sampling)  
* ldpc v2+ (Decoding kernel)

### **Quick Start**

```bash
# Clone the repository
git clone https://github.com/riverlane-internal/asr-mp-decoder.git
cd asr-mp-decoder

# Install dependencies
pip install -r requirements.txt

# Run the Precision Baseline (Standard Noise)
python scripts/benchmark_standard.py -d 3 5 -p 0.001

# Run the Drift Resilience Benchmark (Stress Test)
python scripts/benchmark_stress.py --distance 5 --drift 0.3 --burst 0.05
```

## **5\. Hardware Integration Path**

This kernel is the software precursor to a hardware-accelerated IP block for **Deltaflow**.

* **Latency Target:** < 1 \mu s per round.  
* **Synthesis Strategy:** The BP message-passing stage is mapped to **FPGA systolic arrays** (e.g., Xilinx Zynq UltraScale+). Recent literature confirms BP iteration times of ~24ns on this architecture.  
* **Interface:** Designed to consume **QECi** soft-readout payloads.

## **6\. Citation**

**Arndt, J. (2026).** *Adaptive Soft-Reliability Message Passing (ASR-MP) for Drift-Resilient Quantum Error Correction.* Riverlane Internal Technical Report RL-2026-002.
