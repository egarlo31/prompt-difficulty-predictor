# Project Plan

## 1. Purpose

Organize the development of a Deep Learning system that predicts the difficulty of coding prompts for a target Large Language Model.

The initial reference model will be **Llama 3 8B**, while the system will remain compatible with other local or API-based LLMs.

---

## 2. Development Phases

### Phase 1 — Dataset Research

Identify and select datasets suitable for the project.

Main objectives:

- find coding prompt datasets;
- identify relevant benchmarks;
- document sources and licenses;
- select the initial dataset.

---

### Phase 2 — Data Audit and EDA

Evaluate the selected dataset before modeling.

Main objectives:

- inspect dataset structure and quality;
- detect missing values, duplicates, and inconsistencies;
- analyze prompt characteristics and task distribution;
- identify possible difficulty-related patterns.

---

### Phase 3 — Difficulty Labeling

Generate the target variable required for supervised learning.

The initial difficulty classes are:

- **Easy**
- **Medium**
- **Hard**
- **Cannot Solve**

Labels must be based on measurable LLM performance rather than subjective judgment.

The initial reference model will be **Llama 3 8B**.

General labeling flow:

Coding Prompt  
→ Target LLM  
→ Response Evaluation  
→ Performance Measurement  
→ Difficulty Class

---

### Phase 4 — Data Preparation

Prepare the labeled dataset for model development.

Main objectives:

- standardize the dataset schema;
- preprocess prompts when required;
- create training, validation, and test splits;
- prevent data leakage.

---

### Phase 5 — Baseline

Develop a simple baseline to establish a reference performance level.

Possible approaches include:

- TF-IDF;
- pretrained embeddings;
- simple machine learning classifiers.

The baseline will be used as a reference for evaluating the Deep Learning model.

---

### Phase 6 — Deep Learning Model

Develop the main difficulty prediction model.

Initial architecture:

Prompt  
→ Pretrained Representation  
→ Custom Neural Network  
→ Difficulty Class

Different pretrained representations and neural network configurations may be evaluated experimentally.

Fine-tuning will only be introduced if justified by experimental results.

---

### Phase 7 — Model Evaluation

Evaluate the baseline and Deep Learning models.

Initial metrics include:

- accuracy;
- precision;
- recall;
- F1-score;
- confusion matrix.

The evaluation should also analyze errors between the four difficulty classes.

The objective of this phase is to select the model that will be integrated into the application.

---

### Phase 8 — Backend Development

Develop the backend required to expose the difficulty prediction functionality.

Main objectives:

- create the backend project structure;
- implement the prediction API;
- validate incoming coding prompts;
- connect the API with the difficulty predictor;
- support a temporary mock predictor during early development;
- integrate the trained model once it is validated;
- maintain separation between application logic and external providers.

Initial backend flow:

Request  
→ Validation  
→ Application Logic  
→ Difficulty Predictor  
→ Prediction  
→ Response

The backend will follow the modular architecture defined in the architecture documentation.

---

### Phase 9 — Frontend Development

Develop the minimum user interface required to interact with the system.

Main objectives:

- create the frontend project structure;
- implement the coding prompt input;
- implement prompt submission;
- connect the frontend with the backend API;
- receive the predicted difficulty;
- display the prediction to the user;
- implement basic loading and error handling.

Initial frontend flow:

User  
→ Enter Coding Prompt  
→ Submit Prompt  
→ Backend Request  
→ Receive Prediction  
→ Display Result

The initial frontend should remain focused on the core prediction workflow.

Authentication, user profiles, dashboards, and prediction history are outside the initial MVP unless later required.

---

### Phase 10 — System Integration

Integrate the frontend, backend, trained difficulty predictor, and required LLM integration components.

Main objectives:

- connect the frontend with the backend API;
- replace temporary predictions with the validated trained model;
- integrate the required local or API-based LLM provider;
- verify communication between application components;
- validate request and response handling;
- test the complete user workflow;
- verify error handling between components.

Final application flow:

User  
→ Frontend  
→ Backend API  
→ Difficulty Predictor  
→ Prediction  
→ Backend  
→ Frontend  
→ User

When communication with a target LLM is required:

Backend  
→ LLM Integration  
→ Local or External LLM Provider

Frontend and backend development may progress in parallel once their communication contract has been defined.

---

### Phase 11 — Deployment

Prepare the integrated application for containerized execution.

Main objectives:

- containerize the frontend;
- containerize the backend;
- optionally containerize the local LLM service;
- configure communication between application components;
- validate the complete containerized system.

External LLM APIs will remain outside the local container infrastructure.

---

## 3. Development Flow

The project contains two main development tracks that may progress partially in parallel.

### Modeling Track

Dataset Research  
→ Data Audit and EDA  
→ Difficulty Labeling  
→ Data Preparation  
→ Baseline  
→ Deep Learning Model  
→ Model Evaluation  
→ Trained Difficulty Predictor

### Application Track

Backend Development  
→ Frontend Development  
→ System Integration  
→ Deployment

Frontend and backend development may begin before the final difficulty predictor is available by using temporary or mock predictions.

Both tracks converge during system integration, when the validated predictor is connected to the application.

---

## 4. Collaboration Workflow

Development work will be isolated using Git branches.

Examples:

- `feature/data-audit`
- `feature/eda`
- `feature/labeling`
- `feature/baseline`
- `feature/neural-network`
- `feature/backend`
- `feature/frontend`
- `feature/llm-integration`

Changes will be integrated into `master` through Pull Requests.

Detailed tasks, assignments, dependencies, and task status will be maintained separately from this document.

---

## 5. Current Open Decisions

The following elements remain under evaluation:

- final dataset or datasets;
- exact difficulty labeling criteria;
- difficulty class thresholds;
- pretrained representation model;
- neural network architecture;
- additional target LLMs;
- final evaluation protocol;
- final frontend technology;
- final backend technology;
- final LLM integration mechanism;
- final deployment configuration.

These decisions will be resolved as they become necessary during development and experimentation.