import numpy as np
import matplotlib.pyplot as plt

def calculate_horta2021_halo():
    # Parameters from Horta et al. (2021) - MNRAS 500, 5462
    # Model: Triaxial Plummer (Heracles component)
    a_kpc = 3.5     # Plummer scale radius
    p = 0.8         # Triaxial flattening in Y
    q = 0.6         # Triaxial flattening in Z
    R_sun_kpc = 8.275 

    # User-provided local normalization at the Sun
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # rho(r_e) = rho_0 * (1 + (r_e/a)**2)**(-2.5)
    # Solve for rho_0 at the Sun (r_e = R_sun)
    rho_0 = rho_local_Lsun_kpc3 * (1 + (R_sun_kpc / a_kpc)**2)**2.5

    # Total Luminosity for Triaxial Plummer:
    # L_total = p * q * rho_0 * (4/3) * pi * a^3
    L_total = p * q * rho_0 * (4/3) * np.pi * (a_kpc**3)

    print(f"--- Horta et al. (2021) Heracles Halo Properties ---")
    print(f"Central Density (rho_0): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:   {L_total:.2e} Lsun")
    print(f"Scale Radius (a):        {a_kpc} kpc")
    print(f"Flattening (p, q):       {p}, {q}")
    print(f"------------------------------------------------------")

    # Generate the density profile plot
    r = np.logspace(-1, 2, 500) 
    rho_r = rho_0 * (1 + (r / a_kpc)**2)**(-2.5)

    plt.figure(figsize=(10, 7))
    plt.axvspan(0.1, 10, color='lightblue', alpha=0.3, label='Valid Data Range (0-10 kpc)')
    plt.loglog(r, rho_r / (1000**3), color='crimson', linewidth=2, label='Triaxial Plummer (Major Axis)')
    
    # Markers
    plt.axvline(R_sun_kpc, color='red', linestyle='--', alpha=0.7, label=f'Sun ($R_\\odot$={R_sun_kpc} kpc)')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle=':', alpha=0.7, label=f'Local Norm ({rho_local_Lsun_pc3:.1e} $L_\\odot/pc^3$)')

    plt.title('Heracles Stellar Halo Density Profile (Horta et al. 2021)', fontsize=14)
    plt.xlabel('Galactocentric Radius [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True, loc='best')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    output_png = 'assets/horta2021_density_profile.png'
    plt.savefig(output_png, dpi=300)
    print(f"Plot saved to: {output_png}")

if __name__ == "__main__":
    calculate_horta2021_halo()
