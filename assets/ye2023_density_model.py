import numpy as np
import matplotlib.pyplot as plt

def calculate_ye2023_halo():
    # Parameters from Ye et al. (2023) - MNRAS 525, 2472
    # Model: Broken Power Law (Gaia DR3 RR Lyrae)
    alpha_in = 2.34
    alpha_out = 2.86
    r_break = 22.99
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    q = 0.81       # Constant flattening
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

    # Analytical Integration for Luminosity
    # L = 4 * pi * q * Integral[ rho(r) * r^2 dr ]
    
    # Numerical Integration for Luminosity (integrated to 500 kpc)
    def integrand(r):
        return profile(r) * r**2
    
    from scipy.integrate import quad
    res, err = quad(integrand, 0, 500)
    L_total = 4 * np.pi * q * (rho_0) * res

    print(f"--- Ye et al. (2023) Gaia DR3 RR Lyrae Halo Properties ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Break Radius (r_break):       {r_break} kpc")
    print(f"Core Radius (r_core):         {r_core} kpc")
    print(f"Inner Slope (alpha_in):       {alpha_in}")
    print(f"Outer Slope (alpha_out):      {alpha_out}")
    print(f"Flattening (q):               {q}")
    print(f"----------------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(6, 26, color='lightblue', alpha=0.3, label='Valid Data Range (6-26 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='forestgreen', linewidth=2, label='Ye et al. (2023) RR Lyrae Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_break, color='red', linestyle='--', label=f'Break Radius ({r_break} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Stellar Halo Density Profile (Ye et al. 2023)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/ye2023_density_profile.png', dpi=300)
    print("Plot saved to: assets/ye2023_density_profile.png")

if __name__ == "__main__":
    calculate_ye2023_halo()
