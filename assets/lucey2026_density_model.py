import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.integrate import quad
import os

def calculate_lucey2026_halo():
    # Parameters from Table 1 of Lucey et al. (2026) - AJ, 171, 249
    # Hierarchical Bayesian Gaussian Mixture Model (GMM)
    A = 0.37
    q_ig = 1.311
    q_halo = 0.697
    alpha_deg = 17.7
    phi_deg = -27.2
    
    alpha = np.radians(alpha_deg)
    phi = np.radians(phi_deg)
    
    # Amplitudes (Table 1)
    A_IG = np.array([7.00e-2, 6.53e-2, 6.03e-2, 5.05e-2, 7.53e-1])
    A_H = np.array([9.99e-5, 1.14e-4, 5.60e-2, 7.70e-1, 1.32e-1, 4.25e-2])
    
    # Normalize amplitudes
    A_IG = A_IG / np.sum(A_IG)
    A_H = A_H / np.sum(A_H)
    
    k_ig = 0.1
    k_halo = 1.5  # kpc
    r_core = 1.0  # 1 kpc constant density core (project requirement)
    
    # Calculate S factor for halo rotation along observer major axis (X-axis)
    S = (np.cos(alpha)*np.cos(phi))**2 + np.sin(alpha)**2 + ((np.cos(alpha)*np.sin(phi))**2 / q_halo**2)
    q_eff_halo = q_halo * (S**1.5)
    
    # Local normalisation parameters
    R_sun = 8.275 
    rho_local_Lsun_pc3 = 1.7e-5
    rho_local_Lsun_kpc3 = rho_local_Lsun_pc3 * (1000**3)

    # 1D density profile along x-axis (raw model)
    def rho_1D_raw(r):
        # Inner Galaxy components
        rho_ig = 0.0
        for j in range(5):
            sigma_xy = k_ig * (2.0**j)
            sigma_z = q_ig * sigma_xy
            det_cov = (sigma_xy**2) * sigma_z
            norm = 1.0 / (((2.0 * np.pi)**1.5) * det_cov)
            rho_ig += A_IG[j] * norm * np.exp(-0.5 * (r**2 / sigma_xy**2))
            
        # Halo components
        rho_halo = 0.0
        for j in range(6):
            sigma_xy = k_halo * (2.0**j)
            sigma_z = q_halo * sigma_xy
            det_cov = (sigma_xy**2) * sigma_z
            norm = 1.0 / (((2.0 * np.pi)**1.5) * det_cov)
            exponent = -0.5 * (r**2 / sigma_xy**2) * S
            rho_halo += A_H[j] * norm * np.exp(exponent)
            
        return (1.0 - A) * rho_halo + A * rho_ig

    # Effective flattening q_eff(r)
    def q_eff(r):
        rho_ig = 0.0
        for j in range(5):
            sigma_xy = k_ig * (2.0**j)
            sigma_z = q_ig * sigma_xy
            det_cov = (sigma_xy**2) * sigma_z
            norm = 1.0 / (((2.0 * np.pi)**1.5) * det_cov)
            rho_ig += A_IG[j] * norm * np.exp(-0.5 * (r**2 / sigma_xy**2))
            
        rho_halo = 0.0
        for j in range(6):
            sigma_xy = k_halo * (2.0**j)
            sigma_z = q_halo * sigma_xy
            det_cov = (sigma_xy**2) * sigma_z
            norm = 1.0 / (((2.0 * np.pi)**1.5) * det_cov)
            exponent = -0.5 * (r**2 / sigma_xy**2) * S
            rho_halo += A_H[j] * norm * np.exp(exponent)
            
        tot_rho = (1.0 - A) * rho_halo + A * rho_ig
        return ((1.0 - A) * rho_halo * q_eff_halo + A * rho_ig * q_ig) / (tot_rho + 1e-30)

    # 3D Density function for slices
    def density_3D_raw(x, y, z):
        # Coordinates in rotated halo frame
        # Using orthonormal rotation matrix R_rot^T
        x_prime = x * np.cos(alpha)*np.cos(phi) + y * np.sin(phi) - z * np.sin(alpha)*np.cos(phi)
        y_prime = -x * np.sin(alpha) - z * np.cos(alpha)
        z_prime = -x * np.cos(alpha)*np.sin(phi) + y * np.cos(phi) + z * np.sin(alpha)*np.sin(phi)
        
        # Inner Galaxy GMM components (unrotated)
        rho_ig = 0.0
        for j in range(5):
            sigma_xy = k_ig * (2.0**j)
            sigma_z = q_ig * sigma_xy
            det_cov = (sigma_xy**2) * sigma_z
            norm = 1.0 / (((2.0 * np.pi)**1.5) * det_cov)
            exponent = -0.5 * ((x**2 + y**2) / sigma_xy**2 + z**2 / sigma_z**2)
            rho_ig += A_IG[j] * norm * np.exp(exponent)
            
        # Halo GMM components (rotated)
        rho_halo = 0.0
        for j in range(6):
            sigma_xy = k_halo * (2.0**j)
            sigma_z = q_halo * sigma_xy
            det_cov = (sigma_xy**2) * sigma_z
            norm = 1.0 / (((2.0 * np.pi)**1.5) * det_cov)
            exponent = -0.5 * ((x_prime**2 + y_prime**2) / sigma_xy**2 + z_prime**2 / sigma_z**2)
            rho_halo += A_H[j] * norm * np.exp(exponent)
            
        return (1.0 - A) * rho_halo + A * rho_ig

    # Regularized 3D density (with 1 kpc core)
    def density_3D_regularized(x, y, z):
        r = np.sqrt(x**2 + y**2 + z**2)
        r_clamped = np.maximum(r, r_core)
        r_div = np.where(r == 0, 1.0, r)
        scale = r_clamped / r_div
        return density_3D_raw(x * scale, y * scale, z * scale)

    # Normalisation factor
    norm_at_sun = rho_1D_raw(max(R_sun, r_core))
    rho_0 = rho_local_Lsun_kpc3 / norm_at_sun

    # Numerical integration for luminosity
    def integrand(r):
        r_eff = max(r, r_core)
        return q_eff(r_eff) * rho_1D_raw(r_eff) * r**2
    
    # Integrate from 0 to 200 kpc as per website standard
    result, error = quad(integrand, 0.0, 200.0)
    L_total = 4 * np.pi * rho_0 * result

    print(f"--- Lucey et al. (2026) RR Lyrae Halo Properties ---")
    print(f"Model Type:           Bayesian Gaussian Mixture Model (GMM)")
    print(f"Central Norm (rho_0): {rho_0:.2e} Lsun")
    print(f"Total Halo Luminosity: {L_total:.2e} Lsun")
    print(f"Core Radius:          {r_core} kpc")
    print(f"Inner Galaxy Weight:  {A}")
    print(f"Halo Weight:          {1 - A}")
    print(f"Valid range:          0.2 - 120 kpc")
    print(f"-----------------------------------------------------")

    # Set up dark mode plot aesthetics to match NFW template
    plt.style.use('dark_background')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'figure.facecolor': '#0B0D17',    # Custom deep space background
        'axes.facecolor': '#0B0D17',
        'axes.edgecolor': '#2C3043',
        'grid.color': '#2C3043',
        'axes.labelcolor': '#8F99C1',
        'xtick.color': '#8F99C1',
        'ytick.color': '#8F99C1',
        'text.color': '#FFFFFF',
        'axes.titleweight': 'bold',
        'axes.titlepad': 12,
    })

    # Setup Figure Layout (2x2 Grid)
    fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=150)
    fig.suptitle("Stellar Halo Density Profile & Slices (Lucey et al. 2026 GMM)", 
                 fontsize=18, color='#00E5FF', y=0.96, weight='bold')

    # 1. Top-Left Panel: 1D Radial Density Falloff (0.1 to 100 kpc)
    ax1d = axes[0, 0]
    r_range = np.logspace(-1, 2, 500) # 0.1 kpc to 100 kpc
    
    # Calculate profiles along observer coordinate axes
    rho_x = np.array([rho_0 * density_3D_regularized(r, 0, 0) for r in r_range])
    rho_y = np.array([rho_0 * density_3D_regularized(0, r, 0) for r in r_range])
    rho_z = np.array([rho_0 * density_3D_regularized(0, 0, r) for r in r_range])

    # Convert to Lsun/pc3 for visual display
    ax1d.loglog(r_range, rho_x / (1000**3), label='Observer X-axis (Major)', color='#FF007F', linewidth=2.5)
    ax1d.loglog(r_range, rho_y / (1000**3), label='Observer Y-axis', color='#00E5FF', linewidth=2.0, linestyle='--')
    ax1d.loglog(r_range, rho_z / (1000**3), label='Observer Z-axis', color='#FFD700', linewidth=2.0, linestyle=':')
    
    # Shade valid range up to plotted range (0.2 to 100 kpc)
    ax1d.axvspan(0.2, 100.0, color='lightblue', alpha=0.1, label='Valid Data Range (0.2-120 kpc)')
    ax1d.axvline(r_core, color='purple', linestyle=':', label=f'Core Radius ({r_core} kpc)')
    ax1d.axvline(R_sun, color='white', linestyle='-.', alpha=0.4, label='Solar Position')
    ax1d.axhline(rho_local_Lsun_pc3, color='green', linestyle='-', alpha=0.15, label='Local Normalization')

    ax1d.set_title("1D Radial Density Falloff", fontsize=14)
    ax1d.set_xlabel("Radius $r$ [kpc]", fontsize=12)
    ax1d.set_ylabel(r"Luminosity Density [$L_\odot/pc^3$]", fontsize=12)
    ax1d.set_xlim(0.1, 100.0)
    ax1d.set_ylim(1e-12, 1e-2)
    ax1d.legend(loc='lower left', framealpha=0.1, fontsize=9)
    ax1d.grid(True, which="both", linestyle=':', alpha=0.3, color='#2C3043')

    # Generate 2D Slices (-10 to 10 kpc) for other panels
    lim = 10.0
    n_grid = 400
    u = np.linspace(-lim, lim, n_grid)
    grid_x, grid_y = np.meshgrid(u, u)

    # Compute 3D densities scaled to Lsun/pc3
    rho_xy = np.zeros_like(grid_x)
    rho_xz = np.zeros_like(grid_x)
    rho_yz = np.zeros_like(grid_x)
    for i in range(n_grid):
        for idx in range(n_grid):
            rho_xy[i, idx] = rho_0 * density_3D_regularized(grid_x[i, idx], grid_y[i, idx], 0.0) / (1000**3)
            rho_xz[i, idx] = rho_0 * density_3D_regularized(grid_x[i, idx], 0.0, grid_y[i, idx]) / (1000**3)
            rho_yz[i, idx] = rho_0 * density_3D_regularized(0.0, grid_x[i, idx], grid_y[i, idx]) / (1000**3)

    # Use same colour map as in Figure 5 of the Lucey et al. paper (viridis)
    vmin = 1e-7
    vmax = 1.1 * rho_xy.max()
    norm = LogNorm(vmin=vmin, vmax=vmax)
    cmap = 'viridis'

    map_kwargs = {
        'extent': [-lim, lim, -lim, lim],
        'cmap': cmap,
        'norm': norm,
        'origin': 'lower',
        'interpolation': 'bilinear'
    }

    # 2. Top-Right Panel: XY Plane Slice (z=0)
    ax_xy = axes[0, 1]
    im_xy = ax_xy.imshow(rho_xy, **map_kwargs)
    ax_xy.set_title("X-Y Plane Slice ($z=0$)", fontsize=14)
    ax_xy.set_xlabel("X [kpc]", fontsize=12)
    ax_xy.set_ylabel("Y [kpc]", fontsize=12)
    # Add Sun marker
    ax_xy.plot([-R_sun], [0.0], marker='*', color='white', markersize=10, markeredgecolor='black', label='Sun')

    # 3. Bottom-Left Panel: XZ Plane Slice (y=0)
    ax_xz = axes[1, 0]
    im_xz = ax_xz.imshow(rho_xz, **map_kwargs)
    ax_xz.set_title("X-Z Plane Slice ($y=0$)", fontsize=14)
    ax_xz.set_xlabel("X [kpc]", fontsize=12)
    ax_xz.set_ylabel("Z [kpc]", fontsize=12)

    # 4. Bottom-Right Panel: YZ Plane Slice (x=0)
    ax_yz = axes[1, 1]
    im_yz = ax_yz.imshow(rho_yz, **map_kwargs)
    ax_yz.set_title("Y-Z Plane Slice ($x=0$)", fontsize=14)
    ax_yz.set_xlabel("Y [kpc]", fontsize=12)
    ax_yz.set_ylabel("Z [kpc]", fontsize=12)

    # Formatting 2D axes
    for ax in [ax_xy, ax_xz, ax_yz]:
        ax.grid(True, color='#2C3043', alpha=0.3, linestyle=':')
        ax.axhline(0, color='#8F99C1', alpha=0.2, linestyle=':')
        ax.axvline(0, color='#8F99C1', alpha=0.2, linestyle=':')
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_aspect('equal')

    plt.tight_layout(rect=[0, 0, 0.9, 0.94])

    # Unified vertical colorbar on the right
    cbar_ax = fig.add_axes([0.92, 0.1, 0.02, 0.78])
    cbar = fig.colorbar(im_xy, cax=cbar_ax)
    cbar.set_label(r"Luminosity Density [$L_\odot/pc^3$]", rotation=270, labelpad=20, fontsize=12, color='#8F99C1')
    cbar.ax.yaxis.set_tick_params(color='#8F99C1')
    
    # Save the output file
    if os.path.exists('assets'):
        save_path = 'assets/lucey2026_density_profile.png'
    elif os.path.exists('website/assets'):
        save_path = 'website/assets/lucey2026_density_profile.png'
    else:
        save_path = 'lucey2026_density_profile.png'
        
    plt.savefig(save_path, dpi=300, facecolor='#0B0D17', edgecolor='none', bbox_inches='tight')
    print(f"Plot saved to: {save_path}")

if __name__ == "__main__":
    calculate_lucey2026_halo()
