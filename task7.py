from os.path import join
import sys
import numpy as np
from numba import jit
import time


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

@jit(nopython=True)     
def jacobi_jit(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    u_new = np.copy(u)
    rows, cols = u.shape

    for _ in range(max_iter):
        delta = 0.0
        
        # Explicit cache-friendly loops (outer: row, inner: col)
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if interior_mask[i-1, j-1]: 
                    u_new[i, j] = 0.25 * (u[i, j-1] + u[i, j+1] + u[i-1, j] + u[i+1, j])
                    
                    diff = abs(u[i, j] - u_new[i, j])
                    if diff > delta:
                        delta = diff
                        
        # Apply updates back to u
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if interior_mask[i-1, j-1]:
                    u[i, j] = u_new[i, j]

        if delta < atol:
            break
            
    return u

'''
To optimize for the CPU cache, we replaced NumPy slicing with nested loops in the jacobi function.
The outer loop iterates over rows (i) and the inner over columns (j). 
This matches Python/NumPy's C-contiguous (row-major) memory layout, allowing the CPU to read data linearly 
and avoid expensive cache-misses
'''


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }


if __name__ == '__main__':
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    # CHANGE: warm-up run (the first run will include JIT compilation time and will therefore be slower, we will exclude this time)
    print("Compiling Numba function (Warm-up)...", file=sys.stderr)
    _ = jacobi_jit(all_u0[0], all_interior_mask[0], 2, ABS_TOL)

    # CHANGE: real timing starts here
    t0 = time.time()

    all_u = np.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u = jacobi_jit(u0, interior_mask, MAX_ITER, ABS_TOL)
        all_u[i] = u
    
    # CHANGE: real timing ends here
    t1 = time.time()
    print(f"Pure Numba Time: {t1 - t0:.4f} seconds", file=sys.stderr)

    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))

# Note: time was measured internally after a warm-up run to exclude JIT compilation overhead. (Dont know if this is correct)