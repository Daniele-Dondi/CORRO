##import numpy as np
##from scipy.integrate import solve_ivp
##import matplotlib.pyplot as plt
##
### Constants
##R = 8.314  # J/mol·K
##
### Thermokinetic ODE system
##def thermokinetic_model(t, y, deltaG_rxn, A_f, Ea_f, A_r=None, Ea_r=None, T=298.15, catalyst_factor=1.0):
##    A, B, C = y
##
##    # Forward rate constant with catalyst effect
##    kf = A_f * catalyst_factor * np.exp(-Ea_f / (R * T))
##
##    # Thermodynamically consistent reverse rate
##    if A_r is not None and Ea_r is not None:
##        kr = A_r * catalyst_factor * np.exp(-Ea_r / (R * T))
##    else:
##        K_eq = np.exp(-deltaG_rxn / (R * T))
##        kr = kf / K_eq
##
##    # Net reaction rate
##    rate_forward = kf * A * B
##    rate_reverse = kr * C
##    rate_net = rate_forward - rate_reverse
##
##    # ODEs
##    dA_dt = -rate_net
##    dB_dt = -rate_net
##    dC_dt = rate_net
##    return [dA_dt, dB_dt, dC_dt]
##
### Simulation wrapper
##def simulate_thermokinetics(
##    A0, B0, C0,
##    deltaG_rxn, A_f, Ea_f,
##    A_r=None, Ea_r=None,
##    T=298.15, catalyst_factor=1.0,
##    t_final=1000, num_points=200
##):
##    y0 = [A0, B0, C0]
##    t_eval = np.linspace(0, t_final, num_points)
##    sol = solve_ivp(
##        thermokinetic_model,
##        (0, t_final),
##        y0,
##        args=(deltaG_rxn, A_f, Ea_f, A_r, Ea_r, T, catalyst_factor),
##        t_eval=t_eval,
##        method='LSODA'
##    )
##    return sol.t, sol.y
##
### Example parameters
##params = {
##    'A0': 1.0,      # mol/L
##    'B0': 1.0,      # mol/L
##    'C0': 0.0,      # mol/L
##    'deltaG_rxn': -5000,  # J/mol
##    'A_f': 1e6,     # 1/(mol·s)
##    'Ea_f': 40000,  # J/mol
##    'T': 310.0,     # K
##    'catalyst_factor': 2.0,
##    't_final': 2000
##}
##
### Run simulation
##t, (A, B, C) = simulate_thermokinetics(**params)
##
### Plot results
##plt.plot(t, A, label='[A]')
##plt.plot(t, B, label='[B]')
##plt.plot(t, C, label='[C]')
##plt.xlabel('Time (s)')
##plt.ylabel('Concentration (mol/L)')
##plt.title('Thermokinetic Simulation')
##plt.legend()
##plt.grid(True)
##plt.tight_layout()
##plt.show()


import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

R = 8.314  # J/mol·K

# Thermokinetic model with catalyst and solvent corrections
def thermokinetic_model(t, y, deltaG_rxn, A_f, Ea_f, T, delta_Ea_cat=0, f_cat=1.0, deltaG_solv=0):
    A, B, C = y

    # Corrected parameters
    Ea_eff = Ea_f - delta_Ea_cat
    A_eff = A_f * f_cat
    deltaG_eff = deltaG_rxn + deltaG_solv

    # Rate constants
    kf = A_eff * np.exp(-Ea_eff / (R * T))
    K_eq = np.exp(-deltaG_eff / (R * T))
    kr = kf / K_eq

    rate = kf * A * B - kr * C
    return [-rate, -rate, rate]

# Simulate [C] at a fixed time
def simulate_C_at_t(A0, B0, C0, deltaG_rxn, A_f, Ea_f, T, t_exp, delta_Ea_cat=0, f_cat=1.0, deltaG_solv=0):
    y0 = [A0, B0, C0]
    sol = solve_ivp(
        thermokinetic_model,
        (0, t_exp),
        y0,
        args=(deltaG_rxn, A_f, Ea_f, T, delta_Ea_cat, f_cat, deltaG_solv),
        t_eval=[t_exp],
        method='LSODA'
    )
    return sol.y[2][0]  # [C] at t_exp

# Cost function for fitting
def cost(params, A0, B0, C0, deltaG_rxn, T, t_exp, C_exp):
    A_f, Ea_f, delta_Ea_cat, f_cat, deltaG_solv = params
    C_sim = simulate_C_at_t(A0, B0, C0, deltaG_rxn, A_f, Ea_f, T, t_exp, delta_Ea_cat, f_cat, deltaG_solv)
    return (C_sim - C_exp)**2

# Experimental setup
A0 = 1.0
B0 = 1.0
C0 = 0.0
T = 310.0
t_exp = 1000
C_exp = 0.35
deltaG_rxn = -5000

# Initial guess: [A_f, Ea_f, ΔEa_cat, f_cat, ΔG_solv]
initial_guess = [1e6, 40000, 5000, 2.0, 1000]

# Bounds: reasonable physical ranges
bounds = [
    (1e3, 1e10),     # A_f
    (10000, 100000), # Ea_f
    (0, 20000),      # ΔEa_cat
    (1.0, 10.0),     # f_cat
    (-5000, 5000)    # ΔG_solv
]

