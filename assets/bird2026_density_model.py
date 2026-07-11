import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_bird2026_halo():
    # Parameters from Bird et al. (2026) (submitted)
    # Model: Spherical Broken Power Law
    alpha_in = 2.5
    alpha_out = 4.0
    r_break = 20.0
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    q = 1.0        # Spherical halo
    p = 1.0        # Spherical halo
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Broken Power Law Profile with Core
    def profile(r):
        r_eff = max(r, r_core)
        if r_eff < r_break:
            return r_eff**-alpha_in
        else:
            return (r_break**(alpha_out - alpha_in)) * (r_eff**-alpha_out)

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Numerical Integration for Luminosity
    def integrand(r):
        return profile(r) * r**2
    
    # Integrate from 0 to 100 kpc (paper limit)
    res_100, _ = quad(integrand, 0.0, 100.0)
    L_100 = 4 * np.pi * q * rho_0 * res_100

    # Integrate from 0 to 500 kpc (code comparison limit)
    res_500, _ = quad(integrand, 0.0, 500.0)
    L_500 = 4 * np.pi * q * rho_0 * res_500

    print(f"--- Bird et al. (2026): Galactic Stellar Halo Luminosity Function ---")
    print(f"Model:                Spherical Broken Power Law")
    print(f"Central Norm (rho_0): {rho_0:.2e} Lsun/kpc^3")
    print(f"Luminosity (to 100kpc):{L_100:.2e} Lsun (matches paper 4.6e+08 Lsun)")
    print(f"Luminosity (to 500kpc):{L_500:.2e} Lsun")
    print(f"Inner Slope (alpha_in):{alpha_in}")
    print(f"Outer Slope (alpha_out):{alpha_out}")
    print(f"Break Radius:          {r_break} kpc")
    print(f"Core Radius:          {r_core} kpc")
    print(f"Flattening (q):       {q} (Spherical)")
    print(f"Model Extrapolation Range: 0.1 - 100 kpc")
    print(f"------------------------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-1, 2.7, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(0.1, 100, color='lightblue', alpha=0.3, label='Model Extrapolation Range (0.1-100 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='darkred', linewidth=2, label='Bird et al. (2026) BPL Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_break, color='red', linestyle='--', label=f'Break Radius ({r_break} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Stellar Halo Density Profile (Bird et al. 2026)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/bird2026_density_profile.png', dpi=300)
    print("Plot saved to: assets/bird2026_density_profile.png")

if __name__ == "__main__":
    calculate_bird2026_halo()
