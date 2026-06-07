import numpy as np
import matplotlib.pyplot as plt

def calculate_rix2022_halo():
    # Parameters from Rix et al. (2022) - ApJ 941, 45
    # Model: Single Power Law (for the ancient "Aurora" core)
    alpha = 4.0
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    q = 1.0        # Nearly spherical
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

    # Analytical Integration for Luminosity
    # L = 4 * pi * q * Integral[ rho(r) * r^2 dr ]
    # Part 0: 0 to r_core
    int0 = (r_core**-alpha) * (r_core**3 / 3.0)
    # Part 1: r_core to infinity
    int1 = (0 - r_core**(3 - alpha)) / (3 - alpha)
    
    L_total = 4 * np.pi * q * rho_0 * (int0 + int1)

    print(f"--- Rix et al. (2022) Aurora Halo Properties ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Power-law index (alpha):      {alpha}")
    print(f"Core Radius (r_core):         {r_core} kpc")
    print(f"Flattening (q):               {q} (Spherical)")
    print(f"--------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(0.1, 5, color='lightblue', alpha=0.3, label='Valid Data Range (0-5 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='firebrick', linewidth=2, label='Rix et al. (2022) Aurora Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Rix et al. 2022)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/rix2022_density_profile.png', dpi=300)
    print("Plot saved to: assets/rix2022_density_profile.png")

if __name__ == "__main__":
    calculate_rix2022_halo()
