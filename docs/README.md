# HAN: Hierarchical Agentic Network
📅 *Last modified: `Wednesday, November 26, 2025`*

---

## 🗂️ **Repository Layout**

```
han/
│
├── README.md
├── pyproject.toml          # package setup, deps
├── requirements.txt        # (optional) pip freeze
├── Makefile                # run / clean / dev helpers
│
├── han/                    # main Python package
│   ├── __init__.py
│   ├── atoms/              # frozen LLM/tool wrappers
│   │   ├── base.py
│   │   ├── planner.py
│   │   ├── coder.py
│   │   ├── critic.py
│   │   ├── retriever.py
│   │   └── tester.py
│   │
│   ├── policies/           # learnable components
│   │   ├── router.py
│   │   ├── scheduler.py
│   │   └── editor.py
│   │
│   ├── core/               # "physics": execution engine
│   │   ├── messages.py
│   │   ├── graph.py
│   │   ├── episode.py
│   │   ├── reward.py
│   │   ├── telemetry.py
│   │   └── config.py
│   │
│   ├── tools/              # static analyzers, embeddings, etc.
│   │   ├── embedder.py
│   │   ├── linter.py
│   │   └── utils.py
│   │
│   └── evolution/          # long-term selection + experiments
│       ├── population.py
│       ├── selection.py
│       └── mutations.py
│
├── configs/                # clean YAML configs
│   ├── atoms.yaml
│   ├── policies.yaml
│   ├── env.yaml
│   └── tasks.yaml
│
├── tasks/                  # dataset: specs + unit tests
│   ├── examples/
│   └── generators/
│
├── experiments/            # notebooks & scripts
│   ├── demo-minimal.ipynb
│   └── run_experiment.py
│
├── logs/                   # telemetry, traces, routing graphs
│   └── *.ndjson
│
├── artifacts/              # generated solutions, diffs, diagrams
│
└── docs/                   # diagrams, writeups
    ├── architecture.md
    └── han_layers.svg
```

---

## 📌 **What Each Folder Means (at a glance)**

### **`han/`**

The actual Python package.

### `atoms/`

Frozen LLM wrappers.
Each file = one capability, totally stateless except prompt + model call.

### `policies/`

The **only learnable** modules: router, scheduler, editor.

### `core/`

The “physics engine”:

* episode loop
* message passing
* graph structure
* reward shaping
* telemetry capture

Stable logic; should rarely change.

### `tools/`

Static analyzers (linter, code metrics), embeddings, helpers.
These feed the reward model (if you choose to add one).

### `evolution/`

Optional: run multiple HAN instances, keep best ones (like population-based training).

---

## 📦 **`configs/` — clean and declarative**

* `atoms.yaml`: model names, prompts, temperature, max tokens.
* `policies.yaml`: router & scheduler hyperparameters.
* `env.yaml`: budgets, reward weights, energy rules.
* `tasks.yaml`: which tasks to run, # episodes, curriculum settings.

This keeps the code uncluttered: you change experiments by editing configs.

---

## 🧪 **`tasks/`**

Your self-verifying program synthesis tasks (spec + unit tests).

* `examples/`: curated hand-written tasks.
* `generators/`: scripts to generate noisy descriptions & tests.

---

## 📊 **`logs/`**

Everything goes into NDJSON:

* per-step telemetry
* routing decisions
* scheduler decisions
* reward breakdown
* message counts
* structural mutations

Perfect for later visualization.

---

## 📁 **`artifacts/`**

* saved candidate solutions
* diffs between revisions
* final integration outputs
* archived best-in-class motifs
* snapshots of routing graphs

---

## 📚 **`docs/`**

Human-friendly resources:

* architecture diagram
* research notes
* future ideas
* exported notebooks

---

## 🧭 **Step-by-step Setup Instructions**

### 1️⃣ Clone repo

```
git clone https://github.com/<you>/han.git
cd han
```

### 2️⃣ Set up environment

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3️⃣ Add API keys (if using OpenAI/Anthropic)

```
export OPENAI_API_KEY=...
```

### 4️⃣ Run a minimal demo

```
python experiments/run_experiment.py --config configs/env.yaml
```

### 5️⃣ View logs in real time

```
tail -f logs/latest.ndjson
```

### 6️⃣ Add diagrams for collaborators

* drop them into `/docs/`
* link them in `README.md`

---

<!-- ## 🧱 **Initial Code Stubs (auto-generation option)**

If you want, I can generate:

* `router.py` skeleton
* `scheduler.py` skeleton
* `episode.py` skeleton
* message schema
* config loader
* demo Jupyter notebook (`demo-minimal.ipynb`)
* a starter diagram in SVG

Just say: **“Generate code stubs.”**

---

## 🎉 That’s the whole repo setup

It’s clean, reproducible, scalable, and entirely aligned with the HAN architecture you’ve defined.

If you want, I can also:

* propose **branch naming conventions**,
* design **GitHub Actions CI**,
* generate a **starter roadmap** for the project,
* or produce a **full initial commit** with all folders and files pre-filled but empty.

Would you like that? -->
