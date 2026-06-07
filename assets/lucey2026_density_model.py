import numpy as np
import matplotlib.pyplot as plt

def calculate_lucey2026_halo():
    # Parameters from Lucey et al. (2026) - AJ, 171, 249
    # Model: Broken Power Law (Constant Flattening version)
    alpha_in = 2.1
    alpha_out = 3.8
    r_break = 18.0
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    q = 0.7        # Oblate flattening
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Broken Power Law Profile with Core
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
    # L = 4 * pi * q * Integral[ rho(r) * r^2 dr ]
    
    # Part 0: 0 to r_core (constant density)
    int0 = (r_core**-alpha_in) * (r_core**3 / 3.0)
    # Part 1: r_core to r_break
    int1 = (r_break**(3 - alpha_in) - r_core**(3 - alpha_in)) / (3 - alpha_in)
    # Part 2: r_break to infinity
    C = r_break**(alpha_out - alpha_in)
    int2 = C * (0 - r_break**(3 - alpha_out)) / (3 - alpha_out)
    
    L_total = 4 * np.pi * q * rho_0 * (int0 + int1 + int2)

    print(f"--- Lucey et al. (2026) RR Lyrae Halo Properties ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Break Radius (r_break):       {r_break} kpc")
    print(f"Core Radius (r_core):         {r_core} kpc")
    print(f"Inner Slope (alpha_in):       {alpha_in}")
    print(f"Outer Slope (alpha_out):      {alpha_out}")
    print(f"Flattening (q):               {q}")
    print(f"-----------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 100, color='lightblue', alpha=0.3, label='Valid Data Range (5-100 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='crimson', linewidth=2, label='Lucey et al. (2026) BPL Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_break, color='red', linestyle='--', label=f'Break Radius ({r_break} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Lucey et al. 2026)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/lucey2026_density_profile.png', dpi=300)
    print("Plot saved to: assets/lucey2026_density_profile.png")

if __name__ == "__main__":
    calculate_lucey2026_halo()
