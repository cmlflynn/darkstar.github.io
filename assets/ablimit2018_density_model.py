import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_ablimit2018_halo():
    # Parameters from Ablimit & Zhao (2018) - ApJ 855, 126
    # Model: Broken Power Law (Catalina RR Lyrae)
    alpha_in = 2.8
    alpha_out = 4.8
    r_break = 21.0
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    q = 1.0        # Spherical model
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Broken Power Law Profile with Core
    def profile(r):
        if r < r_core:
            r_eff = r_core
        else:
            r_eff = r
            
        if r_eff < r_break:
            return r_eff**-alpha_in
        else:
            return (r_break**(alpha_out - alpha_in)) * (r_eff**-alpha_out)

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Numerical Integration for Luminosity
    # L = 4 * pi * q * Integral[ rho(r) * r^2 dr ]
    def integrand(r):
        return profile(r) * r**2
    
    # Integrate from 0 to 500 kpc
    result, error = quad(integrand, 0.0, 500.0)
    L_total = 4 * np.pi * q * rho_0 * result

    print(f"--- Ablimit et al. (2018) Catalina RRL Halo Properties ---")
    print(f"Model:                Broken Power Law")
    print(f"Central Norm (rho_0): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity: {L_total:.2e} Lsun")
    print(f"Alpha In:             {alpha_in}")
    print(f"Alpha Out:            {alpha_out}")
    print(f"Break Radius:         {r_break} kpc")
    print(f"Core Radius:          {r_core} kpc")
    print(f"Flattening (q):       {q}")
    print(f"Valid Range:          9 - 50 kpc")
    print(f"------------------------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-1, 2.7, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(9, 50, color='lightblue', alpha=0.3, label='Valid Data Range (9-50 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='firebrick', linewidth=2, label='Ablimit et al. (2018) BPL Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_break, color='red', linestyle='--', label=f'Break Radius ({r_break} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Stellar Halo Density Profile (Ablimit et al. 2018)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/ablimit2018_density_profile.png', dpi=300)
    print("Plot saved to: assets/ablimit2018_density_profile.png")

if __name__ == "__main__":
    calculate_ablimit2018_halo()
