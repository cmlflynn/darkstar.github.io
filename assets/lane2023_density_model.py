import numpy as np
import matplotlib.pyplot as plt

def calculate_lane2023_halo():
    # Parameters from Lane et al. (2023) - MNRAS 526, 1209
    # Model: Doubly Broken Power Law (GSE component)
    a1, a2, a3 = 1.5, 3.5, 5.0
    rb1, rb2 = 12.0, 28.0
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    
    # Flattening q ~ 1.25 (Prolate). Tilted 16 degrees.
    q = 1.25 
    p = 1.0 # Assuming axial symmetry in the prolate plane
    R_sun = 8.275 

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
    
    # Part 0: 0 to r_core
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

    print(f"--- Lane et al. (2023) - The stellar mass of the Gaia-Sausage/Enceladus accretion remnant ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Break Radii:                  {rb1} kpc, {rb2} kpc")
    print(f"Core Radius:                  {r_core} kpc")
    print(f"Power-law Indices:            {a1}, {a2}, {a3}")
    print(f"Flattening (q):               {q} (Prolate)")
    print(f"Tilt:                         16 degrees")
    print(f"---------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 50, color='lightblue', alpha=0.3, label='Valid Data Range (5-50 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='darkorange', linewidth=2, label='Lane et al. (2023) BPL Model (1 kpc Core)')
    
    # Markers
    plt.axvline(rb1, color='gray', linestyle=':', label=f'Inner Break ({rb1} kpc)')
    plt.axvline(rb2, color='gray', linestyle='--', label=f'Outer Break ({rb2} kpc)')
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
