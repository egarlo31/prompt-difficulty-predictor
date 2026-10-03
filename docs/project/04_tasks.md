# Project Tasks

## 1. Purpose

Track the main implementation and experimentation tasks required to develop the Prompt Difficulty Predictor.

Detailed progress and code changes will be managed through Git branches and Pull Requests.

- **Pending**
- **In Progress**
- **Blocked**
- **Done**

---

## 2. Current Tasks

| ID | Task | Workstream | Dependency | Status | Owner |
|---|---|---|---|---|---|
| T-01 | Research GSM8K-compatible reasoning datasets | Data | None | Pending | Unassigned |
| T-02 | Document dataset sources and licenses | Data | T-01 | Pending | Unassigned |
| T-03 | Select initial dataset | Data | T-01, T-02 | Pending | Unassigned |
| T-04 | Define difficulty labeling method | Labeling | T-26 | Pending | Unassigned |
| T-05 | Prepare Llama 3.1 8B Instruct evaluation setup | Labeling / LLM | None | Pending | Unassigned |
| T-06 | Define backend API contract | Backend | None | Pending | Unassigned |
| T-07 | Create backend project skeleton | Backend | T-06 | Pending | Unassigned |
| T-08 | Implement temporary prediction endpoint | Backend | T-07 | Pending | Unassigned |
| T-09 | Select frontend technology | Frontend | None | Pending | Unassigned |
| T-10 | Create frontend project skeleton | Frontend | T-09 | Pending | Unassigned |
| T-11 | Implement prompt input interface | Frontend | T-10 | Pending | Unassigned |
| T-12 | Connect frontend and temporary backend | Integration | T-08, T-11 | Pending | Unassigned |
| T-13 | Generate labeled dataset | Labeling | T-04, T-05 | Pending | Unassigned |
| T-14 | Prepare training data | Modeling | T-13 | Pending | Unassigned |
| T-15 | Implement baseline model | Modeling | T-14 | Pending | Unassigned |
| T-16 | Define neural network architecture | Deep Learning | T-14 | Pending | Unassigned |
| T-17 | Implement neural network | Deep Learning | T-16 | Pending | Unassigned |
| T-18 | Implement training pipeline | Deep Learning | T-17 | Pending | Unassigned |
| T-19 | Train initial neural network | Deep Learning | T-18 | Pending | Unassigned |
| T-20 | Evaluate neural network | Deep Learning | T-15, T-19 | Pending | Unassigned |
| T-21 | Run model experiments | Deep Learning | T-20 | Pending | Unassigned |
| T-22 | Select final predictor | Modeling | T-15, T-20, T-21 | Pending | Unassigned |
| T-23 | Export trained model | Modeling / Integration | T-22 | Pending | Unassigned |
| T-24 | Integrate final predictor into backend | Backend / Integration | T-08, T-23 | Pending | Unassigned |
| T-25 | Perform data audit | Data | T-03 | Pending | Unassigned |
| T-26 | Perform exploratory data analysis | Data | T-25 | Pending | Unassigned |

---

## 3. Experimental Tasks

### T-01 — Research Candidate Datasets

Objective:

Identify datasets containing coding prompts or programming tasks suitable for the project.

Expected result:

- candidate datasets identified;
- basic characteristics documented;
- source links available for review.

---

### T-02 — Document Dataset Sources

Objective:

Document the relevant metadata for each candidate dataset.

Include:

- dataset name;
- source;
- license;
- approximate size;
- available fields;
- relevance to the project.

---

### T-03 — Select Initial Dataset

Objective:

Select the first dataset that will be used for the initial experiments.

The decision should consider:

- compatibility with coding tasks;
- ability to evaluate responses;
- dataset quality;
- licensing;
- dataset size.

---

### T-04 — Define Difficulty Labeling Method

Objective:

Define how LLM performance will be converted into:

- Easy;
- Medium;
- Hard;
- Cannot Solve.

The method must be measurable and reproducible.

