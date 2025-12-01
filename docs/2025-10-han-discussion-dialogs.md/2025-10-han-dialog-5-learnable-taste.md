>Well, I think the system should learn its own standard of perfection. Perfection comes in lots of different aspects - not just passing the unit tests, but also the readability of code, modularity of code, conciseness / minimal length, etc. Just like human - the system should grow to live by its own work aesthetics...

---

Love that. Let’s give HAN its own evolving “taste” without touching the atom LLMs.

# Idea in one line

Train a small **learned reward model** $R_\theta$ that scores solutions on multiple aesthetic axes (readability, modularity, brevity, etc.), and let the router/scheduler optimize against **that**—not just tests. $R_\theta$ itself keeps updating from **self-play preferences**, static analyzers, and committee critics. No atomic LLM fine-tuning needed.

---

# Architecture additions (stacked by abstraction)

## A) Organism level — what changes

* Each episode still aims to solve the task, but **acceptance** is now: high $R_\theta$ score **and** tests pass (tests act as a safety floor).
* The revision loop optimizes a **composite reward**:
  $$
  J = \alpha \cdot \text{pass}@k + \beta \cdot R_\theta(\text{code}) - \lambda_{\text{cost}}
  $$
  with $\alpha \gg 0$ as a gate (no aesthetics without correctness) and $\beta>0$.

## B) Physiology — new organs (all lightweight)

1. **Aesthetics Reward Model $R_\theta$** (tiny MLP or logistic head; 10–100k params).

   * Inputs: a feature vector $f(\text{code})$ (below) + critic committee votes.
   * Output: scalar (or vector for multi-objective; see Pareto below).
2. **Preference Generator** (self-play):

   * Runs **duels** between drafts (A vs B) and produces pairwise preferences $A \succ B$ using rules below.
3. **Archive & Hall of Fame**:

   * Stores past “good” solutions; new drafts duel against these for **stationary standards**.
4. **Pareto Manager** (optional but nice):

   * Maintains a small **Pareto front** of solutions by $(\text{tests}, \text{readability}, \text{modularity}, \text{brevity})$.
   * Lets scheduler choose which frontier point to aim for (style diversity).

## C) Metabolism — how $R_\theta$ learns its taste

### Feature extractor $f(\text{code})$ (all automated, frozen tools)

* **Static analyzers:** cyclomatic complexity, nesting depth, fan-out, cohesion/coupling, unused vars, duplication.
* **Lints & style:** ruff/flake8 count, naming heuristics, docstring presence.
* **Structure:** function count, average function length, module boundaries, import hygiene.
* **Brevity/MDL-ish:** token count, gzip size, AST node count (a proxy for description length).
* **Robustness:** test margin (e.g., property-based fuzz pass rate if cheap), exception handling presence.
* **Readability proxy:** score from a **frozen** rubric-LLM judge (short, stable prompt) converted to numeric.
* **Stability:** variance of outputs under small seed noise (lower is better).

> All of these are *metrics*, not labels. We’ll turn them into **preferences**.

### Preference formation (no humans)

Given two drafts (A,B) that both pass tests (or when neither passes, compare partial progress):

1. **Tournament rule:** compute a weighted score $S(A)=w^\top f(A)$ with a **slowly learned** $w$; if margin > δ, prefer higher.
2. **Committee rule (frozen)**: Critics (distinct prompts) vote on readability/modularity; majority adds +1 preference strength.
3. **MDL tiebreak:** prefer lower description length (gzip/AST size) when correctness equal and committee split.
4. **Stability tiebreak:** prefer lower variance across seeds / higher AST equivalence across reruns.
5. **Diversity cap:** if A is near-duplicate of an archive exemplar, slightly down-weight to avoid mode collapse.

Record pair $(A,B,y)$ with $y\in{0,1}$ indicating $A\succ B$.

### Train $R_\theta$ by preference learning

* **Bradley–Terry / logistic** on pairs:
  $$
  \Pr[A \succ B] = \sigma\left(R_\theta(f(A)) - R_\theta(f(B))\right)
  $$
