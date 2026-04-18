from os.path import join
import sys
from time import perf_counter as time
import numpy as np
from numba import cuda


# --------------------------------------------------
# Constants
# --------------------------------------------------

SIZE = 512
PADDED_SIZE = SIZE + 2
TOTAL_BUILDINGS = 4571


# --------------------------------------------------
# Load data
# --------------------------------------------------

def load_data(load_dir, bid):

    # Allocate padded grid 
    u = np.zeros((PADDED_SIZE, PADDED_SIZE), dtype=np.float32)

    # Insert domain values (walls + interior)
    u[1:-1, 1:-1] = np.load(
        join(load_dir, f"{bid}_domain.npy")
    ).astype(np.float32)

    # Load mask marking interior grid points
    interior_mask = np.load(
        join(load_dir, f"{bid}_interior.npy")
    ).astype(np.uint8)

    return u, interior_mask


# --------------------------------------------------
# Reference Jacobi solver (CPU implementation)
# --------------------------------------------------

def jacobi_reference(u, interior_mask, max_iter):

    # Copy input grid
    u = np.array(u, copy=True, dtype=np.float32)

    # Boolean mask for interior points
    mask = interior_mask != 0

    # Perform fixed number of Jacobi iterations
    for _ in range(max_iter):

        # Compute neighbor average
        u_new = 0.25 * (
            u[1:-1, :-2] +
            u[1:-1, 2:] +
            u[:-2, 1:-1] +
            u[2:, 1:-1]
        )

        # Update interior points only
        u[1:-1, 1:-1][mask] = u_new[mask]

    return u


# --------------------------------------------------
# CUDA kernel: performs ONE Jacobi iteration
# --------------------------------------------------

# CUDA decorator
@cuda.jit
def jacobi_step_kernel(u_old, u_new, interior_mask):

    # 2D thread index
    i, j = cuda.grid(2)

    # Check grid bounds
    if i < interior_mask.shape[0] and j < interior_mask.shape[1]:

        # Shift indices because of padded boundary
        ii = i + 1
        jj = j + 1

        # Update only interior points
        if interior_mask[i, j] != 0:

            u_new[ii, jj] = 0.25 * (
                u_old[ii, jj - 1] +
                u_old[ii, jj + 1] +
                u_old[ii - 1, jj] +
                u_old[ii + 1, jj]
            )

        # Keep boundary values unchanged
        else:
            u_new[ii, jj] = u_old[ii, jj]


# --------------------------------------------------
# Helper function: runs Jacobi solver on GPU
# Calls kernel once per iteration
# --------------------------------------------------

def jacobi_cuda(u, interior_mask, max_iter):

    # Copy arrays to device memory
    d_u_old = cuda.to_device(u.astype(np.float32))
    d_u_new = cuda.device_array_like(d_u_old)
    d_mask = cuda.to_device(interior_mask.astype(np.uint8))

    # Define thread block size
    threadsperblock = (16, 16)

    # Compute number of blocks needed
    blockspergrid = (
        (interior_mask.shape[0] + threadsperblock[0] - 1)
        // threadsperblock[0],
        (interior_mask.shape[1] + threadsperblock[1] - 1)
        // threadsperblock[1],
    )

    
    for _ in range(max_iter):

        # Launch kernel 
        jacobi_step_kernel[
            blockspergrid,
            threadsperblock
        ](d_u_old, d_u_new, d_mask)

        # Swap buffers
        d_u_old, d_u_new = d_u_new, d_u_old

    # Ensure all GPU work is finished
    cuda.synchronize()

    # Copy result back to host memory
    return d_u_old.copy_to_host()


# --------------------------------------------------
# Main program: timing comparison CPU vs GPU
# --------------------------------------------------

if __name__ == "__main__":

    LOAD_DIR = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"

    
    with open(join(LOAD_DIR, "building_ids.txt"), "r") as f:
        building_ids = f.read().splitlines()

    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    MAX_ITER = int(sys.argv[2]) if len(sys.argv) > 2 else 20000

    building_ids = building_ids[:N]

    print(f"\nRunning {N} buildings")
    print(f"Iterations per building: {MAX_ITER}\n")

    
    all_u0 = []
    all_masks = []

    for bid in building_ids:
        u0, mask = load_data(LOAD_DIR, bid)
        all_u0.append(u0)
        all_masks.append(mask)

    # ---------------- CPU timing ----------------

    print("Timing reference CPU version...")

    t0 = time()

    for u0, mask in zip(all_u0, all_masks):
        jacobi_reference(u0, mask, MAX_ITER)

    t1 = time()

    ref_time = t1 - t0

    # ---------------- GPU timing ----------------

    print("Timing CUDA version...")

    cuda.synchronize()
    t2 = time()

    for u0, mask in zip(all_u0, all_masks):
        jacobi_cuda(u0, mask, MAX_ITER)

    cuda.synchronize()
    t3 = time()

    cuda_time = t3 - t2

    # ---------------- Results ----------------

    speedup = ref_time / cuda_time

    ref_total = ref_time * TOTAL_BUILDINGS / N
    cuda_total = cuda_time * TOTAL_BUILDINGS / N

    print("\nPerformance comparison")
    print("----------------------")
    print(f"Buildings processed: {N}")
    print(f"Reference time: {ref_time:.3f} s")
    print(f"CUDA time: {cuda_time:.3f} s")
    print(f"Speedup: {speedup:.2f}x")

    print(f"\nEstimated runtime for all {TOTAL_BUILDINGS} buildings:")
    print(f"Reference: {ref_total:.1f} seconds")
    print(f"CUDA: {cuda_total:.1f} seconds")
    print(f"CUDA: {cuda_total/60:.1f} minutes")
    print(f"CUDA: {cuda_total/3600:.2f} hours")