import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_wu2025_halo():
    # Parameters from Wu et al. (2025) - A&A 700, A244
    # Model: Single Power Law with Variable Flattening
    alpha = 4.65
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    
    # Variable flattening q(r)
    # q ~ 0.4 at 8 kpc, q ~ 0.8 at 25 kpc
    def q_func(r):
        if r < 8: return 0.4
        if r > 25: return 0.8
        return 0.4 + (0.8 - 0.4) * (r - 8) / (25 - 8)

    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Power Law Profile with Core
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
    
    result, error = quad(integrand, 0.0, 150.0)
    L_total = 4 * np.pi * rho_0 * result

    print(f"--- Wu et al. (2025) BHB Halo Properties ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Power-law index (alpha):      {alpha}")
    print(f"Core Radius (r_core):         {r_core} kpc")
    print(f"Flattening (q):               0.4 (inner) to 0.8 (outer)")
    print(f"--------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 30, color='lightblue', alpha=0.3, label='Valid Data Range (5-30 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='royalblue', linewidth=2, label='Wu et al. (2025) Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Wu et al. 2025)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/wu2025_density_profile.png', dpi=300)
    print("Plot saved to: assets/wu2025_density_profile.png")

if __name__ == "__main__":
    calculate_wu2025_halo()
