# Economic Model Specification

**Version 1 & 2 — Oligopolistic Industry Simulator**

---

## Core Economic Objective

Each firm maximizes long-run discounted profit under competitive pressure and regulatory constraint:

$$\pi_i(t) = P_i(t) \cdot Q_i(t) - C_m(t) \cdot Q_i(t) - k \cdot (R&D_i(t))^2 - C_{capital} - (C_{fixed} + \tau \cdot Q_i(t))$$

---

## Market Demand System

### Base Demand (Macroeconomic)
```
D_base(t) = D_0 · EconomicCycle(t)

where:
  D_0 = 1000 units (base market size)
  EconomicCycle ∈ {0.8 (recession), 1.2 (boom)}
  Markov(p_11=0.95, p_12=0.05, p_21=0.1, p_22=0.9) + Normal(1, 0.02)
```

### Effective Demand (Market Dynamics)
```
D_effective(t) = D_base(t) · exp(-ε · P_avg(t)) · (1 - SubstitutePressure(t))

where:
  ε = 0.015 (price elasticity of demand)
  P_avg = average market price
  SubstitutePressure: random walk in [0.05, 0.3], drift σ=0.005
```

### Firm Quantity
```
Q_i = S_i · D_effective

where S_i = market share (see below)
```

---

## Market Share Allocation (Competitive Rivalry)

Soft competition function (Bertrand oligopoly with product differentiation):

$$S_i(t) = \frac{\exp(-\alpha \cdot P_i(t) + \beta(t) \cdot I_i(t))}{\sum_j \exp(-\alpha \cdot P_j(t) + \beta(t) \cdot I_j(t))}$$

**Parameters:**
```
α = 0.03 (price sensitivity / price elasticity coefficient)
β(t) = 1.5 · TechProgress(t) · DiminishingReturns(I_total)
     = 1.5 · (1 + 0.002·t) · (1 + 0.01·I_total)^-1

Interpretation:
- Higher price → lower market share (buyer power)
- Higher innovation → higher market share (tech advantage)
- β increases over time (tech progress)
- β diminishes as total innovation saturates
```

---

## Cost Structure

### Marginal Production Cost
```
C_m(t) = C_base · SupplierShock(t) · RegulationFactor(t)

where:
  C_base = 80 $/unit (base manufacturing + logistics cost)
  SupplierShock(t) ~ LogNormal(μ=0, σ=0.05)
    Models: input volatility, logistics disruptions, raw material shocks
  RegulationFactor(t) = function of regulatory regime
```

### Capital Cost (Fixed)
```
C_capital = 150 per period

Represents: plant, equipment, workforce, infrastructure
```

### R&D/Innovation Cost
```
C_R&D_i = k · (R&D_i)^2

where:
  k = 0.05 (quadratic cost coefficient)
  (R&D_i)^2 models diminishing returns on R&D spending
  Higher R&D → exponentially higher cost
```

### Compliance Cost (Regulatory)
```
C_compliance_i = C_fixed + τ · Q_i

where:
  C_fixed = 50 (fixed regulatory burden)
  τ = 0.02 · C_base = 1.6 (per-unit compliance cost)
  
Models: testing, approval, audits, certification
  - Fixed cost: annual regulatory burden
  - Variable cost: scales with production volume
```

---

## Innovation Dynamics

### Innovation Stock (Accumulation)
```
I_i(t+1) = I_i(t) + R&D_i(t)

where:
  I_i = cumulative innovation stock of firm i
  R&D_i = annual innovation investment (agent action)
```

### Innovation Effectiveness Over Time
```
β(t) = β_0 · TechProgress(t) · DiminishingReturns(I_total)

where:
  β_0 = 1.5
  TechProgress(t) = 1 + 0.002·t
    (exogenous tech progress: digitalization, biotech, automation)
  DiminishingReturns = 1 / (1 + 0.01 · I_total)
    (innovation saturates: double diminishing returns)
```

**Interpretation:**
- Innovation becomes more powerful over decades (tech progress)
- But over-investment saturates returns (diminishing)
- Creates realistic R&D tradeoffs: invest now vs harvest later

---

## Regulatory Constraints (Porter's 5 Forces: Entry Barriers)

### Price Cap (Government Regulation)
```
Action space:
  Price ∈ [C_m(t) + ε, P_max]
  
where:
  C_m(t) + ε : Must cover marginal cost + small profit margin
  P_max = 250 (government price ceiling)
  
Enforcement: Hard constraint in action space
  (Agents cannot output price above ceiling)
```

### Compliance Cost Scaling
```
Models regulatory burden scaling with firm size and output.
High-volume firms pay more compliance cost.
```

---

## Exogenous Shocks & Dynamics

