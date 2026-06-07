import numpy as np
import matplotlib.pyplot as plt

def calculate_chen2023_halo():
    # Parameters from Chen et al. (2023) - MNRAS 525, 3075
    # Best-fitting 4-parameter BPL model (including flattening q)
    # Using the values after removing Sgr stream (if available, otherwise the main ones)
    # Paper states: s1 = 2.83, s2 = 4.49, r0 = 27.45 kpc, q = 0.73
    s1 = 2.83
    s2 = 4.49
    r0 = 27.45
    q = 0.73
    
    # Solar position (standard value)
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Broken Power Law Profile Function (r_q = sqrt(x^2 + y^2 + (z/q)^2))
    def profile(r):
        if r < r0:
            return r**-s1
        else:
            return (r0**(s2 - s1)) * (r**-s2)

    # Normalization at the Sun
    # Note: At the Sun, z=0 so r_q = R_sun.
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Analytical Integration for Luminosity
    # L = 4 * pi * q * Integral[ rho(r_q) * r_q^2 dr_q ]
    
    # Part 1: 0 to r0
    int1 = (r0**(3 - s1)) / (3 - s1)
    # Part 2: r0 to infinity
    C = r0**(s2 - s1)
    int2 = C * (0 - r0**(3 - s2)) / (3 - s2)
    
    L_total = 4 * np.pi * q * rho_0 * (int1 + int2)

    print(f"--- Chen et al. (2023) BPL Halo Properties ---")
    print(f"Central Norm (at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:  {L_total:.2e} Lsun")
    print(f"Break Radius (r0):      {r0} kpc")
    print(f"Inner Slope (s1):       {s1}")
    print(f"Outer Slope (s2):       {s2}")
    print(f"Flattening (q):         {q}")
    print(f"---------------------------------------------------")

    # Plotting
    r_vals = np.logspace(0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 100, color='lightblue', alpha=0.3, label='Valid Data Range (5-100 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='purple', linewidth=2, label='Chen et al. (2023) BPL Model')
    
    # Markers
    plt.axvline(r0, color='red', linestyle='--', label=f'Break Radius ({r0} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Chen et al. 2023)', fontsize=14)
    plt.xlabel('Flattened Radius $r_q$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/chen2023_density_profile.png', dpi=300)
    print("Plot saved to: assets/chen2023_density_profile.png")

if __name__ == "__main__":
    calculate_chen2023_halo()
