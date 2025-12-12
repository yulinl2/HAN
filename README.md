# 🧠 Hierarchical Agentic Network (HAN)
📅 *Last modified: `Wednesday, November 26, 2025`*

> **A minimal, self-organizing architecture built from frozen LLM atoms.**  
> Instead of fine-tuning models, HAN learns only *how* components connect, communicate, and coordinate.

---

## 🌍 Overview
The **Hierarchical Agentic Network (HAN)** treats small LLMs and tools as immutable **atoms**.  
It learns the *wiring*—the routing, scheduling, and structural patterns—between them.  
Through simple global rules on energy, redundancy, and reward, complex multi-level organization **emerges naturally**.

---

## 💡 Core Idea
> *Teach nothing. Wire everything. Let coordination evolve.*

Each atom has a fixed skill (retrieving, planning, coding, critiquing, testing).  
HAN learns which atoms should talk, when, and how.  
This produces a system that refines its own workflow—bottom-up—without new rules or weight updates.

---

## 🧬 Architecture at a Glance

| Layer | Role | Example behavior |
|-------|------|------------------|
| **Atoms** | Frozen LLMs / tools | Write, critique, retrieve, test |
| **Motifs (Organs)** | Small reusable patterns | Planner → Coder → Tester |
| **Graph (Tissue)** | Communication wiring | Message routing, feedback loops |
| **Policies (Physiology)** | Learnable controllers | Routing, scheduling, structural edits |
| **Organism** | Whole HAN instance | Solves tasks via internal coordination |
| **Evolution** | Population-level selection | Keeps best graphs, motifs, and styles |

Every layer shares the same message protocol and energy/reward physics—  
no new logic required as depth increases.

---

## 🧩 What Learns vs What’s Fixed

| Component | Type | Function |
|------------|------|----------|
| Atomic LLMs & tools | **Fixed** | Provide core skills |
| Message format / energy rules | **Fixed** | Define system physics |
| Router policy | **Learned (RL)** | Chooses edges / message schemas |
| Scheduler policy | **Learned (RL)** | Allocates turns, budgets, stops |
| Editor policy | **Learned (slow)** | Adds, removes, splits, merges motifs |
| Reward model (optional) | **Learned** | Captures emergent “taste” (readability, elegance) |

---

## 🚀 Minimal Demo Setup

**Task:** program synthesis from noisy natural-language specs + unit tests (self-verifying).  
**Atoms:** `SpecCompressor`, `Retriever`, `Planner`, `Coder`, `Critic`, `Tester`.  
**Learnable:** Router + Scheduler (tiny RL/bandit policies).  
**Fixed:** all LLM prompts and atomic behaviors.

**Loop**
1. Planner breaks down the problem.  
2. Router directs messages among atoms.  
3. Scheduler decides who acts next & when to stop.  
4. Tester scores results (pass rate, cost, stability).  
5. Policies update → structure gradually self-organizes.

Even with random routing, HAN can produce runnable code from the start;  
learning mainly improves **coordination and efficiency**.

---

## ⚖️ Scaling Principle

| Dimension | Mechanism | Result |
|------------|------------|--------|
| **Width** | Add more motifs under the same rules | Parallel specialization |
| **Depth** | Allow motifs to compose recursively | Emergent hierarchy |
| **Energy constraint** | Global token/time budget | Natural pruning & focus |

> HAN scales like a *fractal*: cells → organs → organisms → societies—  
> all governed by identical dynamics.

---

## 🎯 Emergent Behaviors
- Local convergence (each block self-refines).  
- Global organization (higher-level coordination).  
- Automatic task partitioning & specialization.  
- Progressive aesthetic improvement (readability, modularity, conciseness).

---

## 🧮 Resource Snapshot

| Stage | Estimate |
|--------|-----------|
| 5–8 frozen LLMs | single 24 GB GPU or mid-tier API |
| 1 – 2 × 10⁶ tokens | quick proof-of-concept (~hours) |
| 10⁷ – 10⁸ tokens | stable learning (~days) |
| Cost | modest local / cloud budget |

---

## 📦 Demo Deliverables
- **Working prototype:** HAN generates & revises code until tests pass.  
- **Telemetry:** evolving message graph + reward traces.  
- **Report / notebook:** evidence of emergent specialization & hierarchy.

---

## 🧠 In One Sentence
> **HAN = a scalable, self-organizing, reinforcement-driven “organism” built from frozen LLM atoms—learning how to think *together*, not how to think *individually*.**

---

### 📘 Citation / Reference
*(Add link to paper or preprint once available)*

---

### 🧩 Diagram Placeholder

```
[ Atoms ] → [ Motifs ] → [ Graph ] → [ Policies ] → [ Organism ] → [ Evolution ]
```

(Add `docs/diagram.png` or `assets/han_layers.svg` here)

---