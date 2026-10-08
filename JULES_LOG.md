
## 2023-10-04 Performance Optimization: `orient` function

Identified the `orient` function in `src/mcp/exactgeom.py` as a critical performance bottleneck. It previously instantiated many intermediate `fractions.Fraction` objects and performed expensive GCD computations, which caused the test suite to run for ~110 seconds. I optimized this hot path by directly extracting the integer `.numerator` and `.denominator` components from the point coordinates and evaluating the cross-product sign using purely primitive integer math. This algebraically preserves the exact orientation result while halving the entire test suite's execution time to ~33-55 seconds.

### 2026-10-05: Performance Optimization in Convex Position Subsets

Optimized the performance of `forbidden_quadruples` and `maximal_convex_subsets_fast` in `src/mcp/convexposition.py`. The original implementation of `forbidden_quadruples` performed O(N^4) calls to the geometric orientation primitive (`orient`) from scratch. I improved this by precomputing the chirotope orientations (all triplets) upfront, evaluating point-in-triangle queries directly from the dictionary, changing the time complexity to essentially O(N^3) with fast dict lookups. Furthermore, I inlined the inner logic of `compatible` into `rec` within the branch-on-addable-vertex routine (`maximal_convex_subsets_fast`), changing standard python subsets into integers bitmasks during recursive calls, dropping functional and memory overhead by avoiding massive scale recursive function call allocations. These changes combined reduce computing times by roughly 3-4x in complex general-position configurations.

### 2026-10-07: Performance Optimization in Convex Position Subsets

Identified the `maximal_convex_subsets_fast` function in `src/mcp/convexposition.py` as a critical performance bottleneck. Optimized its inner loop by precomputing bit lengths in a dictionary (`bit_len_dict`), which eliminates the overhead of `.bit_length()`. Also deduplicated elements in `by_vertex` by converting them to `tuple` of `tuple`s, bypassing list iteration overheads. These algorithmic and structural adjustments yielded a roughly 2x performance increase on the benchmark suite `test_fast_agreement.py` execution time, reducing its runtime from ~32s to ~14.8s.

### 2026-10-08: Performance optimization in convex hull sorting

Optimized the primary point sorting bottleneck in `convex_hull_vertices` by introducing a hybrid float-fraction sorting key (`key=lambda i: (float(Q[i][0]), float(Q[i][1]), Q[i][0], Q[i][1])`). This change drastically reduces the number of slow Python `fractions.Fraction` comparisons by using floating-point approximations for fast sorting, falling back to exact rational values only when coordinates are numerically close. The optimization cuts the overall test suite time from 34s to 29s and improves the performance of the heaviest calculations without compromising the exact arithmetic guarantees.
