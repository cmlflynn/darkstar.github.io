import numpy as np
import matplotlib.pyplot as plt

def calculate_amarante2024_halo():
    # Parameters from Amarante et al. (2024) - A&A 690, A166
    alpha_in = 2.9
    alpha_out = 4.5
    r_br = 19.1
    r_core = 1.0  # 1 kpc constant density core
    
    q_inner = 0.77
    q_outer = 0.99
    
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # 1. Profile without core
    def profile_no_core(r):
        if r < r_br:
            return r**-alpha_in
        else:
            return (r_br**(alpha_out - alpha_in)) * (r**-alpha_out)

    # 2. Profile with core
    def profile_with_core(r):
        if r < r_core:
            return r_core**-alpha_in
        elif r < r_br:
            return r**-alpha_in
        else:
            return (r_br**(alpha_out - alpha_in)) * (r**-alpha_out)

    # Normalization at the Sun (Sun is at 8.275 kpc, which is > r_core)
    norm_at_sun = profile_no_core(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # --- Luminosity WITHOUT core ---
    # 0 to r_br
    int1_nc = (r_br**(3 - alpha_in)) / (3 - alpha_in)
    # r_br to 30 kpc
    C = r_br**(alpha_out - alpha_in)
    int2_nc = C * (30**(3 - alpha_out) - r_br**(3 - alpha_out)) / (3 - alpha_out)
    # 30 kpc to infinity
    int3_nc = C * (0 - 30**(3 - alpha_out)) / (3 - alpha_out)
    
    L_no_core = 4 * np.pi * rho_0 * (q_inner * (int1_nc + int2_nc) + q_outer * int3_nc)

    # --- Luminosity WITH core ---
    # 0 to r_core (constant density: rho = rho_0 * r_core^-alpha_in)
    int_core = (r_core**-alpha_in) * (r_core**3 / 3.0)
    # r_core to r_br
    int1_c = (r_br**(3 - alpha_in) - r_core**(3 - alpha_in)) / (3 - alpha_in)
    # rest are same as int2_nc, int3_nc
    
    L_with_core = 4 * np.pi * rho_0 * (q_inner * (int_core + int1_c + int2_nc) + q_outer * int3_nc)

    print(f"--- Amarante et al. (2024) BHB Halo Properties ---")
    print(f"Break Radius:           {r_br} kpc")
    print(f"Core Radius:            {r_core} kpc")
    print(f"Inner Slope (alpha):    {alpha_in}")
    print(f"Outer Slope (alpha):    {alpha_out}")
    print(f"Luminosity (No Core):   {L_no_core:.2e} Lsun")
    print(f"Luminosity (With Core): {L_with_core:.2e} Lsun")
    print(f"Difference:             {((L_no_core - L_with_core)/L_no_core)*100:.2f}%")
    print(f"---------------------------------------------------")

    # Plotting
    r_vals = np.logspace(-0.5, 2.2, 500)
    rho_nc = np.array([rho_0 * profile_no_core(r) for r in r_vals])
    rho_c = np.array([rho_0 * profile_with_core(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.axvspan(5, 120, color='lightblue', alpha=0.3, label='Valid Data Range (5-120 kpc)')
    plt.loglog(r_vals, rho_nc / (1000**3), color='blue', linestyle='--', alpha=0.5, label='Original (No Core)')
    plt.loglog(r_vals, rho_c / (1000**3), color='blue', linewidth=2, label='Modified (1 kpc Core)')
    
    # Markers
    plt.axvline(r_br, color='red', linestyle='--', label=f'Break Radius ({r_br} kpc)')
    plt.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Amarante et al. 2024: Density Profile with 1 kpc Core', fontsize=14)
    plt.xlabel('Flattened Radius $r_q$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/amarante2024_density_profile.png', dpi=300)
    print("Plot saved to: assets/amarante2024_density_profile.png")

if __name__ == "__main__":
    calculate_amarante2024_halo()
