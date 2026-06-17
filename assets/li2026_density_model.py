import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_li2026_halo():
    # Parameters from Li et al. (2026) - ApJ 999, 108
    # Model: Triple Power Law (DESI K Giants)
    alpha1 = 1.50
    alpha2 = 3.45
    alpha3 = 5.20
    rb1 = 16.0
    rb2 = 76.3
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    q = 0.74       # Minor axis flattening
    p = 0.85       # Intermediate axis flattening
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Triple Power Law Profile with Core
    def profile(r):
        if r < r_core:
            r_eff = r_core
        else:
            r_eff = r
            
        if r_eff < rb1:
            return r_eff**-alpha1
        elif r_eff < rb2:
            return (rb1**(alpha2 - alpha1)) * (r_eff**-alpha2)
        else:
            return (rb1**(alpha2 - alpha1)) * (rb2**(alpha3 - alpha2)) * (r_eff**-alpha3)

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Numerical Integration for Luminosity
    # For a triaxial halo: L = 4 * pi * p * q * Integral[ rho(r) * r^2 dr ]
    def integrand(r):
        return profile(r) * r**2
    
    # Integrate from 0 to 500 kpc
    result, error = quad(integrand, 0.0, 500.0)
    L_total = 4 * np.pi * p * q * rho_0 * result

    print(f"--- Li et al. (2026) DESI K Giant Halo Properties ---")
    print(f"Model:                Triple Power Law (Triaxial)")
    print(f"Central Norm (rho_0): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity: {L_total:.2e} Lsun")
    print(f"Alpha 1:              {alpha1}")
    print(f"Alpha 2:              {alpha2}")
    print(f"Alpha 3:              {alpha3}")
    print(f"Break Radius 1:       {rb1} kpc")
    print(f"Break Radius 2:       {rb2} kpc")
    print(f"Core Radius:          {r_core} kpc")
    print(f"Flattening (p, q):    {p}, {q}")
    print(f"Valid Range:          10 - 100 kpc")
    print(f"------------------------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-1, 2.7, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(10, 100, color='lightblue', alpha=0.3, label='Valid Data Range (10-100 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='darkblue', linewidth=2, label='Li et al. (2026) TPL Model (1 kpc Core)')
    
    # Markers
    plt.axvline(rb1, color='red', linestyle='--', label=f'Break 1 ({rb1} kpc)')
    plt.axvline(rb2, color='orange', linestyle='--', label=f'Break 2 ({rb2} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Stellar Halo Density Profile (Li et al. 2026)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/li2026_density_profile.png', dpi=300)
    print("Plot saved to: assets/li2026_density_profile.png")

if __name__ == "__main__":
    calculate_li2026_halo()
