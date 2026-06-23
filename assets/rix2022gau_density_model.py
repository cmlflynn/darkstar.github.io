import numpy as np
import matplotlib.pyplot as plt

def calculate_rix2022gau_halo():
    # Parameters from Rix et al. (2022) - ApJ 941, 45
    # Model: Gaussian density falloff (for the ancient "Aurora" core)
    sigma = 2.7
    q = 1.0        # Spherical
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Gaussian Profile (No Core)
    def profile(r):
        return np.exp(-(r**2 - R_sun**2) / (2 * sigma**2))

    # Analytical Integration (Total Luminosity)
    from scipy.integrate import quad
    fn = lambda r: rho_local_Lsun_kpc3 * np.exp(-(r**2 - R_sun**2)/(2*sigma**2)) * 4 * np.pi * (r**2)
    L_total, _ = quad(fn, 0, np.inf)

    print(f"--- Rix et al. (2022) Aurora Halo [Gaussian] Properties ---")
    print(f"Total Halo Luminosity:        {L_total:.2e} Lsun")
    print(f"Sigma (sigma):                {sigma} kpc")
    print(f"Flattening (q):               {q} (Spherical)")
    print(f"--------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_vals = np.array([rho_local_Lsun_pc3 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(0.1, 5, color='lightblue', alpha=0.3, label='Valid Data Range (0-5 kpc)')
    plt.loglog(r_vals, rho_vals, color='firebrick', linewidth=2, label='Rix et al. (2022) Aurora Model (Gaussian)')
    
    # Markers
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Rix et al. 2022 Gaussian)', fontsize=14)
    plt.xlabel('Radius $r$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/rix2022gau_density_profile.png', dpi=300)
    print("Plot saved to: assets/rix2022gau_density_profile.png")

if __name__ == "__main__":
    calculate_rix2022gau_halo()
