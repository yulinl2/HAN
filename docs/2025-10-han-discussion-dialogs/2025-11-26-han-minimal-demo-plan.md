# Minimal Effective HAN Demo

Here’s a clean, end-to-end blueprint for a **minimal effective HAN demo** where only the **wiring/routing/scheduling** learns and all atomic LLMs stay frozen. I’ll lay it out from high-level → low-level so you can see exactly what to build.

## Scope of the minimal demo

* **Task domain:** program synthesis from noisy natural-language specs with unit tests (self-scoring).
* **Atoms (frozen):** 5 roles → {SpecCompressor, Retriever, Planner, Coder, Critic}.
  (Tester is a Python runner, not an LLM.)
* **Learned pieces:** Router policy (who talks to whom + payload size) and Scheduler policy (who goes next + early stop).
  Optional (later): Structure editor (clone/prune/fuse motifs) updated slowly via selection.
* **Signals:** Reward = pass@k – λ·tokens – μ·latency – ρ·redundancy + κ·stability.

---

## 1) System at a glance (levels of abstraction)

### Level A — Organism (episode lifecycle)

**Goal:** Solve one task instance under a token/time budget.
**Loop:**

1. Ingest spec → compress → plan.
2. Router picks recipients and payload schema; Scheduler allocates steps.
3. Nodes produce drafts/edits; Tester runs unit tests when Coder proposes code.
4. Early-stop if tests pass or budget used; compute reward.

**You build:** episode driver, budgets, stop criteria, reward calculator.

---

### Level B — Anatomy (graph + node types)

**Typed DAG** with bounded fan-out and depth.

* **Nodes (frozen LLMs)**

  * `SpecCompressor` (S): distills the problem statement into crisp I/O description.
  * `Retriever` (R): fetches API hints/snippets from a small local corpus (stdlib, tricks).
  * `Planner` (P): decomposes into steps + edge-cases; emits “dev brief”.
  * `Coder` (C): writes/edits Python function per brief; keeps diffs small.
  * `Critic` (K): reviews code vs brief & failing tests; suggests targeted patch.

* **Tools (non-LLM)**

  * `Tester`: runs unit tests; returns pass count + failing traces.
  * `Embedder`: sentence-embedding for novelty/duplication scoring (small, frozen).
  * `Cache`: memo for (prompt → completion) to enable counterfactuals cheaply.

**You build:** node wrappers with uniform API + tool adapters.

---

### Level C — Physiology (policies + state)

* **Router policy** π_r(a | state): choose edges to activate and payload schema.
* **Scheduler policy** π_s(a | state): pick next node(s), micro-budget, early-stop.
* (Optional later) **Editor** π_e: propose structure mutations every N episodes.

**State features** (no LLM training needed):

* Graph features: active edges, degree/fan-out, motif IDs.
* Telemetry: msg length, latency, token cost, tool hits.
* Content metrics: entropy of summaries, disagreement score, novelty vs cache, embedding similarity.
* Task progress: tests passed, error types, #patches applied.

**Actions:**

* Router: `{activate_edges: [(u→v, schema_id, max_tokens), …]}`.
* Scheduler: `{next_node, step_budget, maybe_early_stop}`.
* Editor: `{add_edge, remove_edge, clone_branch, fuse(u,v)}` (rarely invoked).

---

### Level D — Metabolism (reward & credit)

**Reward per episode**
`R = α·task_score – β·tokens – γ·latency – δ·redundancy + ε·stability`

* `task_score`: normalized pass@k (e.g., 1.0 if all tests pass).
* `tokens`: total model tokens (prompt+completion).
* `latency`: wall time (or proxy).
* `redundancy`: mean cosine similarity among parallel branches’ outputs.
* `stability`: agreement of final solution across two independent runs with tiny noise.

**Credit assignment (cheap)**

* Use **REINFORCE + learned baseline** on π_r, π_s with per-step advantages.
* **Counterfactual routing buffer:** for the most costly decisions, replay with top-2 alternative edges using cache; compute ΔR to train π_r.
* **Shapley-lite:** leave-one-edge-out on cached drafts near the end to attribute marginal utility.