Exact thresholds may remain experimental.

---

### T-05 — Prepare Llama 3 8B Evaluation Setup

Objective:

Prepare a reproducible mechanism for executing prompts with the initial target model.

Initial model:

**Llama 3 8B**

The setup should record the relevant inference configuration.

---

## 4. Backend Tasks

### T-06 — Define API Contract

Objective:

Define the minimum communication contract between the frontend and backend.

Initial operation:

Prediction request  
→ Coding prompt  
→ Difficulty prediction

The contract should remain independent from the final trained model.

---

### T-07 — Create Backend Skeleton

Objective:

Create the initial backend structure following the modular architecture defined in the architecture documentation.

Initial scope:

- API layer;
- prediction module;
- predictor interface;
- basic configuration.

---

### T-08 — Implement Temporary Prediction Endpoint

Objective:

Allow frontend development to proceed before the final model is available.

Initial flow:

Request  
→ Validation  
→ Temporary Predictor  
→ Response

The temporary predictor will later be replaced by the trained model.

---

## 5. Frontend Tasks

### T-09 — Select Frontend Technology

Objective:

Select the frontend technology required for the MVP.

The decision should prioritize:

- simplicity;
- development speed;
- backend API integration;
- maintainability.

---

### T-10 — Create Frontend Skeleton

Objective:

Create the minimum frontend project structure.

Initial scope:

- main page;
- prompt input area;
- API client;
- result area.

---

### T-11 — Implement Prompt Input Interface

Objective:

Allow the user to enter and submit a coding prompt.

Initial flow:

User  
→ Enter Prompt  
→ Submit

---

### T-12 — Connect Frontend and Temporary Backend

Objective:

Connect the initial frontend with the temporary backend prediction endpoint.

Main tasks:

- connect the frontend API client to the backend;
- send coding prompts to the prediction endpoint;
- receive the temporary prediction response;
- display the result in the frontend;
- verify basic error handling.

Initial flow:

User  
→ Frontend  
→ Backend API  
→ Temporary Predictor  
→ Backend Response  
→ Frontend

Dependency:

- T-08 — Implement Temporary Prediction Endpoint
- T-11 — Implement Prompt Input Interface

---

### T-13 — Generate Labeled Dataset

Objective:

Generate the difficulty labels required for supervised model training.

Main tasks:

- execute the selected coding prompts with the reference LLM;
- evaluate the generated responses;
- apply the defined difficulty labeling method;
- assign one difficulty class to each prompt;
- store the generated labels in the processed dataset;
- verify the resulting class distribution.

Difficulty classes:

- Easy;
- Medium;
- Hard;
- Cannot Solve.

Dependency:

- T-04 — Define Difficulty Labeling Method
- T-05 — Prepare Llama 3 8B Evaluation Setup

## 6. Modeling Tasks

### T-14 — Prepare Training Data

Objective:

Prepare the labeled dataset for model development.

Main tasks:

- define input features and target;
- create training, validation, and test splits;
- verify class distribution;
- prevent data leakage;
- prepare the input format required by the model.

Dependency:

- T-13 — Generate Labeled Dataset

---

### T-15 — Implement Baseline Model

Objective:

Create a simple reference model for comparison with the neural network.

Possible approaches:

- TF-IDF with a simple classifier;
- pretrained embeddings with a simple classifier.

Main tasks:

- train the baseline;
- evaluate it using the project metrics;
- save the results for later comparison.

Dependency:

- T-14 — Prepare Training Data

---

### T-16 — Define Neural Network Architecture

Objective:

Define the first Deep Learning architecture for difficulty classification.

Initial flow:

Prompt  
→ Pretrained Representation  
→ Neural Network  
→ Difficulty Class

Define:

- pretrained representation;
- network layers;
- activation functions;
- output layer;
- loss function;
- optimizer;
- initial training parameters.

The first architecture should remain simple and serve as the starting point for experimentation.

Dependency:

- T-14 — Prepare Training Data

---

