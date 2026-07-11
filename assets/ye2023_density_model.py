import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_ye2023_halo():
    # Parameters from Table 1 of Ye et al. (2023)
    bins = [
        {"range": (6.0, 26.0), "r_break": 24.0, "n": 2.1, "q": 0.68, "delta_n": 0.5, "name": "GSE Inner Apocenter"},
        {"range": (26.0, 36.0), "r_break": 31.0, "n": 2.9, "q": 0.86, "delta_n": 0.5, "name": "GSE Outer Apocenter"},
        {"range": (36.0, 46.0), "r_break": 43.0, "n": 3.4, "q": 0.81, "delta_n": -0.3, "name": "Sgr Stream (Reverse Break)"},
        {"range": (46.0, 76.0), "r_break": 57.0, "n": 3.2, "q": 0.84, "delta_n": 0.2, "name": "Outer Shell A"},
        {"range": (76.0, 96.0), "r_break": 91.0, "n": 3.4, "q": 0.91, "delta_n": 0.2, "name": "Outer Shell B"},
        {"range": (96.0, 116.0), "r_break": 107.0, "n": 3.8, "q": 0.90, "delta_n": 0.4, "name": "Observation Boundary"},
    ]

    r_core = 1.0   # 1 kpc constant density core (project requirement)
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Exponent function g(r_e)
    def g_func(r_e, n, delta_n, r_break, a=0.0):
        return n + 0.5 * delta_n + (delta_n / np.pi) * np.arctan(10.0**a * (r_e - r_break))

    # Compute continuity coefficients rho_rel (relative to rho_rel_1 = 1.0)
    rho_rel = [1.0]
    for idx in range(1, len(bins)):
        prev_bin = bins[idx-1]
        curr_bin = bins[idx]
        r_bound = prev_bin["range"][1]
        
        g_prev = g_func(r_bound, prev_bin["n"], prev_bin["delta_n"], prev_bin["r_break"])
        density_bound = rho_rel[-1] * (R_sun / r_bound) ** g_prev
        
        g_curr = g_func(r_bound, curr_bin["n"], curr_bin["delta_n"], curr_bin["r_break"])
        rho_rel_curr = density_bound / ((R_sun / r_bound) ** g_curr)
        rho_rel.append(rho_rel_curr)

    for idx, b in enumerate(bins):
        b["rho_rel"] = rho_rel[idx]

    # Density profile along major axis
    def profile_rel(r):
        r_eff = max(r, r_core)
        # Find active bin
        active_bin = None
        for idx, b in enumerate(bins):
            r_min, r_max = b["range"]
            if idx == 0:
                if r_eff <= r_max: active_bin = b; break
            elif idx == len(bins) - 1:
                if r_eff > r_min: active_bin = b; break
            else:
                if r_min < r_eff <= r_max: active_bin = b; break
        
        if active_bin is None:
            active_bin = bins[-1]

        g = g_func(r_eff, active_bin["n"], active_bin["delta_n"], active_bin["r_break"])
        return active_bin["rho_rel"] * (R_sun / r_eff) ** g

    norm_at_sun = profile_rel(R_sun) # Should be 1.0
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun # norm factor

    def integrand_1d(r):
        r_eff = max(r, r_core)
        active_bin = None
        for idx, b in enumerate(bins):
            r_min, r_max = b["range"]
            if idx == 0:
                if r_eff <= r_max: active_bin = b; break
            elif idx == len(bins) - 1:
                if r_eff > r_min: active_bin = b; break
            else:
                if r_min < r_eff <= r_max: active_bin = b; break
        if active_bin is None:
            active_bin = bins[-1]

        g = g_func(r_eff, active_bin["n"], active_bin["delta_n"], active_bin["r_break"])
        rho_val = active_bin["rho_rel"] * (R_sun / r_eff) ** g
        return (r**2) * 4 * np.pi * active_bin["q"] * rho_0 * rho_val

    res, err = quad(integrand_1d, 0, 500)
    L_total = res

    print(f"--- Ye et al. (2023) Gaia DR3 RR Lyrae 6-Segment Halo Properties ---")
    print(f"Central Norm (rho_0 at Sun):  {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity (1D):  {L_total:.2e} Lsun")
    print(f"Valid Range:                  6.0 - 116.0 kpc")
    print(f"----------------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.7, 500)
    rho_vals = np.array([rho_0 * profile_rel(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(6, 116, color='lightblue', alpha=0.3, label='Valid Data Range (6-116 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='forestgreen', linewidth=2, label='Ye et al. (2023) RR Lyrae 6-Segment Model (1 kpc Core)')
    
    # Markers for breaks
    colors = ['red', 'orange', 'gold', 'green', 'blue', 'purple']
    for idx, b in enumerate(bins):
        plt.axvline(b["r_break"], color=colors[idx], linestyle='--', alpha=0.7, label=f'Break {idx+1}: {b["r_break"]} kpc ({b["name"]})')

    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Stellar Halo Density Profile (Ye et al. 2023 6-Segment)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True, fontsize=8, loc='upper right')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/ye2023_density_profile.png', dpi=300)
    print("Plot saved to: assets/ye2023_density_profile.png")

if __name__ == "__main__":
    calculate_ye2023_halo()
