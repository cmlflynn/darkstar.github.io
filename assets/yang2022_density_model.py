import numpy as np
import matplotlib.pyplot as plt

def calculate_yang2022_halo():
    # Parameters from Yang et al. (2022) - AJ 164:241
    # Double-broken power law
    a1, a2, a3 = 1.5, 2.8, 6.1
    rb1, rb2 = 10.0, 25.0
    
    # Flattening q: 0.5 at r < 5, 0.8 at r > 30.
    # We'll use a simple linear interpolation or just the values for the integration.
    # For simplicity in luminosity calc, let's use the profile with q changing.
    def q_func(r):
        if r < 5: return 0.5
        if r > 30: return 0.8
        return 0.5 + (0.8 - 0.5) * (r - 5) / (30 - 5)

    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Double-Broken Power Law Profile
    def profile(r):
        if r < rb1:
            return r**-a1
        elif r < rb2:
            return (rb1**(a2-a1)) * (r**-a2)
        else:
            C = rb1**(a2-a1)
            return (C * rb2**(a3-a2)) * (r**-a3)

    # Normalization at the Sun
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Numerical Integration for Luminosity
    # L = 4 * pi * Integral[ q(r) * rho(r) * r^2 dr ]
    from scipy.integrate import quad
    
    def integrand(r):
        return q_func(r) * profile(r) * r**2
    
    # Integrate from 0.1 to 150 kpc
    result, error = quad(integrand, 0.1, 150.0)
    L_total = 4 * np.pi * rho_0 * result

    print(f"--- Yang et al. (2022) Halo Properties ---")
    print(f"Central Norm (at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:  {L_total:.2e} Lsun")
    print(f"Break Radii:            {rb1} kpc, {rb2} kpc")
    print(f"Inner Index (a1):       {a1}")
    print(f"Middle Index (a2):      {a2}")
    print(f"Outer Index (a3):       {a3}")
    print(f"Flattening (q):         0.5 (inner) to 0.8 (outer)")
    print(f"-------------------------------------------")

    # Plotting
    r_vals = np.logspace(0, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 50, color='lightblue', alpha=0.3, label='Valid Data Range (5-50 kpc)')
    plt.loglog(r_vals, rho_vals / (1000**3), color='darkgreen', linewidth=2, label='Yang et al. (2022) Model')
    
    # Markers
    plt.axvline(rb1, color='gray', linestyle=':', label=f'Inner Break ({rb1} kpc)')
    plt.axvline(rb2, color='gray', linestyle='--', label=f'Outer Break ({rb2} kpc)')
    plt.axvline(R_sun, color='blue', linestyle='-.', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Yang et al. 2022)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/yang2022_density_profile.png', dpi=300)
    print("Plot saved to: assets/yang2022_density_profile.png")

if __name__ == "__main__":
    calculate_yang2022_halo()
