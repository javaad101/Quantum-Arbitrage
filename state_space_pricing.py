"""
State-Space Pricing, Waterfall Double-Counting, and CHSH Quantum Correlations
Author: Javaad Ali

Executable numerical verification accompanying:
  "Why Common Stock Prevents State-Space Pricing: Rank Deficiency, Waterfall
   Double-Counting, and the Constructive Path to Arrow-Debreu Completeness"

Zero external dependencies (Python 3 standard library only). Verifies:
  1. Proposition 1: Rank deficiency of entity-level common equity (rank(X_eq) <= N < D)
  2. Theorem 1: Eisenberg-Noe simultaneous clearing & positive phantom equity
     (sum E_i^standalone - sum E_i^cleared = Delta_phantom > 0)
  3. Corollary 1: Full-rank pre-waterfall formula primitives (rank(X_prim) = D,
     Delta_phantom = 0) and exact Arrow-Debreu state-price recovery q = X_prim^-1 p
  4. Exact Born-rule CHSH Bell correlation reaching Tsirelson's bound 2*sqrt(2) > 2
"""

from __future__ import annotations
import math


def gaussian_elimination_rank(matrix: list[list[float]], tol: float = 1e-10) -> int:
    m = [list(row) for row in matrix]
    rows, cols = len(m), len(m[0])
    rank = 0
    for c in range(cols):
        pivot = None
        for r in range(rank, rows):
            if abs(m[r][c]) > tol:
                pivot = r
                break
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        piv_val = m[rank][c]
        m[rank] = [x / piv_val for x in m[rank]]
        for r in range(rows):
            if r != rank and abs(m[r][c]) > tol:
                factor = m[r][c]
                m[r] = [m[r][j] - factor * m[rank][j] for j in range(cols)]
        rank += 1
    return rank


def solve_linear_system(A: list[list[float]], b: list[float]) -> list[float]:
    """Solves A x = b via Gauss-Jordan elimination with partial pivoting."""
    n = len(A)
    aug = [list(A[i]) + [b[i]] for i in range(n)]
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(aug[r][i]))
        aug[i], aug[pivot] = aug[pivot], aug[i]
        piv = aug[i][i]
        if abs(piv) < 1e-12:
            raise ValueError("Singular payoff matrix: state prices are not uniquely invertible.")
        aug[i] = [val / piv for val in aug[i]]
        for r in range(n):
            if r != i:
                f = aug[r][i]
                aug[r] = [aug[r][c] - f * aug[i][c] for c in range(n + 1)]
    return [aug[i][n] for i in range(n)]


def eisenberg_noe_clearing(
    physical_assets: list[float],
    liabilities: list[list[float]],
    tol: float = 1e-12,
    max_iter: int = 500,
) -> tuple[list[float], list[float], list[float]]:
    """
    Computes simultaneous bankruptcy clearing payments p* under Eisenberg & Noe (2001),
    returning (standalone_equity, cleared_equity, clearing_payments).

    liabilities[i][j] = gross obligation owed by firm i to firm j.
    """
    n = len(physical_assets)
    p_bar = [sum(liabilities[i]) for i in range(n)]
    pi = [
        [liabilities[i][j] / p_bar[i] if p_bar[i] > 0 else 0.0 for j in range(n)]
        for i in range(n)
    ]

    # Standalone accounting assumes full book recovery on all inbound receivables
    standalone_eq = [
        max(0.0, physical_assets[i] + sum(liabilities[j][i] for j in range(n) if j != i) - p_bar[i])
        for i in range(n)
    ]

    # Simultaneous fixed-point clearing: p = min(p_bar, A + Pi^T p)
    p = list(p_bar)
    for _ in range(max_iter):
        p_next = [
            min(p_bar[i], max(0.0, physical_assets[i] + sum(pi[j][i] * p[j] for j in range(n))))
            for i in range(n)
        ]
        if max(abs(p_next[i] - p[i]) for i in range(n)) < tol:
            p = p_next
            break
        p = p_next

    cleared_eq = [
        max(0.0, physical_assets[i] + sum(pi[j][i] * p[j] for j in range(n)) - p_bar[i])
        for i in range(n)
    ]
    return standalone_eq, cleared_eq, p


