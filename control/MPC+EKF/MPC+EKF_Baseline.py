
import casadi as ca
import numpy as np
import matplotlib.pyplot as plt
from casadi.tools import *

# --- Parameter & Modell ---
p = {
    'Ra': 12.345, 'La': 0.314,
    'km': 0.253, 'J': 0.00441,
    'B': 0.00732, 'ua': 60.0,
    'tl_true': 1.47,
    'dt': 0.01
}

nx = 2; nu = 1
x_sym = ca.MX.sym('x', nx)
u_sym = ca.MX.sym('u')

dia_dt = (-p['Ra']/p['La'])*x_sym[0] - (p['km']/p['La'])*x_sym[1]*u_sym + p['ua']/p['La']
domega_dt = (-p['B']/p['J'])*x_sym[1] + (p['km']/p['J'])*x_sym[0]*u_sym - p['tl_true']/p['J']
f_cont = ca.vertcat(dia_dt, domega_dt)
f_ode = ca.Function('f_ode', [x_sym, u_sym], [f_cont])

dt = p["dt"]
k1 = f_ode(x_sym, u_sym)
k2 = f_ode(x_sym + dt/2 * k1, u_sym)
k3 = f_ode(x_sym + dt/2 * k2, u_sym)
k4 = f_ode(x_sym + dt * k3, u_sym)
x_next = x_sym + dt/6*(k1+2*k2+2*k3+k4)

f_disc = ca.Function('f_disc', [x_sym,u_sym],[x_next])
jac_f   = ca.Function('jac_f',[x_sym,u_sym],[ca.jacobian(x_next,x_sym)])

# --- EKF Parameter ---
Q_proc   = np.diag([5e-3 ,50])   # Process Noise
R_meas   = 4                     # Measurement Noise
H        = np.array([[0.,1.]])   # Only measuring omega

def ekf_step(x_est,u,y,P):
    x_pred=np.array(f_disc(x_est,u)).flatten()
    Phi=np.array(jac_f(x_est,u))
    P_pred=Phi@P@Phi.T+Q_proc
    S=H@P_pred@H.T+R_meas
    K=P_pred@H.T@np.linalg.inv(S)
    resid=y-x_pred[1]
    x_upd=x_pred+(K.flatten()*resid)
    P_upd=(np.eye(nx)-K@H)@P_pred
    return x_upd,P_upd,K,resid

# --- Prepare MPC Solver ---
N = 50                # Predicition Horizon
omega_setpoint = -175.0
tracking_weight = 2000.0
control_weight  = 0.01

opt_x = struct_symSX([
    entry('x', shape=nx, repeat=[N+1]),
    entry('u', shape=nu, repeat=[N])
])

lb_opt_x = opt_x(-ca.inf)
ub_opt_x = opt_x(ca.inf)

lb_opt_x['x', :, 0], ub_opt_x['x', :, 0] = -10., 10.
lb_opt_x['x', :, 1], ub_opt_x['x', :, 1] = -200., 35.
lb_opt_x['u'], ub_opt_x['u']              = -10., 10.

J   = 0
g   = []
lbg = []
ubg = []

# Parameter for initial conditions
x_init_param = ca.SX.sym("xin", nx)
g.append(opt_x["x", 0] - x_init_param)
lbg.append([0, 0])
ubg.append([0, 0])

# Dynamics and cost
for i in range(N):
    # cost function
    J += tracking_weight*(opt_x["x", i][1] - omega_setpoint)**2 \
         + control_weight*(opt_x["u", i])**2
    
    # System dynamics
    x_next_pred = f_disc(opt_x["x", i], opt_x["u", i])
    g.append(opt_x["x", i+1] - x_next_pred)
    lbg.append([0, 0])
    ubg.append([0, 0])

prob   = {'f': J,
          'x': opt_x,
          'g': ca.vertcat(*g),
          'p': x_init_param}

solver_opts={'ipopt.print_level':0,'print_time':False}
solver=ca.nlpsol("solver","ipopt",prob,solver_opts)

# Initial warm start:
x_guess=opt_x(np.zeros(opt_x.shape))

# ============================================================
# SIMULATION WITH NOISE AND EKF ESTIMATION
# ============================================================

T_sim=2.; steps=int(T_sim/p["dt"])
curr_true=np.array([0.,0.])
curr_est=np.array([0.,0.])
curr_u=float(0.)
P=np.eye(nx)

hist_true=[]; hist_est=[]; hist_y=[]; hist_u=[]
print(f"Simuliting MPC+EKF with ω_set={omega_setpoint} ...")

for k in range(steps):

    # --- Simulate plant with noise ---
    w=np.random.multivariate_normal(np.zeros(nx), Q_proc)
    curr_true=np.array(f_disc(curr_true,curr_u)).flatten()+w

    # --- Measurement with noise ---
    v=np.random.normal(0,np.sqrt(R_meas))
    y_meas=float(curr_true[1]+v)

    # --- EKF-Step ---
    curr_est,P,K,resid_=ekf_step(curr_est,curr_u,y_meas,P)

    # --- MPC-Step with estimated state ---
    sol = solver(
        p=curr_est,
        lbx=lb_opt_x,
        ubx=ub_opt_x,
        lbg=0,
        ubg=0,
        x0=x_guess
        )

    opt_val = opt_x(sol['x'])
    curr_u = float(opt_val['u', 0])
    x_guess = sol['x']
    
    ## Saving:
    hist_true.append(curr_true.copy())
    hist_est.append(curr_est.copy())
    hist_y.append(y_meas);hist_u.append(curr_u)


true_arr=np.asarray(hist_true); est_arr=np.asarray(hist_est); y_arr=np.asarray(hist_y)

plt.figure(figsize=(10,5))
plt.subplot(211)
plt.plot(true_arr[:,1],'b-',label='True ω')
plt.plot(est_arr[:,1],'r--',label='EKF ω̂')
plt.scatter(range(len(y_arr)),y_arr,s=20,color='green',alpha=0.3,label='Measured ω')
plt.axhline(omega_setpoint,color='black',ls='--')
plt.legend(); plt.grid(True); plt.ylabel("Angular Velocity [rad/s]")

plt.subplot(212)
plt.step(range(len(hist_u)),hist_u,label="Control input u")
plt.grid(True); plt.xlabel("Time step"); plt.ylabel("Control signal")
plt.tight_layout()


plt.show()