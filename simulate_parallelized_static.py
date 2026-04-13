from os.path import join
import sys
import numpy as np
from multiprocessing import Pool, cpu_count


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)

    for _ in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] +
                        u[:-2, 1:-1] + u[2:, 1:-1])

        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break

    return u


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    return {
        'mean_temp': u_interior.mean(),
        'std_temp': u_interior.std(),
        'pct_above_18': np.sum(u_interior > 18) / u_interior.size * 100,
        'pct_below_15': np.sum(u_interior < 15) / u_interior.size * 100,
    }


# --- Worker function ---
def process_batch(args):
    bids, load_dir, max_iter, atol = args
    results = []

    for bid in bids:
        u0, interior_mask = load_data(load_dir, bid)
        u = jacobi(u0, interior_mask, max_iter, atol)
        stats = summary_stats(u, interior_mask)
        results.append((bid, stats))

    return results


if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'

    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    # Limit to max 100 floorplans
    if len(sys.argv) < 2:
        N = 1
    else:
        N = min(int(sys.argv[1]), 100)
        n_workers = int(sys.argv[2])
    print(N)
    print("n_workers= ", n_workers )
    building_ids = building_ids[:N]

    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    # --- Static scheduling ---
    chunk_size = (N + n_workers - 1) // n_workers  # ceil division
   

    batches = [
        building_ids[i:i + chunk_size]
        for i in range(0, N, chunk_size)
    ]

    args = [
        (batch, LOAD_DIR, MAX_ITER, ABS_TOL)
        for batch in batches
    ]

    # --- Parallel execution ---
    with Pool(processes=n_workers) as pool:
        results = pool.map(process_batch, args)

    # Flatten results
    results = [item for sublist in results for item in sublist]

    # --- Output ---
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    #print('building_id, ' + ', '.join(stat_keys))

    #for bid, stats in results:
        #print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))