### Economic Cycle (Regime Switching)
```
Regime(t) ∈ {Boom, Recession}
Transition probabilities (Markov):
  Boom → Boom: 0.95
  Boom → Recession: 0.05
  Recession → Recession: 0.90
  Recession → Boom: 0.10

Demand multiplier:
  EconomicCycle(Boom) = 1.2
  EconomicCycle(Recession) = 0.8
  
Noise: EconomicCycle(t) *= Normal(1, 0.02)
```

### Supplier Shocks (Input Volatility)
```
SupplierShock(t) ~ LogNormal(μ=0, σ=0.05)

Models:
  - Raw material price spikes
  - Logistics disruptions
  - Supply chain shocks
  
Applied to marginal cost: C_m(t) = C_base · SupplierShock(t)
```

### Substitute Pressure (Threat of Substitutes)
```
SubstitutePressure(t+1) = clamp(
    SubstitutePressure(t) + Normal(0, 0.005),
    min=0.05, max=0.3
)

Models:
  - Generics, imports, alternative therapies
  - Slow-moving competitive threat
  - Demand leakage: D_effective *= (1 - SubstitutePressure)
```

---

## Agent Actions & Observations

### Action Space (Agent Control Variables)
```
action_i(t) = [price_i(t), R&D_i(t)]

where:
  price_i ∈ [C_m(t) + ε, P_max]    (hard constraint)
  R&D_i ∈ [0, ∞)                    (continuous, unbounded)
```

### Observation Space (Full State)
```
state = [
    prices of all 3 firms,
    innovation stocks of all 3 firms,
    market shares of all 3 firms,
    current marginal costs,
    total effective demand,
    current economic regime,
    current supplier shock,
    current substitute pressure,
    time step (t)
]
```

**Note:** Fully observable, non-stationary (shocks, tech progress)

---

## Episode Dynamics

### Episode Length
```
T = 200 steps
Interpretation: 200 quarters = 50 years
Long-term strategic horizon
```

### Discount Factor
```
γ = 0.99

Supports:
  - Intertemporal strategy (R&D payoff planning)
  - Long-run profit maximization
  - Tacit collusion dynamics
```

---

## Equilibrium Properties

This economic model is designed to exhibit:

✅ **Cost-covering equilibrium** (prices ≥ marginal cost)
✅ **Bertrand-like oligopoly** (price competition)
✅ **Positive profit in equilibrium** (sustainable industry)
✅ **Price wars** (under competitive pressure)
✅ **Innovation races** (R&D investment tradeoffs)
✅ **Regulatory impact** (price ceiling binding)
✅ **Market concentration** (possibly unequal shares)
✅ **Shock resilience** (adaptation to demand/cost shocks)
✅ **Dynamic strategy** (time-varying policies)

---

## Parameter Summary Table

| Parameter | Symbol | Value | Unit | Interpretation |
|-----------|--------|-------|------|-----------------|
| Base demand | D₀ | 1,000 | units | Market size |
| Marginal cost | C_base | 80 | $/unit | Production cost |
| Capital cost | C_cap | 150 | $ | Fixed cost/period |
| Compliance (fixed) | C_fix | 50 | $ | Regulatory burden |
| Compliance (variable) | τ | 1.6 | $/unit | Per-unit regulatory |
| R&D cost coeff | k | 0.05 | — | Quadratic cost |
| Price cap | P_max | 250 | $ | Government ceiling |
| Price elasticity | ε | 0.015 | — | Buyer power |
| Price sensitivity | α | 0.03 | — | Softmax coeff |
| Innovation power | β₀ | 1.5 | — | Tech advantage |
| Tech progress rate | — | 0.002 | /year | Exogenous tech |
| Diminishing returns | — | 0.01 | — | Innovation saturation |
| Boom multiplier | — | 1.2 | — | Economic cycle |
| Recession multiplier | — | 0.8 | — | Economic cycle |
| Supply shock std | — | 0.05 | — | Supplier volatility |
| Substitute pressure range | — | [0.05, 0.3] | — | Generic/import threat |
| Number of firms | n | 3 | — | Oligopoly |
| Episode length | T | 200 | steps (quarters) | 50-year horizon |
| Discount factor | γ | 0.99 | — | RL time preference |

---

## Validation Checklist

This economic model should produce:

- [ ] Positive equilibrium profits (not negative)
- [ ] Stable price bands (e.g., $120-180 range)
- [ ] Meaningful innovation investment (e.g., $5-15/period)
- [ ] Market shares roughly in [20%, 50%] (varies by strategy)
- [ ] No price collapse to $0 or $1
- [ ] Shock response (prices/innovation adjust to shocks)
- [ ] Long-run convergence (200 steps allows learning)

---

**Document Version:** 1.0
**Last Updated:** January 21, 2026
**Status:** Complete & Operationalized
