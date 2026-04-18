from os.path import join
import sys
import matplotlib.pyplot as plt
import numpy as np


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)

    for _ in range(max_iter):
        u_new = 0.25 * (
            u[1:-1, :-2]
            + u[1:-1, 2:]
            + u[:-2, 1:-1]
            + u[2:, 1:-1]
        )

        u_new_interior = u_new[interior_mask]

        delta = np.abs(
            u[1:-1, 1:-1][interior_mask] - u_new_interior
        ).max()

        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break

    return u


if __name__ == "__main__":

    LOAD_DIR = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"

    with open(join(LOAD_DIR, "building_ids.txt"), "r") as f:
        building_ids = f.read().splitlines()

    # Number of buildings and iterations
    if len(sys.argv) < 2:
        N = 3
    else:
        N = int(sys.argv[1])

    building_ids = building_ids[:N]

    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype=bool)
    all_u = np.empty((N, 514, 514))

    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask
        all_u[i] = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)

    # ===============================#
     # task 1: visualize input data #
    # ==============================#
    for i, bid in enumerate(building_ids[:3]):

        u0 = all_u0[i]
        interior_mask = all_interior_mask[i]

        plt.figure()
        plt.imshow(u0[1:-1, 1:-1], cmap="inferno", vmin=5, vmax=25)
        plt.colorbar(label="Temperature (°C)")
        plt.title(f"Floorplan {i+1} – domain")
        plt.savefig(f"floorplan{i+1}_domain.png", dpi=200, bbox_inches="tight")
        plt.close()

        plt.figure()
        plt.imshow(interior_mask, cmap="gray")
        plt.colorbar(label="Interior mask")
        plt.title(f"Floorplan {i+1} – interior mask")
        plt.savefig(f"floorplan{i+1}_mask.png", dpi=200, bbox_inches="tight")
        plt.close()

    # =========================
    # task 3: visualize simulation results
    # =========================
    for i, bid in enumerate(building_ids[:3]):

        u = all_u[i]

        plt.figure()
        plt.imshow(u[1:-1, 1:-1], cmap="inferno", vmin=5, vmax=25)
        plt.colorbar(label="Temperature (°C)")
        plt.title(f"Floorplan {i+1} – temperature distribution")
        plt.savefig(
            f"floorplan{i+1}_temperature.png",
            dpi=200,
            bbox_inches="tight",
        )
        plt.close()