### T-17 — Implement Neural Network

Objective:

Implement the initial neural network architecture.

Main tasks:

- implement the model;
- integrate the pretrained representation;
- implement the forward pass;
- configure four-class output;
- verify input and output dimensions.

Dependency:

- T-16 — Define Neural Network Architecture

---

### T-18 — Implement Training Pipeline

Objective:

Create the training and validation process.

Main tasks:

- create data loaders;
- implement training;
- implement validation;
- calculate loss and classification metrics;
- save model checkpoints;
- record the main experiment configuration.

Dependency:

- T-17 — Implement Neural Network

---

### T-19 — Train Initial Neural Network

Objective:

Train the first complete Deep Learning model.

Main tasks:

- run training;
- monitor training and validation performance;
- identify obvious overfitting or underfitting;
- save the trained model;
- save the experiment results.

Dependency:

- T-18 — Implement Training Pipeline

---

### T-20 — Evaluate Neural Network

Objective:

Evaluate the trained model and compare it with the baseline.

Initial metrics:

- accuracy;
- precision;
- recall;
- F1-score;
- confusion matrix.

Dependency:

- T-19 — Train Initial Neural Network
- T-15 — Implement Baseline Model

---

### T-21 — Run Model Experiments

Objective:

Evaluate a limited number of justified model configurations.

Possible experiments:

- hidden layer size;
- number of layers;
- dropout;
- learning rate;
- pretrained representation;
- frozen representation vs. fine-tuning.

Experiments should only be added when they test a clear hypothesis or address an observed problem.

Dependency:

- T-20 — Evaluate Neural Network

---

### T-22 — Select Final Predictor

Objective:

Select the model that will be integrated into the application.

Consider:

- validation and test performance;
- performance across difficulty classes;
- model complexity;
- inference requirements;
- stability of results.

Dependency:

- T-15 — Implement Baseline Model
- T-20 — Evaluate Neural Network
- T-21 — Run Model Experiments

### T-23 — Export Trained Model

Objective:

Prepare the selected predictor for integration into the backend.

Main tasks:

- save the trained model weights;
- save the required preprocessing configuration;
- save the label mapping;
- save the model configuration needed for inference;
- verify that the exported model can be loaded correctly.

Expected result:

- reusable model artifact ready for backend integration.

Dependency:

- T-22 — Select Final Predictor

### T-24 — Integrate Final Predictor into Backend

Objective:

Replace the temporary predictor with the exported trained model.

Main tasks:

- load the exported model in the backend;
- reproduce the required preprocessing;
- execute inference from the prediction endpoint;
- return the predicted difficulty;
- verify the complete backend prediction flow.

Dependency:

- T-23 — Export Trained Model
- T-08 — Implement Temporary Prediction Endpoint

### T-25 — Perform Data Audit

Objective:

Evaluate the quality and structural integrity of the selected dataset.

Main tasks:

- inspect dataset structure and schema;
- detect missing values;
- detect duplicates;
- identify invalid or inconsistent records;
- inspect data types;
- verify relevant fields;
- document data quality findings.

Dependency:

- T-03 — Select Initial Dataset

---

### T-26 — Perform Exploratory Data Analysis

Objective:

Understand the main characteristics of the selected dataset before labeling and modeling.

Main tasks:

- analyze prompt length distribution;
- analyze task or category distribution;
- inspect relevant variables;
- identify imbalance or unusual patterns;
- analyze characteristics potentially related to difficulty;
- document relevant findings.

Dependency:

- T-25 — Perform Data Audit

## 7. Git Workflow and Branch Strategy

### 7.1 Task–Branch Mapping

