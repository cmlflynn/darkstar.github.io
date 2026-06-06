import numpy as np
import matplotlib.pyplot as plt

def calculate_amarante2024_halo():
    # Parameters from Amarante et al. (2024) - A&A 690, A166
    # Broken Power Law Profile
    alpha_in = 2.9
    alpha_out = 4.5
    r_br = 19.1
    # Flattening: they assume q=0.77 for r < 30 kpc and q=0.99 otherwise.
    # We'll use an average or the inner value for the luminosity calculation if needed,
    # but for the profile plot we use the flattened radius rq.
    q_inner = 0.77
    q_outer = 0.99
    
    # Solar position (standard value often used if not specified, 8.122 or 8.275)
    # Staf256 uses 8.275, Han uses 8.122. Let's use 8.275.
    R_sun = 8.275 

    # User local norm
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # Broken Power Law Profile Function (rq = sqrt(x^2 + y^2 + (z/q)^2))
    def profile(r):
        if r < r_br:
            return r**-alpha_in
        else:
            return (r_br**(alpha_out - alpha_in)) * (r**-alpha_out)

    # Normalization at the Sun
    # Note: Amarante uses rq. At the Sun, z=0 so rq = R_sun regardless of q.
    norm_at_sun = profile(R_sun)
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Analytical Integration for Luminosity
    # L = 4 * pi * q * Integral[ rho(r) * r^2 dr ]
    # Since q changes, we split the integral at 30 kpc or r_br?
    # Actually, the profile is defined in terms of rq.
    # L = 4 * pi * q * Integral[ rho(rq) * rq^2 drq ]
    
    # Part 1: 0 to r_br (using q_inner)
    int1 = (r_br**(3 - alpha_in)) / (3 - alpha_in)
    L1 = 4 * np.pi * q_inner * rho_0 * int1
    
    # Part 2: r_br to 30 kpc (using q_inner)
    C = r_br**(alpha_out - alpha_in)
    int2 = C * (30**(3 - alpha_out) - r_br**(3 - alpha_out)) / (3 - alpha_out)
    L2 = 4 * np.pi * q_inner * rho_0 * int2
    
    # Part 3: 30 kpc to infinity (using q_outer)
    int3 = C * (0 - 30**(3 - alpha_out)) / (3 - alpha_out)
    L3 = 4 * np.pi * q_outer * rho_0 * int3
    
    L_total = L1 + L2 + L3

    print(f"--- Amarante et al. (2024) BHB Halo Properties ---")
    print(f"Central Norm (at 1kpc): {rho_0:.2e} Lsun/kpc^3")
    print(f"Total Halo Luminosity:  {L_total:.2e} Lsun")
    print(f"Break Radius:           {r_br} kpc")
    print(f"Inner Slope (alpha):    {alpha_in}")
    print(f"Outer Slope (alpha):    {alpha_out}")
    print(f"---------------------------------------------------")

    # Plotting
    r_vals = np.logspace(0.5, 2.2, 500)
    rho_vals = np.array([rho_0 * profile(r) for r in r_vals])

    plt.figure(figsize=(10, 7))
    plt.loglog(r_vals, rho_vals / (1000**3), color='blue', linewidth=2, label='Amarante et al. (2024) BHB Model')
    
    # Markers
    plt.axvline(r_br, color='red', linestyle='--', label=f'Break Radius ({r_br} kpc)')
    plt.axvline(R_sun, color='black', linestyle=':', alpha=0.5, label='Solar Position')
    plt.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.2, label='Local Normalization')

    plt.title('Milky Way Stellar Halo Density Profile (Amarante et al. 2024)', fontsize=14)
    plt.xlabel('Flattened Radius $r_q$ [kpc]', fontsize=12)
    plt.ylabel('Luminosity Density [$L_\\odot/pc^3$]', fontsize=12)
    plt.legend(frameon=True)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('assets/amarante2024_density_profile.png', dpi=300)
    print("Plot saved to: assets/amarante2024_density_profile.png")

if __name__ == "__main__":
    calculate_amarante2024_halo()
