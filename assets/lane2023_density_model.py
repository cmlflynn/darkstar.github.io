import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_lane2023_halo():
    # Parameters from Lane et al. (2023) - MNRAS 526, 1209
    # Model: Triaxial Oblate Single Power Law (Whole Halo fit)
    alpha = 2.5
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    p = 0.8        # Triaxial shape parameter b/a
    q = 0.58       # Triaxial shape parameter c/a (oblate)
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Single Power Law Profile with Core
    def profile(r):
        r_eff = max(r, r_core)
        return r_eff**-alpha

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Numerical Integration for Luminosity
    # L = 4 * pi * p * q * Integral[ rho(r) * r^2 dr ]
    def integrand(r):
        return profile(r) * r**2
    
    # Integrate from 0 to 500 kpc
    result, error = quad(integrand, 0.0, 500.0)
    L_total = 4 * np.pi * p * q * rho_0 * result

    print(f"--- Lane et al. (2023) Whole Halo Properties ---")
    print(f"Model:                Triaxial Oblate Single Power Law")
    print(f"Central Norm (rho_0): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity: {L_total:.2e} Lsun")
    print(f"Slope (alpha):        {alpha}")
    print(f"Core Radius:          {r_core} kpc")
    print(f"Flattening (q):       {q} (Oblate)")
    print(f"Axis ratio (p):       {p}")
    print(f"Valid Range:          2 - 40 kpc")
    print(f"------------------------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-1, 2.7, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(2, 40, color='lightblue', alpha=0.3, label='Valid Data Range (2-40 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='darkorange', linewidth=2, label='Lane et al. (2023) SPL Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Stellar Halo Density Profile (Lane et al. 2023)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/lane2023_density_profile.png', dpi=300)
    print("Plot saved to: assets/lane2023_density_profile.png")

if __name__ == "__main__":
    calculate_lane2023_halo()
