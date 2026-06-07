import numpy as np
import matplotlib.pyplot as plt

def calculate_libinney2022_halo():
    # Parameters from Li & Binney (2022) - MNRAS 510, 4706
    # Model: Softened Double Power Law (Simplified for density profile)
    # They find an outer slope of ~ -4.5 and inner slope is shallower.
    # We'll use a smooth broken power law form that matches their results.
    alpha_in = 1.0  # Shallower inner slope
    alpha_out = 4.5
    r_break = 20.0  # Smooth transition starting around 20 kpc
    r_core = 1.0    # 1 kpc constant density core (project requirement)
    q = 0.65        # Oblate flattening
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Smooth Double Power Law Profile with Core
    def profile(r):
        if r < r_core:
            return r_core**-alpha_in
        elif r < r_break:
            return r**-alpha_in
        else:
            return (r_break**(alpha_out - alpha_in)) * (r**-alpha_out)

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Analytical Integration for Luminosity
    # Part 0: 0 to r_core
    int0 = (r_core**-alpha_in) * (r_core**3 / 3.0)
    # Part 1: r_core to r_break
    int1 = (r_break**(3 - alpha_in) - r_core**(3 - alpha_in)) / (3 - alpha_in)
    # Part 2: r_break to infinity
    C = r_break**(alpha_out - alpha_in)
    int2 = C * (0 - r_break**(3 - alpha_out)) / (3 - alpha_out)
    
    L_total = 4 * np.pi * q * rho_0 * (int0 + int1 + int2)

    print(f"--- Li & Binney (2022) RR Lyrae Halo Properties ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Outer Slope (alpha_out):      {alpha_out}")
    print(f"Transition Region (r_break):  {r_break} kpc")
    print(f"Core Radius (r_core):         {r_core} kpc")
    print(f"Flattening (q):               {q}")
    print(f"---------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(0.1, 100, color='lightblue', alpha=0.3, label='Valid Data Range (0-100 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='navy', linewidth=2, label='Li & Binney (2022) Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_break, color='red', linestyle='--', label=f'Transition Region ({r_break} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Li & Binney 2022)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/libinney2022_density_profile.png', dpi=300)
    print("Plot saved to: assets/libinney2022_density_profile.png")

if __name__ == "__main__":
    calculate_libinney2022_halo()