| ID   | Task                                    | Workstream             | Branch                                         |
| ---- | --------------------------------------- | ---------------------- | ---------------------------------------------- |
| T-01 | Research candidate datasets             | Data                   | `data/T-01-research-candidate-datasets`        |
| T-02 | Document dataset sources and licenses   | Data                   | `data/T-02-document-dataset-sources`           |
| T-03 | Select initial dataset                  | Data                   | `data/T-03-select-initial-dataset`             |
| T-04 | Define difficulty labeling method       | Labeling               | `labeling/T-04-define-difficulty-labeling`     |
| T-05 | Prepare Llama 3 evaluation setup        | Labeling / LLM         | `experiment/T-05-llama3-evaluation-setup`      |
| T-06 | Define backend API contract             | Backend                | `backend/T-06-define-api-contract`             |
| T-07 | Create backend project skeleton         | Backend                | `backend/T-07-create-project-skeleton`         |
| T-08 | Implement temporary prediction endpoint | Backend                | `backend/T-08-temporary-prediction-endpoint`   |
| T-09 | Select frontend technology              | Frontend               | `frontend/T-09-select-frontend-technology`     |
| T-10 | Create frontend project skeleton        | Frontend               | `frontend/T-10-create-project-skeleton`        |
| T-11 | Implement prompt input interface        | Frontend               | `frontend/T-11-prompt-input-interface`         |
| T-12 | Connect frontend and temporary backend  | Integration            | `integration/T-12-connect-frontend-backend`    |
| T-13 | Generate labeled dataset                | Labeling               | `labeling/T-13-generate-labeled-dataset`       |
| T-14 | Prepare training data                   | Modeling               | `model/T-14-prepare-training-data`             |
| T-15 | Implement baseline model                | Modeling               | `model/T-15-implement-baseline-model`          |
| T-16 | Define neural network architecture      | Deep Learning          | `model/T-16-define-neural-architecture`        |
| T-17 | Implement neural network                | Deep Learning          | `model/T-17-implement-neural-network`          |
| T-18 | Implement training pipeline             | Deep Learning          | `model/T-18-implement-training-pipeline`       |
| T-19 | Train initial neural network            | Deep Learning          | `model/T-19-train-initial-neural-network`      |
| T-20 | Evaluate neural network                 | Deep Learning          | `model/T-20-evaluate-neural-network`           |
| T-21 | Run model experiments                   | Deep Learning          | `experiment/T-21-run-model-experiments`        |
| T-22 | Select final predictor                  | Modeling               | `model/T-22-select-final-predictor`             |
| T-23 | Export trained model                    | Modeling / Integration | `model/T-23-export-trained-model`               |
| T-24 | Integrate final predictor into backend  | Backend / Integration  | `integration/T-24-integrate-predictor-backend` |
| T-25 | Perform data audit                      | Data                   | `data/T-25-perform-data-audit`                  |
| T-26 | Perform exploratory data analysis       | Data                   | `data/T-26-perform-eda`                         |

### 7.2 Branch Naming Convention

Each project task has a predefined task branch.

The branch naming convention is:

`<workstream>/<task-id>-<short-description>`

Examples:

- `data/T-01-research-candidate-datasets`
- `experiment/T-05-llama3-evaluation-setup`
- `model/T-17-implement-neural-network`

### 7.3 Development Workflow

Task branches are created from `master` when the corresponding task moves to
`In Progress`.

Contributors should not work directly on protected task branches. Individual
work should be performed in a temporary branch derived from the corresponding
task branch.

Example:

`data/T-01-ruben-dataset-research`
→ Pull Request
→ `data/T-01-research-candidate-datasets`

When a task is completed and reviewed, the task branch is merged into `master`
through a Pull Request.

Temporary contributor branches should be deleted after merging.

### 7.4 Branch Roles

- `master`: stable integration branch.
- Task branches: represent one project task.
- Temporary contributor branches: contain individual work before review.

### 7.5 Branch Rules

1. Do not work directly on `master`.
2. Do not work directly on protected task branches.
3. Create temporary contributor branches from the corresponding task branch.
4. Submit changes to the task branch through a Pull Request.
5. Require review before merging.
6. Merge completed task branches into `master` through a Pull Request.
7. Delete temporary contributor branches after merging.
8. Keep branch names linked to the corresponding task ID.