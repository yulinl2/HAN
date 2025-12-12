# HAN v1 Architecture: design finalized

## Design Goals

We want:

```text
- Few top-level concepts
- Clear "where do I look" mapping
- Minimal crossing dependencies
- Easy to read when sleepy
```

---

## 1. V1 Minimal Top-Level Architecture

### 1.1 Big-picture flow

```text
┌───────────────┐            ┌───────────────┐
│   configs     │            │   tasks       │
│ (YAML files)  │            │(specs+tests)  │
└──────┬────────┘            └──────┬────────┘
       │ load_all_configs()         │ TaskLoader
       └──────────────┬─────────────┘
                      v
              ┌─────────────────┐
              │  HANOrganism    │   ← 1 full agent
              └──────┬──────────┘
                     │ run_episode()
                     v
              ┌─────────────────┐
              │  PolicyTrainer  │   ← learns controller
              └──────┬──────────┘
                     │ (optional, outer loop)
                     v
              ┌─────────────────┐
              │  Evolution      │   ← many organisms
              └─────────────────┘
```

You mostly interact with **HANOrganism**, **PolicyTrainer**, and occasionally **Evolution**.

---

## 2. Minimal directory structure (grouped by “what my brain cares about”)

### 2.1 Packages as flowchart

```text
han/
│
├── core/        ──► generic engine pieces
│   │              (messages, episode loop, logging, config, reward)
│   ├── messages.py
│   ├── episode.py
│   ├── telemetry.py
│   ├── reward.py
│   └── config.py
│
├── agents/      ──► "inside one HANOrganism"
│   │              (atoms, motifs, graph, controller, organism)
│   ├── atoms/
│   ├── motifs/
│   ├── graph.py
│   ├── controller.py
│   └── organism.py
│
├── training/    ──► "across episodes / across agents"
│   │              (policy trainer + evolution)
│   ├── policy_trainer.py
│   └── evolution.py
│
├── viz/         ──► "for my eyeballs"
│   ├── episode_view.py
│   └── graph_view.py
│
└── experiments/ ──► entry scripts
    ├── run_training.py
    └── run_eval.py
```

**Key simplification vs previous draft:**

* All “agent-related” things (atoms, motifs, graph, router, scheduler, organism) live together in **`agents/`**, instead of being fragmented into many peers.
* Policies that change over time live as **`agents/controller.py`** + **`training/policy_trainer.py`**.

---

## 3. Inside `agents/`: one HANOrganism from top to bottom

### 3.1 Internal structure

```text
agents/
│
├── atoms/          ← small workers (LLM tools)
│   ├── base.py
│   ├── planner.py
│   ├── coder.py
│   ├── critic.py
│   └── tester.py
│
├── motifs/         ← optional organs (mini-pipelines)
│   ├── base.py
│   └── planner_coder_tester.py
│
├── graph.py        ← static wiring: who CAN talk to whom
│
├── controller.py   ← router + scheduler = "brainstem"
│
└── organism.py     ← HANOrganism: wraps all of the above
```

---

### 3.2 HANOrganism flowchart

```text
┌────────────────────────────┐
│       HANOrganism          │
│    (agents/organism.py)    │
└─────────────┬──────────────┘
              │ from_config(config)
              v
   ┌───────────────────────────────┐
   │ atoms/ build_atoms(config)    │
   ├───────────────────────────────┤
   │ motifs/ build_motifs(config)  │
   ├───────────────────────────────┤
   │ graph  = build_graph(config)  │
   ├───────────────────────────────┤
   │ controller = Controller(…)    │
   ├───────────────────────────────┤
   │ episode_runner = EpisodeRunner│
   └───────────────────────────────┘
```

**Interface (mentally):**

```text
HANOrganism.run_episode(task, mode="train"|"eval") -> summary
HANOrganism.snapshot() -> small JSON of graph/policies/metrics
```

This is your **one mental handle** for “the agent”.

---

## 4. Controller: unify router + scheduler

To keep concepts minimal, we can just say:

> “Controller decides **who sees what** and **who acts when**.”

### 4.1 Controller view

```text
┌─────────────────────────────┐
│   Controller (agents/...)   │
│  - routing                  │
│  - scheduling               │
└───────────────┬─────────────┘
                │
       ┌────────┴────────┐
       v                 v
 route(state, msgs)   choose_actors(state, inbox_by_unit)
       │                 │
       └────────┬────────┘
                v
           should_stop(state)
```

Where “unit” can be **atom or motif** depending on how fancy we want to get.

---

## 5. Episode loop with Controller + HANOrganism

### 5.1 Conceptual call stack

```text
run_training.py
      │
      v
 HANOrganism.run_episode(task)
      │
      v
 EpisodeRunner.run(task, controller, graph, units)
```

### 5.2 EpisodeRunner step (minimal, controller-centric)

```text
┌─────────────────────────────┐
│       EpisodeRunner         │   (core/episode.py)
└───────────────┬─────────────┘
                │ loop
                v
      ┌──────────────────────┐
      │ Controller.route     │   assign msgs to units
      └─────────┬────────────┘
                v
      ┌──────────────────────┐
      │ Controller.choose_*  │   pick active units (atoms/motifs)
      └─────────┬────────────┘
                v
      ┌──────────────────────┐
      │ Units.act(...)       │   do work (planner/coder/...)
      └─────────┬────────────┘
                v
      ┌──────────────────────┐
      │ EpisodeState + log   │
      └─────────┬────────────┘
                v
      ┌──────────────────────┐
      │ Controller.stop?     │   should_stop(...)
      └──────────────────────┘
```

