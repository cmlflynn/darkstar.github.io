import numpy as np
import matplotlib.pyplot as plt

def calculate_feng2024_halo():
    # Parameters from Feng et al. (2024) - ApJ 966, 159
    # Model: Single Power Law for the Outer Halo (25-90 kpc)
    alpha = 4.5    # Fit for M-giants (cleaner sample)
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    q = 1.0        # Spherical outer halo
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
    # Part 0: 0 to r_core
    int0 = (r_core**-alpha) * (r_core**3 / 3.0)
    # Part 1: r_core to infinity
    int1 = (0 - r_core**(3 - alpha)) / (3 - alpha)
    
    L_total = 4 * np.pi * q * rho_0 * (int0 + int1)

    print(f"--- Feng et al. (2024) LAMOST Giant Halo Properties ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Power-law index (alpha):      {alpha}")
    print(f"Core Radius (r_core):         {r_core} kpc")
    print(f"Flattening (q):               {q} (Spherical)")
    print(f"-------------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(25, 90, color='lightblue', alpha=0.3, label='Valid Data Range (25-90 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='darkgreen', linewidth=2, label='Feng et al. (2024) Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Feng et al. 2024)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/feng2024_density_profile.png', dpi=300)
    print("Plot saved to: assets/feng2024_density_profile.png")

if __name__ == "__main__":
    calculate_feng2024_halo()
