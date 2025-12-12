> How much resource does it require for a minimal effective demo? How much does the learning process rely on labeled examples and computes?
---


Great question 👍—because this whole “HAN with RL over the wiring” idea *sounds* like it could explode in compute, but a minimal effective demo can be surprisingly lightweight if you scope it right. Let me break it down in terms of **resource requirements** and **data dependence**:

---

## 1. Scale of the Demo

* **Atomic LLMs:**
  You don’t need GPT-4 level models. Small frozen models (e.g. GPT-3.5-turbo, LLaMA-8B, or even `phi-3-mini`) are fine because the point isn’t raw reasoning but *differential usefulness under routing*.
  ➝ In practice, 5–8 atomic LLMs, each doing a role like Retriever, Planner, Critic, etc.

* **Graph policies:**
  The learnable parts (router/scheduler/editor) can be very small neural nets (MLPs with ~10k–100k params). Training those is cheap—minutes to hours on CPU/GPU.

---

## 2. Compute Cost

* **Episode definition:** one full run of the HAN on a task (e.g., writing code until unit tests pass).

* **Per episode cost:** dominated by LLM calls. If each episode uses 50–200 messages across 5–8 models, and each message is a short (<300 tokens) exchange, you’re looking at ~10k–30k tokens/episode.

* **Training budget (minimal demo):**

  * **Tiny run:** 500–1,000 episodes → ~10–30M tokens (a few $ if using GPT-3.5 API; a weekend on a small open model).
  * **More robust:** 10k episodes → ~200–300M tokens (a few GPUs for a week, or ~$100s on API calls).

So: not negligible, but not at the “pretraining” scale—closer to reinforcement fine-tuning runs in RLHF papers.

---

## 3. Data / Labels

* **No big labeled dataset needed.**
  You don’t collect human annotations. The “reward” comes from **task environment signals**:

  * For coding: % of unit tests passed.
  * For math: correctness checks on answers.
  * For planning: objective score (path length, success/failure).
  * For QA: overlap with ground-truth answers.

* **So:** you only need a **task generator** (like random specs with unit tests). This is why program synthesis is such a good first demo—it’s fully automatable, no human labelers.

---

## 4. Where learning signal comes from

* **Fast timescale:** Router/scheduler learn from *relative usefulness of edges* within one episode (bandit-style).
* **Slow timescale:** Graph evolution learns from *aggregate reward* across episodes (selection).

Because of caching + automatic task rewards, you avoid needing massive labeled corpora. The system *bootstraps* by exploration.

---

## 5. Minimal Effective Demo Recipe

* **Hardware:** 1 GPU with ~24GB VRAM (or cloud API access to a mid-tier LLM).
* **Task:** code-gen with self-checking tests (like HumanEval-style, or your own toy spec-to-unit test generator).
* **Nodes:** 6 frozen small models (retriever, summarizer, planner, coder, tester, critic).
* **Policies:** 2 tiny MLPs (router, scheduler) trained with REINFORCE + baseline.
* **Episodes:** 1k–2k → enough to see emergent routing (e.g., “Planner always forwards to Critic before Coder”).
* **Wall-clock:** A few days if running locally; much faster if you parallelize tasks.

---

✅ **Bottom line:**
A minimal demo doesn’t need fine-tuning atomic LLMs, doesn’t need a big labeled dataset, and runs at the *RLHF-style finetune* scale (~10–100M tokens, not billions). It’s compute-heavy compared to a toy script, but absolutely feasible for a research prototype on a single good GPU or with modest API credits.

---

Would you like me to **design the cheapest possible variant** (e.g., 3 nodes + bandit router, <1M tokens) that still clearly shows *emergent specialization*—so you could try it hands-on without too much cost?