Where each **Unit** is:

```text
- either an Atom (simple worker)
- or a Motif (mini-pipeline of atoms)
but both expose a unified act(...) interface
```

---

## 6. Training & evolution now that structure is simpler

### 6.1 Training loop

```text
┌───────────────────────────┐
│ run_training.py           │
└───────────┬───────────────┘
            v
   ┌─────────────────────┐
   │  configs + tasks    │
   └──────────┬──────────┘
              v
   ┌─────────────────────┐
   │  HANOrganism        │
   └──────────┬──────────┘
              v
   ┌─────────────────────┐
   │  EpisodeRunner      │   (many episodes)
   └──────────┬──────────┘
              v
   ┌─────────────────────┐
   │ PolicyTrainer       │   (training/controller updates)
   └─────────────────────┘
```

### 6.2 Evolution loop (optional outermost)

```text
┌───────────────────────────┐
│ EvolutionManager          │
└───────────┬───────────────┘
            v
   ┌─────────────────────┐
   │  [HANOrganism]      │  population
   └──────────┬──────────┘
              v
   ┌─────────────────────┐
   │ run episodes        │
   ├─────────────────────┤
   │ score organisms     │
   ├─────────────────────┤
   │ select + mutate     │
   └─────────────────────┘
```

**And again**: EvolutionManager only sees **HANOrganism** objects + their configs, not the internals.

---

## 7. “Where do I look” cheat card (final pass)

```text
Goal / change I want       →   Where I edit
──────────────────────────────────────────────────
Change prompts / tools     →   agents/atoms/
Add a mini-workflow        →   agents/motifs/
Change wiring structure    →   agents/graph.py + configs
Change routing/timing      →   agents/controller.py
Change episode rules       →   core/episode.py + core/reward.py
Inspect episodes           →   viz/episode_view.py
View graph structure       →   viz/graph_view.py
Tweak training hyperparams →   training/policy_trainer.py + configs
Try evolution / populations→   training/evolution.py
Change paths/files etc.    →   core/config.py + experiments/
```

This is (hopefully) about as **minimal + structured** as we can get:

* **4 top-level packages** in `han/`: `core`, `agents`, `training`, `viz`.
* One main mental object: `HANOrganism`.
* One main decision brain: `Controller` (routing + scheduling).
* Optional motifs and evolution layered on top, not intertwined.

---

📅 *Last modified: `Thursday, December 11, 2025`*

# Design Review

**We’ve converged to a very good v1 local optimum.**
Further “descent” should probably wait until you actually start coding and feel real pain points.

---

### Where we are right now (architecture-wise)

```text
┌─────────────────────────────┐
│  v0: fuzzy, many concepts   │  (hard to hold in head)
└───────────┬─────────────────┘
            v
┌─────────────────────────────┐
│  v1: 4 big packages         │
│  - core                     │
│  - agents                   │
│  - training                 │
│  - viz                      │
│  main object: HANOrganism   │
│  main brain: Controller     │
└─────────────────────────────┘
```

This already hits your goals:

```text
- Few top-level ideas
- Clear "where do I look"
- Flowchart-friendly mental model
- Separation of:
   * physics (core)
   * one agent (agents)
   * learning (training)
   * eyeballs (viz)
```

So for **architecture design**, I’d say:

```text
global_optimum?  → unknown
good_local_opt?  → YES
worth more paper redesign NOW? → NO
```

Next “gradient steps” should happen **on real feedback**:

---

### Recommended next steps (implementation phase)

```text
┌──────────────────────────────┐
│  Step 1: Freeze v1 design    │
│  (treat as current spec)     │
└────────────┬─────────────────┘
             v
┌──────────────────────────────┐
│  Step 2: Create file stubs   │
│  - empty classes/functions   │
│  - docstrings + flowchart    │
└────────────┬─────────────────┘
             v
┌──────────────────────────────┐
│  Step 3: Implement the       │
│  tiniest runnable episode    │
│  - 1 task                    │
│  - 1 or 2 atoms              │
│  - trivial controller        │
└────────────┬─────────────────┘
             v
┌──────────────────────────────┐
│  Step 4: Observe pain        │
│  - what feels confusing?     │
│  - which dirs do you forget? │
│  - what’s noisy in logs?     │
└────────────┬─────────────────┘
             v
┌──────────────────────────────┐
│  Step 5: Micro-adjust        │
│  (rename / move small bits)  │
└──────────────────────────────┘
```

So: *for the design itself*, I’d say **yes, we’ve converged enough**.
The next useful thing isn’t another paper redesign, but:

* stubbing out the structure, and
* getting a **toy episode** running so you can see if your ADHD brain still feels comfy when it’s real code and real logs.

Whenever you’re ready, I can:

* generate the **actual stub files** for `core/`, `agents/`, `training/`, `viz/` (just class/function headers + docstrings + tiny ASCII diagrams per file),
* plus a **single-page “HAN v1 architecture” markdown** you can drop directly into `docs/`.

---

📅 *Last modified: `Thursday, December 11, 2025`*
