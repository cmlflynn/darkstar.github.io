import numpy as np
import matplotlib.pyplot as plt

def calculate_halo_properties():
    # Parameters from Horta & Schiavon (2025) - staf256.pdf
    # Table 1: Combined Sample results
    a_kpc = 3.48    # Plummer scale radius in kpc
    p = 0.80        # Triaxial flattening in Y
    q = 0.66        # Triaxial flattening in Z
    R_sun_kpc = 8.275 # Galactocentric distance of the Sun

    # User-provided local normalization at the Sun (X=R_sun, Y=0, Z=0)
    rho_local_Lsun_pc3 = 1.7e-5
    # Convert Lsun/pc^3 to Lsun/kpc^3
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # The triaxial Plummer profile:
    # rho(r_e) = rho_0 * (1 + (r_e/a)**2)**(-2.5)
    # At the Sun: r_e = sqrt(R_sun**2 + (0/p)**2 + (0/q)**2) = R_sun
    # rho_local = rho_0 * (1 + (R_sun/a)**2)**(-2.5)
    
    # Solve for central density rho_0
    rho_0 = rho_local_Lsun_kpc3 * (1 + (R_sun_kpc / a_kpc)**2)**2.5

    # Total Luminosity calculation (integration to infinity)
    # The volume element in triaxial coordinates (x, y, z) = (x', py', qz') 
    # adds a factor of (p * q) to the standard spherical Plummer integration.
    # L_total = pq * Integral[ rho_0 * (1 + (r'/a)**2)**(-2.5) * 4*pi*r'^2 dr' ]
    # Analytical solution for Plummer: (4/3) * pi * a^3 * rho_0
    L_total = p * q * rho_0 * (4/3) * np.pi * (a_kpc**3)

    print(f"--- Halo Properties (Horta & Schiavon 2025 Model) ---")
    print(f"Central Density (rho_0): {rho_0:.2e} Lsun/kpc^3")
    print(f"Local Density (fixed):   {rho_local_Lsun_pc3:.2e} Lsun/pc^3")
    print(f"Total Halo Luminosity:   {L_total:.2e} Lsun")
    print(f"------------------------------------------------------")

    # Generate the density profile plot
    r = np.logspace(-1, 2, 500) # Radius from 0.1 to 100 kpc
    rho_r = rho_0 * (1 + (r / a_kpc)**2)**(-2.5) # Density along X-axis

    plt.figure(figsize=(10, 7))
    plt.loglog(r, rho_r / (1000**3), color='blue', linewidth=2, label='Triaxial Plummer (Major Axis)')
    
    # Markers
    plt.axvline(R_sun_kpc, color='red', linestyle='--', alpha=0.7, label=f'Sun ($R_\\odot$={R_sun_kpc} kpc)')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle=':', alpha=0.7, label=f'Local Norm ({rho_local_Lsun_pc3:.1e} $L_\\odot/pc^3$)')

    # Formatting
    plt.title('Milky Way Stellar Halo Density Profile\n(Model: Horta & Schiavon 2025)', fontsize=14)
    plt.xlabel('Galactocentric Radius [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True, loc='best')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    output_png = 'staf256_density_profile.png'
    plt.savefig(output_png, dpi=300)
    print(f"Plot saved to: {output_png}")

if __name__ == "__main__":
    calculate_halo_properties()
