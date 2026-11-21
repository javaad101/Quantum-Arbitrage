# Quantum & State-Space Asset Pricing

Working paper, Bell/CHSH entanglement experiments (originally executed under an IBM Quantum hardware grant and ported to local Objective-C / Python numerical kernels), and constructive Arrow–Debreu state-price verification.

## Working Paper

- **[Why Common Stock Prevents State-Space Pricing: Rank Deficiency, Waterfall Double-Counting, and the Constructive Path to Arrow–Debreu Completeness](paper/Why_Common_Stock_Prevents_State_Space_Pricing.pdf)** ([LaTeX source](paper/state_space_pricing.tex))
  - **Proposition 1 (Rank Deficiency & Partial-Trace Contraction):** Demonstrates why $N$ entity-level common stocks compressing coupled operational states via $p_i(t) = \operatorname{Re}(\operatorname{Tr}_{-i}[\hat{O}_i \rho(t)])_{g_t}$ satisfy $\operatorname{rank}(X_{\mathrm{eq}}) \le N \ll D$, leaving Arrow–Debreu state prices $\bm{q}_t$ unidentifiable in a $(D - N)$-dimensional nullspace.
  - **Theorem 1 (Phantom Equity Under Simultaneous Liquidation):** Proves via Eisenberg–Noe fixed-point clearing that standalone corporate equity double-counts bilateral receivables across entity boundaries, producing strictly positive phantom equity ($\Delta_{\mathrm{phantom}}(\omega_{\mathrm{sys}}) > 0$) that vanishes under simultaneous default.
  - **Corollary 1 (Formula-Defined Pre-Waterfall State Primitives):** Constructs linearly independent pre-waterfall contingent claims $\{x_{\mathrm{base}}, x_{\mathrm{sat}}, x_{\mathrm{tail}}, x_{\mathrm{net}}\}$ that partition aggregate physical output identically ($\Delta_{\mathrm{phantom}} \equiv 0$) and render $\bm{q}_t = X_{\mathrm{prim}}^{-1}\bm{p}_t$ uniquely invertible.

## Repository Contents

- `paper/` — Typeset PDF and LaTeX source (`state_space_pricing.tex`)
- `state_space_pricing.py` — Zero-dependency numerical verification of Proposition 1, Theorem 1 (Eisenberg–Noe fixed-point clearing), Corollary 1 (exact state-price inversion), and CHSH Bell violation ($S = 2\sqrt{2} > 2$)
- `tests/test_state_space_pricing.py` — Unit test suite verifying all analytical bounds
- `Javaad-Ali-Quantum-Asset-Pricing/` — macOS Objective-C CHSH Bell simulator & portfolio prototype

## Running Verification Suite

Requires only standard-library Python 3:

```bash
python3 state_space_pricing.py
python3 -m unittest -v tests/test_state_space_pricing.py
```
