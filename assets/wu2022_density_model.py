import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def calculate_wu2022_halo():
    # Parameters from Wu et al. (2022) - AJ 164, 41
    # Model: Sum of two power laws
    a1 = 4.92
    a2 = 4.25
    r_core = 1.0   # 1 kpc constant density core (project requirement)
    
    # Matching radius: ln(R) = 3.0 => R ~ 20.0855 kpc
    r_match = np.exp(3.0) 
    
    # Variable flattening q(r)
    def q_func(r):
        if r < 8: return 0.4
        if r > 25: return 0.8
        return 0.4 + (0.8 - 0.4) * (r - 8) / (25 - 8)

    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Sum of two power laws: rho = rho1*r^-a1 + rho2*r^-a2
    # Condition: rho1 * r_match^-a1 = rho2 * r_match^-a2
    # rho1 = rho2 * r_match^(a1 - a2)
    # Total profile f(r) = r_match^(a1-a2) * r^-a1 + r^-a2
    
    def get_raw_profile(r):
        term1 = (r_match**(a1 - a2)) * (r**-a1)
        term2 = r**-a2
        return term1 + term2

    # Normalization at the Sun
    # Apply 1 kpc core to the RAW profile shape
    def profile_with_core(r):
        if r < r_core:
            return get_raw_profile(r_core)
        return get_raw_profile(r)

    norm_at_sun = profile_with_core(R_sun)
    rho_0_unit = rho_local_Lsun_kpc3 / norm_at_sun

    # Final Density Function (Lsun/kpc^3)
    def density_kpc3(r):
        return rho_0_unit * profile_with_core(r)

    # Numerical Integration for Luminosity
    # L = 4 * pi * Integral[ q(r) * rho(r) * r^2 dr ]
    def integrand(r):
        return q_func(r) * density_kpc3(r) * r**2
    
    result, error = quad(integrand, 0.0, 150.0)
    L_total = 4 * np.pi * result

    print(f"--- Wu et al. (2022) K Giant Halo Properties ---")
    print(f"Model:                Sum of two Power Laws")
    print(f"Total Halo Luminosity: {L_total:.2e} Lsun")
    print(f"Alpha 1 (Inner-ish):   {a1}")
    print(f"Alpha 2 (Outer-ish):   {a2}")
    print(f"Match Radius:          {r_match:.2f} kpc")
    print(f"Core Radius:           {r_core} kpc")
    print(f"Flattening (q):        0.4 (inner) to 0.8 (outer)")
    print(f"--------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([density_kpc3(r) for r in r_vals])
    
    # Components for plotting
    term1_vals = np.array([rho_0_unit * (r_match**(a1 - a2)) * (max(r, r_core)**-a1) for r in r_vals])
    term2_vals = np.array([rho_0_unit * (max(r, r_core)**-a2) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 120, color='lightblue', alpha=0.3, label='Valid Data Range (5-120 kpc)')
    
    # Plot components
    plt.loglog(r_vals, term1_vals / (1000**3), color='gray', linestyle='--', alpha=0.6, label=f'Component 1 (alpha={a1})')
    plt.loglog(r_vals, term2_vals / (1000**3), color='gray', linestyle=':', alpha=0.6, label=f'Component 2 (alpha={a2})')
    
    # Plot sum
    plt.loglog(r_vals, rho_vals / (1000**3), color='black', linewidth=2.5, label='Wu et al. (2022) Total (Sum-of-PL)')
    
    # Markers
    plt.axvline(r_match, color='red', linestyle='--', label=f'Equidensity Radius ({r_match:.1f} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='blue', linestyle='-.', alpha=0.4, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('K-Giant Stellar Halo Density Profile (Wu et al. 2022)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/wu2022_density_profile.png', dpi=300)
    print("Plot saved to: assets/wu2022_density_profile.png")

if __name__ == "__main__":
    calculate_wu2022_halo()
