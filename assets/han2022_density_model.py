import numpy as np
import matplotlib.pyplot as plt

def calculate_han2022_halo():
    # Parameters from Han et al. (2022) - AJ 164:249
    # Fiducial GSE model
    a1, a2, a3 = 1.70, 3.09, 4.58
    rb1, rb2 = 11.85, 28.33
    r_core = 1.0  # 1 kpc constant density core
    p, q = 0.81, 0.73
    R_sun = 8.122  # Solar position used in the paper

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Doubly Broken Power Law Profile with Core
    def profile(r):
        if r < r_core:
            return r_core**-a1
        elif r < rb1:
            return r**-a1
        elif r < rb2:
            return (rb1**(a2-a1)) * (r**-a2)
        else:
            C = rb1**(a2-a1)
            return (C * rb2**(a3-a2)) * (r**-a3)

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Analytical Integration for Luminosity
    # L = 4 * pi * p * q * Integral[ rho(r) * r^2 dr ]
    # Part 0: 0 to r_core (constant density)
    int0 = (r_core**-a1) * (r_core**3 / 3.0)
    # Part 1: r_core to rb1
    int1 = (rb1**(3-a1) - r_core**(3-a1)) / (3-a1)
    # Part 2: rb1 to rb2
    C = rb1**(a2-a1)
    int2 = C * (rb2**(3-a2) - rb1**(3-a2)) / (3-a2)
    # Part 3: rb2 to infinity
    D = C * rb2**(a3-a2)
    int3 = D * (0 - rb2**(3-a3)) / (3-a3)

    L_total = 4 * np.pi * p * q * rho_0 * (int0 + int1 + int2 + int3)

    print(f"--- Han et al. (2022) GSE Halo Properties ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Break Radii:                  {rb1} kpc, {rb2} kpc")
    print(f"Core Radius:                  {r_core} kpc")
    print(f"Power-law Indices:            {a1}, {a2}, {a3}")
    print(f"----------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 50, color='lightblue', alpha=0.3, label='Valid Data Range (5-50 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='darkred', linewidth=2, label='Han et al. (2022) GSE Model (1 kpc Core)')
    
    # Markers
    plt.axvline(rb1, color='gray', linestyle=':', label=f'Inner Break ({rb1} kpc)')
    plt.axvline(rb2, color='gray', linestyle='--', label=f'Outer Break ({rb2} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='blue', linestyle='-.', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('GSE Stellar Halo Density Profile (Han et al. 2022)', fontsize=14)
    plt.xlabel('Flattened Radius [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/han2022_density_profile.png', dpi=300)
    print("Plot saved to: assets/han2022_density_profile.png")

if __name__ == "__main__":
    calculate_han2022_halo()
