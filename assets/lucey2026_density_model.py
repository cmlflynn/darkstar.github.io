import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_lucey2026_halo():
    # Parameters from Lucey et al. (2026) - AJ, 171, 249
    # Refined Model: Single Power Law with Variable Flattening
    alpha = 4.0
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    
    # Flattening q: 1.31 for R < 10 kpc, 0.70 for R > 10 kpc
    def q_func(r):
        return 1.31 if r < 10.0 else 0.70
        
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Single Power Law Profile with Core
    def profile(r):
        if r < r_core:
            return r_core**-alpha
        else:
            return r**-alpha

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Numerical Integration for Luminosity
    # L = 4 * pi * Integral[ q(r) * rho(r) * r^2 dr ]
    def integrand(r):
        return q_func(r) * profile(r) * r**2
    
    # Integrate from 0 to 200 kpc
    result, error = quad(integrand, 0.0, 200.0)
    L_total = 4 * np.pi * rho_0 * result

    print(f"--- Lucey et al. (2026) RR Lyrae Halo Properties ---")
    print(f"Model Type:           Single Power Law with q transition")
    print(f"Central Norm (rho_0): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity: {L_total:.2e} Lsun")
    print(f"Power-law index:      {alpha}")
    print(f"Core Radius:          {r_core} kpc")
    print(f"Flattening (q):       1.31 (inner) to 0.70 (outer) at 10 kpc")
    print(f"Valid range:          0.2 - 120 kpc")
    print(f"-----------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-1, 2.3, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(0.2, 120, color='lightblue', alpha=0.3, label='Valid Data Range (0.2-120 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='crimson', linewidth=2, label='Lucey et al. (2026) SPL Model (1 kpc Core)')
    
    # Markers
    plt.axvline(10.0, color='red', linestyle='--', label='q Transition Radius (10 kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Stellar Halo Density Profile (Lucey et al. 2026)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/lucey2026_density_profile.png', dpi=300)
    print("Plot saved to: assets/lucey2026_density_profile.png")

if __name__ == "__main__":
    calculate_lucey2026_halo()