* Optimize $-\sum \log \Pr[y]$ with small L2 and **temporal ensembling** (EMA of $\theta$) to avoid drift.
* Refresh on a **slow timescale** (e.g., every N episodes) so the target doesn’t move too fast.

> If you want **multi-objective taste**: predict a vector $g_\theta \in \mathbb{R}^m$ and learn **contextual weights** $w_c$ per task family; or keep the **Pareto set** and let the scheduler pick a point conditioned on budget.

---

# How this shapes behavior (without touching atoms)

## Router & Scheduler training target

Replace the old scalar reward with:
$$
R_{\text{episode}} = \alpha \cdot \mathbb{1}[\text{tests pass}] + \beta \cdot R_\theta(\text{final}) - \lambda_\text{tokens} - \lambda_\text{latency} - \rho \cdot \text{redundancy}
$$

* **During revision**, give **delta bonuses** when $R_\theta$ increases or complexity drops **while** tests remain green.
* **Early stop** learns to trigger when additional loops don’t raise $R_\theta$ beyond $\epsilon$.

## Emergent “house style”

* Over time, the archive + preferences stabilize a style (naming, factoring, docstrings, small functions).
* The **motif library** will reflect this: e.g., Planner tends to route through “Refactor-Before-Patch” motifs when $R_\theta$ rewards modularity; or favors “Small Patch” when brevity is emphasized.

---

# Guarding against reward hacking

* **Holdout critics:** keep one frozen judge and a hidden static metric set used **only** on validation; penalize large train/val gaps.
* **Adversarial checks:** detect trivial ways to please rubrics (e.g., inserting docstrings without substance) with **content-aware heuristics** (e.g., docstring/code semantic alignment via embeddings).
* **Rate limit rubric influence:** cap its weight so static analyzers + stability always matter.
* **Slow updates:** update $R_\theta$ on a slower schedule and with replayed, **re-audited** pairs.

---

# Minimal effective way to build this (small & doable)

1. **Metrics first**: implement $f(\text{code})$ with:

   * `pytest` pass rate; `ruff`/`flake8` count; cyclomatic complexity; LOC; gzip size; AST nodes; function count; avg function length.
2. **Frozen rubric judge**: one tiny model with a 10-line rubric prompt that outputs 1–10 for readability & modularity.
3. **Pairwise self-play**:

   * For each episode, keep the **last K drafts** that pass tests. Sample pairs (A,B) across steps + vs archive exemplars.
4. **Train $R_\theta$**:

   * Start with **linear Bradley–Terry on features** (no MLP yet). Every 200–500 episodes, re-fit in seconds.
5. **Plug into RL**:

   * Replace the “improvement” signal in your scheduler with $\Delta R_\theta$. Give **patch bonus** only if $\Delta R_\theta>0$.
6. **Pareto-lite** (optional, cheap):

   * Track a tiny frontier on $[\text{readability}, \text{brevity}, \text{modularity}]$ for passed solutions; let scheduler pick a target point conditioned on **budget** (short budget → brevity; ample budget → modularity).

---

# Pseudocode (pairwise training loop)

```python
# After each episode with final code 'C_final' and passing drafts 'D_pass'
archive.add(C_final)
pairs = sample_duels(D_pass + archive.sample(m=3))

for (A,B) in pairs:
    y = preference(A,B)  # rules above
    X.append(f(A) - f(B))
    Y.append(y)

# Bradley–Terry (logistic) update every N episodes
theta = fit_logistic(X, Y, l2=1e-3)  # seconds
R_theta(code) = sigmoid(theta · f(\text{code}))  # or raw score
```

---

# What you get

* **Self-organized aesthetics:** The system grows a house style that *it* prefers—grounded in analyzable signals, not hand-written rules.
* **Task-aligned taste:** Because tests gate reward and archive duels are anchored, the style stays useful, not decorative.
* **No atom tuning:** All learning is in $R_\theta$ and the router/scheduler; atom LLMs remain frozen.

If you want, I can draft the exact feature list, the 10-line rubric prompt, and a tiny Bradley–Terry trainer you can drop into your current scaffolding.
