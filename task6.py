from os.path import join
import sys
import numpy as np
from multiprocessing import Pool


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


# Worker function for dynamic scheduling
def process_single(args):
    # Now it only receives One bid (building) at a time
    bid, load_dir, max_iter, atol = args
    
    u0, interior_mask = load_data(load_dir, bid)
    u = jacobi(u0, interior_mask, max_iter, atol)
    stats = summary_stats(u, interior_mask)
    
    return (bid, stats)


if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'

    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    # Limit to max 100 floorplans
    if len(sys.argv) < 2:
        N = 1
        n_workers = 1
    else:
        N = min(int(sys.argv[1]), 100)
        n_workers = int(sys.argv[2])
        
    print(f"N= {N}")
    print(f"n_workers= {n_workers}")
    building_ids = building_ids[:N]

    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    
    # Create arguments for each floorplan individually, no batching (creates a giant queue of 100 individual tasks, one for each building)
    args = [
        (bid, LOAD_DIR, MAX_ITER, ABS_TOL)
        for bid in building_ids
    ]

    # Parallel execution (MODIFIED)
    with Pool(processes=n_workers) as pool:
        # chunksize=1 is the magic dynamic scheduling parameter.
        # It forces workers to take exactly 1 item, process it, and ask for the next.
        results = pool.map(process_single, args, chunksize=1)


    # --- Output ---
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    # print('building_id, ' + ', '.join(stat_keys))
    # for bid, stats in results:
    #     print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))