---

## 2) Interfaces & schemas (what you literally code)

### 2.1 Node API (uniform wrapper)

```python
class Node:
    def __init__(self, role_name, system_prompt, model):
        self.role = role_name
        self.sys = system_prompt
        self.model = model  # frozen LLM or tool

    def run(self, inbox, controls):
        """
        inbox: List[Message]  # see schema below
        controls: Dict        # {max_tokens, temperature, schema_hint}
        returns: NodeOutput   # text, annotations, cost telemetry
        """
        ...
```

### 2.2 Message schema (routing payload)

```json
{
  "header": {
    "from": "Planner",
    "to": "Coder",
    "intent": "propose_patch",             // enum
    "certainty": 0.68,                     // 0..1 (self-reported)
    "novelty_est": 0.42,                   // vs cache/embeds
    "cost_est": 320                        // est tokens if executed
  },
  "content": {
    "summary": "...",
    "evidence": ["doc:python_sort_examples#3"],
    "diff_hint": "edit lines 12-18 only"
  },
  "trace": {
    "episode_id": "...",
    "step": 9,
    "parents": ["msg_7","msg_8"]
  }
}
```

### 2.3 Telemetry record (per step)

Columns you’ll log:

```
episode_id, step, active_edges, next_node,
prompt_tokens, completion_tokens, wall_ms,
tool_calls, pass_count, fail_count, fail_types,
entropy, novelty, sim_to_peers, cache_hit,
early_stop, reward_partial
```

### 2.4 Policy input tensor (state encoder)

* Numeric: budget_left, step_idx, pass_rate, recent_fail_type_onehot (len~8), avg_entropy, avg_novelty, mean_sim, deg(u), deg(v), motif_id onehot, last_node onehot.
* Categorical (embed): role IDs, edge IDs, schema IDs.
* Size target: ≤ 256 dims.

---

## 3) Training loop & curriculum

### 3.1 Episode driver (pseudo)

```python
for task in sampler(curriculum):
    state = observe(graph, telemetry, task)
    inboxes = bootstrap_with_spec(task)

    for step in range(MAX_STEPS):
        A_route = router.sample(state)
        msgs = deliver(A_route, inboxes)

        next_node, budget, stop_flag = scheduler.sample(state)
        if stop_flag: break

        out = run_node(next_node, msgs[next_node], max_tokens=budget)
        update_inboxes_and_cache(out)
        update_telemetry(out)

        if tests_passed(out) or budget_exhausted():
            break

    R = compute_reward(telemetry)
    update_policies(router, scheduler, R, logs=telemetry)
    maybe_mutate_graph_every_N(R)
```

### 3.2 Curriculum

* Start with **single-function** problems (no tricky I/O).
* Gradually introduce **noisier specs**, edge-cases, time limits.
* Increase energy budget with competence (to mimic “development”).

---

## 4) Evaluation harness

* **Metrics:** pass@k, tokens/episode, time/episode, steps to success, variance across seeds (stability), redundancy score.
* **Baselines:**

  1. Single sequential agent (no routing/scheduling).
  2. Fixed hand-wired graph (no learning).
  3. Random router/scheduler (sanity).
* **Ablations:** remove Critic, remove Retriever, freeze router (only scheduler learns).

---

## 5) Storage & services

* **Cache:** LM prompt→completion with fingerprint (role, sys, prompt hash, schema, temperature).
* **Replay buffer:** (state, action, reward, alt_actions, deltas) for counterfactual training.
* **Artifacts:** all code drafts, diffs, failing traces (enable post-hoc analysis).
* **Small doc corpus:** 100–300 snippets (stdlib patterns, idioms) for Retriever.

---

## 6) Concrete “first build” (runnable in days)

### 6.1 Node prompts (“hormones”) sketched

