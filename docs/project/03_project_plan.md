# Project Plan

## 1. Purpose

Organize the development of a Deep Learning system that predicts the difficulty of coding prompts for a target LLM.

The initial reference model will be **Llama 3 8B**, while the architecture will remain compatible with other local or API-based LLMs.

## 2. Development Phases

### Phase 1 — Dataset Research

- search for coding prompt datasets;
- identify benchmarks suitable for measuring LLM capability;
- document dataset sources and licenses;
- select the initial dataset.

### Phase 2 — Data Audit and EDA

- inspect dataset structure and quality;
- detect missing values, duplicates, and inconsistencies;
- analyze prompt length and task distribution;
- identify possible difficulty-related patterns.

### Phase 3 — Difficulty Labeling

Define the four target classes:

- **Easy**
- **Medium**
- **Hard**
- **Cannot Solve**

Labels should be derived from measurable LLM performance rather than subjective judgment.

Llama 3 8B will initially be used as one of the reference models for this process.

### Phase 4 — Data Preparation

- standardize the dataset schema;
- preprocess coding prompts;
- create training, validation, and test splits;
- prevent data leakage.

### Phase 5 — Baseline

Develop a simple baseline to establish a reference performance level.

Possible approaches include:

- TF-IDF;
- pretrained embeddings;
- simple classifier.

### Phase 6 — Deep Learning Model

Develop the main classification architecture:

Prompt → Pretrained Representation → Custom Neural Network → Difficulty Class

Experiments may include frozen pretrained representations and later fine-tuning if justified.

### Phase 7 — Evaluation

Evaluate the models using classification metrics such as:

- accuracy;
- precision;
- recall;
- F1-score;
- confusion matrix.

The final evaluation should also analyze errors between the four difficulty categories.

### Phase 8 — System Integration

Once the modeling approach is validated:

- integrate the trained model into the backend;
- support local and API-based LLMs;
- connect the frontend;
- containerize the system with Docker.

## 3. Collaboration Workflow

Each development task should use a separate Git branch.

Examples:

- `feature/data-audit`
- `feature/eda`
- `feature/labeling`
- `feature/baseline`
- `feature/neural-network`

Changes will be integrated into `master` through Pull Requests.

## 4. Current Open Decisions

The following elements are still under evaluation:

- final datasets;
- exact labeling thresholds;
- pretrained representation model;
- neural network architecture;
- additional LLMs for comparison;
- final evaluation protocol.