# Fit
result = minimize(
    cost,
    initial_guess,
    args=(A0, B0, C0, deltaG_rxn, T, t_exp, C_exp),
    bounds=bounds
)

# Output fitted parameters
A_f_fit, Ea_f_fit, delta_Ea_cat_fit, f_cat_fit, deltaG_solv_fit = result.x
print(f"Fitted A_f: {A_f_fit:.2e}")
print(f"Fitted Ea_f: {Ea_f_fit:.2f} J/mol")
print(f"Catalyst ΔEa: {delta_Ea_cat_fit:.2f} J/mol")
print(f"Catalyst factor: {f_cat_fit:.2f}")
print(f"Solvent ΔG correction: {deltaG_solv_fit:.2f} J/mol")


import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

R = 8.314  # J/mol·K

# Thermokinetic model with optional catalyst and solvent corrections
def thermokinetic_model(t, y, deltaG_rxn, A_f, Ea_f, T, delta_Ea_cat=0, f_cat=1.0, deltaG_solv=0):
    A, B, C = y
    Ea_eff = Ea_f - delta_Ea_cat
    A_eff = A_f * f_cat
    deltaG_eff = deltaG_rxn + deltaG_solv
    kf = A_eff * np.exp(-Ea_eff / (R * T))
    K_eq = np.exp(-deltaG_eff / (R * T))
    kr = kf / K_eq
    rate = kf * A * B - kr * C
    return [-rate, -rate, rate]

# Simulate [C] at a fixed time
def simulate_C_at_t(A0, B0, C0, deltaG_rxn, A_f, Ea_f, T, t_exp, delta_Ea_cat=0, f_cat=1.0, deltaG_solv=0):
    y0 = [A0, B0, C0]
    sol = solve_ivp(
        thermokinetic_model,
        (0, t_exp),
        y0,
        args=(deltaG_rxn, A_f, Ea_f, T, delta_Ea_cat, f_cat, deltaG_solv),
        t_eval=[t_exp],
        method='LSODA'
    )
    return sol.y[2][0]

# Ask user whether to include catalyst and solvent effects
include_catalyst = input("Include catalyst effect? (yes/no): ").strip().lower() == "yes"
include_solvent = input("Include solvent effect? (yes/no): ").strip().lower() == "yes"

# Experimental setup
A0 = 1.0
B0 = 1.0
C0 = 0.0
T = 310.0
t_exp = 1000
C_exp = 0.35
deltaG_rxn = -5000

# Build cost function dynamically
def cost(params):
    if include_catalyst and include_solvent:
        A_f, Ea_f, delta_Ea_cat, f_cat, deltaG_solv = params
    elif include_catalyst:
        A_f, Ea_f, delta_Ea_cat, f_cat = params
        deltaG_solv = 0
    elif include_solvent:
        A_f, Ea_f, deltaG_solv = params
        delta_Ea_cat = 0
        f_cat = 1.0
    else:
        A_f, Ea_f = params
        delta_Ea_cat = 0
        f_cat = 1.0
        deltaG_solv = 0

    C_sim = simulate_C_at_t(A0, B0, C0, deltaG_rxn, A_f, Ea_f, T, t_exp, delta_Ea_cat, f_cat, deltaG_solv)
    return (C_sim - C_exp)**2

# Set initial guesses and bounds
if include_catalyst and include_solvent:
    initial_guess = [1e6, 40000, 5000, 2.0, 1000]
    bounds = [(1e3, 1e10), (10000, 100000), (0, 20000), (1.0, 10.0), (-5000, 5000)]
elif include_catalyst:
    initial_guess = [1e6, 40000, 5000, 2.0]
    bounds = [(1e3, 1e10), (10000, 100000), (0, 20000), (1.0, 10.0)]
elif include_solvent:
    initial_guess = [1e6, 40000, 1000]
    bounds = [(1e3, 1e10), (10000, 100000), (-5000, 5000)]
else:
    initial_guess = [1e6, 40000]
    bounds = [(1e3, 1e10), (10000, 100000)]

# Run fitting
result = minimize(cost, initial_guess, bounds=bounds)
params_fit = result.x

# Display results
print("\nFitted parameters:")
if include_catalyst and include_solvent:
    print(f"A_f: {params_fit[0]:.2e}")
    print(f"Ea_f: {params_fit[1]:.2f} J/mol")
    print(f"ΔEa_cat: {params_fit[2]:.2f} J/mol")
    print(f"Catalyst factor: {params_fit[3]:.2f}")
    print(f"ΔG_solv: {params_fit[4]:.2f} J/mol")
elif include_catalyst:
    print(f"A_f: {params_fit[0]:.2e}")
    print(f"Ea_f: {params_fit[1]:.2f} J/mol")
    print(f"ΔEa_cat: {params_fit[2]:.2f} J/mol")
    print(f"Catalyst factor: {params_fit[3]:.2f}")
elif include_solvent:
    print(f"A_f: {params_fit[0]:.2e}")
    print(f"Ea_f: {params_fit[1]:.2f} J/mol")
    print(f"ΔG_solv: {params_fit[2]:.2f} J/mol")
else:
    print(f"A_f: {params_fit[0]:.2e}")
    print(f"Ea_f: {params_fit[1]:.2f} J/mol")