* `SpecCompressor`: “Summarize function signature, input constraints, examples; remove fluff; list 3 edge cases.”
* `Planner`: “Turn summary into a 3–5 step dev brief; enumerate edge-case handling; state minimal test plan.”
* `Coder`: “Implement only what brief states. If patching, output unified diff only.”
* `Critic`: “Read failing tests/trace; propose the smallest diff to fix; keep style consistent.”
* `Retriever`: “Given brief, fetch up to 2 relevant snippets (names + 1–2 lines).”

(Keep system prompts short and stable; that’s key for frozen specialization.)

### 6.2 Policies (cheap to start)

* **Router:** contextual bandit (LinUCB) over a small discrete action set:

  * Candidate edges from {S→P, P→C, P→K, K→C, S→R, R→P, C→K} × {schema: brief|patch|summary} × {max_tokens: 64|128|256}
* **Scheduler:** small MLP (2 layers, 64 units) with softmax over {next_node} and a Bernoulli for early-stop.
* Upgrade both to PPO once telemetry stabilizes.

### 6.3 Budgets

* Max 10–16 steps/episode.
* Max tokens/step: 128–256 for LLM nodes, 64 for Critic patches.
* Run dual-seed stability only on validation to save cost.

---

## 7) Directory layout (suggested)

```
han-minimal/
  cfg/
    env.yaml             # budgets, rewards, λ, γ, δ, ε
    policies.yaml        # router action set, scheduler net sizes
    prompts.yaml         # system prompts per role
  data/
    corpus/              # retriever snippets
    tasks/               # task specs & unit tests
  src/
    core/                # episode driver, graph, telemetry
    nodes/               # S,R,P,C,K wrappers
    tools/               # tester, embedder, cache
    policies/            # router.py, scheduler.py, (editor.py)
    reward/              # calculators, counterfactuals
    eval/                # baselines, reports
  runs/
    logs/, checkpoints/, artifacts/
```

---

## 8) Config examples (trimmed)

**cfg/env.yaml**

```yaml
budget:
  max_steps: 14
  max_tokens_per_step: 192
  wall_time_ms: 20000
reward:
  alpha_task: 1.0
  beta_tokens: 0.0005
  gamma_latency: 0.0001
  delta_redundancy: 0.1
  epsilon_stability: 0.1
routing:
  max_fanout: 2
  schemas: [summary, brief, patch]
  candidates:
    - [SpecCompressor, Planner]
    - [Planner, Coder]
    - [Planner, Critic]
    - [Critic, Coder]
    - [SpecCompressor, Retriever]
    - [Retriever, Planner]
```

**cfg/policies.yaml**

```yaml
router:
  type: linucb
  explore_alpha: 0.2
scheduler:
  type: mlp
  hidden: [64, 64]
  lr: 1e-3
  entropy_coef: 0.01
```

---

## 9) Guardrails & failure modes

* **Ping-pong detector:** block immediate back-and-forth repeats (A→B→A→B).
* **Similarity cap:** if peer-sim > 0.9, penalize additional parallel branches.
* **Patch size cap:** critic patches ≤ N lines; else force Planner to re-brief.
* **Test sandboxing:** resource/time limits; forbid file/network access.

---

## 10) Milestones (tight)

1. Fixed graph + **bandit router** beats single agent on pass@1 at equal token budget.
2. **Scheduler** learns early-stop and fewer steps → lower cost without hurting pass@k.
3. Add **redundancy penalty** → emergent division of labor (Planner uses Retriever only when helpful; Critic patches become smaller).
4. (Optional) Introduce **editor** every 100 episodes to clone/fuse; keep if validation reward ↑.

---

### TL;DR build list

* [ ] Episode driver + reward calc + budgets
* [ ] Node wrappers for S/R/P/C/K + Tester tool
* [ ] Router (bandit) & Scheduler (tiny MLP) with state encoder
* [ ] Telemetry + cache + replay for counterfactuals
* [ ] Task generator + unit-test harness
* [ ] Baselines & eval scripts

---