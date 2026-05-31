# Control Systems — Project Overview

This folder contains two closed-loop motor control implementations, both built around a **DC motor model** and combining Model Predictive Control (MPC) with an Extended Kalman Filter (EKF). The two scripts represent a progression: a clean baseline followed by a more advanced version that handles unknown disturbances.

---

## Scripts

### 1. `MPC+EKF/MPC_EKF_Baseline.py` — Baseline controller
The starting point. A 2-state model (armature current *iₐ*, angular velocity *ω*) where the load torque is a known constant. The EKF is used purely for noise filtering — it cleans up the noisy ω measurement before handing the state to the MPC.

**Good for:** understanding the core MPC + EKF loop before adding complexity.

### 2. `MPC+EKF/MPC-EKF_Estimating_Torque.py` — Extended controller with torque estimation
Builds on the baseline by augmenting the state vector with load torque *τₗ* as a third unknown state. The EKF now does two jobs simultaneously: filters noise **and** estimates the torque online, starting from an incorrect initial guess. Also runs a side-by-side comparison of MPC performance with and without EKF feedback.

**Good for:** seeing how state augmentation handles real-world unknowns without a separate observer.

---

## How They Relate

```
MPC+EKF/MPC_EKF_Baseline.py
    └── 2-state model, τₗ known
    └── EKF: noise filtering only
    └── Single simulation run

MPC+EKF/MPC-EKF_Estimating_Torque.py
    └── 3-state model, τₗ estimated
    └── EKF: noise filtering + disturbance estimation
    └── Comparative simulation (with EKF vs without)
```

---

## Shared Architecture

Both scripts follow the same pipeline:

```
Plant (true state + noise)
    → Measurement (ω only, noisy)
        → EKF (state estimate)
            → MPC (optimal control input)
                → Plant
```

- Dynamics discretised with **RK4** via CasADi symbolic differentiation
- MPC solved as a **nonlinear program** using IPOPT
- Only angular velocity ω is measured — current sensing is omitted deliberately

---

## Dependencies

```bash
cd MPC+EKF
pip install -r requirements.txt
```

---

## Run Order

Run the baseline first to validate the core loop, then the extended version to see torque estimation in action.

```bash
cd MPC+EKF
python MPC_EKF_Baseline.py
python MPC-EKF_Estimating_Torque.py
```

---

*University team project — Control Systems / Mechatronics, 2026*