def construct_formula_primitives() -> tuple[list[list[float]], list[float]]:
    """
    Constructs 4 linearly independent pre-waterfall formula primitives spanning a
    D = 4 coupled 2-enterprise state space Omega = {omega_0, omega_1, omega_2, omega_3}
    that partition aggregate physical surplus Y(omega) identically (Delta_phantom = 0).
    """
    # Coupled physical state space Omega (D = 4 states):
    #   omega_0: systemic distress (A1=20, A2=10) -> Y=30
    #   omega_1: anchor solvent, supplier constrained (A1=60, A2=25) -> Y=85
    #   omega_2: moderate expansion (A1=90, A2=45) -> Y=135
    #   omega_3: high-throughput saturation (A1=140, A2=70) -> Y=210
    x1 = [20.0, 60.0, 90.0, 140.0]
    Y = [30.0, 85.0, 135.0, 210.0]

    tau = 50.0
    mu = 85.0
    alpha = 12.0
    beta = 30.0
    gamma = 0.08

    def sigmoid(z: float) -> float:
        return 1.0 / (1.0 + math.exp(-z))

    x_base = [min(val, tau) for val in x1]
    x_sat = [beta * sigmoid(gamma * (val - mu)) for val in x1]
    x_tail = [alpha * (1.0 if val < tau else 0.0) for val in x1]
    x_net = [Y[w] - (x_base[w] + x_sat[w] + x_tail[w]) for w in range(4)]

    X_prim = [x_base, x_sat, x_tail, x_net]
    return X_prim, Y


def chsh_tsirelson_value() -> float:
    """
    Analytical Born-rule CHSH S-parameter on Bell state |Phi^+> at optimal
    measurement angles (a0=0, a1=pi/2, b0=pi/4, b1=-pi/4), where E(a,b) = cos(2(a-b))
    for polarization / cos(a-b) on Bloch-sphere spin observables -> |S| = 2*sqrt(2).
    """
    a0, a1 = 0.0, math.pi / 2.0
    b0, b1 = math.pi / 4.0, -math.pi / 4.0

    def corr(theta_a: float, theta_b: float) -> float:
        return math.cos(theta_a - theta_b)

    return abs(corr(a0, b0) + corr(a0, b1) + corr(a1, b0) - corr(a1, b1))


if __name__ == "__main__":
    # 1. Theorem 1: Phantom equity in a 3-node network + external senior claimants (node 3)
    # Firm 0 (insolvent anchor) owes 40 to Firm 1 and 20 to external bondholders (node 3).
    # Firm 1 owes 35 to Firm 2; Firm 2 owes 30 to Firm 1.
    assets_sys = [5.0, 10.0, 10.0, 0.0]
    liabilities = [
        [0.0, 40.0, 0.0, 20.0],
        [0.0, 0.0, 35.0, 0.0],
        [0.0, 30.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
    ]
    standalone, cleared, _ = eisenberg_noe_clearing(assets_sys, liabilities)
    # Sum equity across the 3 corporate issuers (excluding external bondholder sink node 3)
    standalone_corp = sum(standalone[:3])
    cleared_corp = sum(cleared[:3])
    phantom = standalone_corp - cleared_corp

    # 2. Proposition 1 & Corollary 1: Rank deficiency vs. Exact Arrow-Debreu inversion
    X_eq_2firms_4states = [
        [0.0, 15.0, 45.0, 95.0],
        [0.0, 5.0, 25.0, 50.0],
    ]
    rank_eq = gaussian_elimination_rank(X_eq_2firms_4states)

    X_prim, Y = construct_formula_primitives()
    rank_prim = gaussian_elimination_rank(X_prim)
    true_q = [0.35, 0.28, 0.20, 0.12]
    market_prices = [sum(X_prim[k][w] * true_q[w] for w in range(4)) for k in range(4)]
    recovered_q = solve_linear_system(
        [[X_prim[k][w] for w in range(4)] for k in range(4)],
        market_prices,
    )

    print(f"Proposition 1 — Rank of 2-stock payoff matrix on D=4 states: {rank_eq} < 4")
    print(f"Theorem 1     — Standalone equity sum: {standalone_corp:.2f}, Cleared equity sum: {cleared_corp:.2f}, Phantom equity: {phantom:.2f} > 0")
    print(f"Corollary 1   — Rank of formula primitives X_prim: {rank_prim} == 4")
    print(f"Corollary 1   — Max state-price inversion error ||q_hat - q||_inf: {max(abs(recovered_q[i] - true_q[i]) for i in range(4)):.2e}")
    print(f"CHSH Bound    — Quantum Bell S-parameter: {chsh_tsirelson_value():.6f} (classical bound = 2.0)")
