
## 2023-10-04 Performance Optimization: `orient` function

Identified the `orient` function in `src/mcp/exactgeom.py` as a critical performance bottleneck. It previously instantiated many intermediate `fractions.Fraction` objects and performed expensive GCD computations, which caused the test suite to run for ~110 seconds. I optimized this hot path by directly extracting the integer `.numerator` and `.denominator` components from the point coordinates and evaluating the cross-product sign using purely primitive integer math. This algebraically preserves the exact orientation result while halving the entire test suite's execution time to ~33-55 seconds.
