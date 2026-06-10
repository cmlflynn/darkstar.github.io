import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_mackereth2020_halo():
    # Parameters from Mackereth & Bovy (2020) - MNRAS 492, 3631
    # Model: Triaxial Single Power Law with Exponential Cut-off
    alpha = 3.49
    r_cut = 25.0    # Exponential cut-off scale radius
    r_core = 1.0    # 1 kpc constant density core (project requirement)
    q = 0.56        # Vertical flattening
    p = 0.73        # Azimuthal flattening
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Power Law with Exponential Cut-off and Core
    def profile(r):
        if r < r_core:
            return (r_core**-alpha) * np.exp(-r_core / r_cut)
        else:
            return (r**-alpha) * np.exp(-r / r_cut)

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Numerical Integration for Luminosity
    # L = 4 * pi * p * q * Integral[ rho(r) * r^2 dr ]
    def integrand(r):
        return profile(r) * r**2
    
    # Integrate from 0 to 150 kpc (well beyond the cut-off)
    result, error = quad(integrand, 0.0, 150.0)
    L_total = 4 * np.pi * p * q * rho_0 * result

    print(f"--- Mackereth & Bovy (2020) - Weighing the stellar constituents of the galactic halo with APOGEE red giant stars ---")
    print(f"Central Norm (rho_0 at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Power-law index (alpha):      {alpha}")
    print(f"Cut-off Radius (r_cut):       {r_cut} kpc")
    print(f"Core Radius (r_core):         {r_core} kpc")
    print(f"Flattening (p, q):            {p}, {q}")
    print(f"-------------------------------------------------------------------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 30, color='lightblue', alpha=0.3, label='Valid Data Range (5-30 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='indigo', linewidth=2, label='Mackereth & Bovy (2020) Model (1 kpc Core)')
    
    # Markers
    plt.axvline(r_cut, color='red', linestyle='--', label=f'Cut-off Radius ({r_cut} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Stellar Halo Density Profile (Mackereth & Bovy 2020)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/mackereth2020_density_profile.png', dpi=300)
    print("Plot saved to: assets/mackereth2020_density_profile.png")

if __name__ == "__main__":
    calculate_mackereth2020_halo()
