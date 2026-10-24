# Project Plan

## 1. Purpose

Organize the development of a Deep Learning system
capable of predicting the difficulty of coding
prompts for a target Large Language Model (LLM).

The initial reference model will be Llama 3 8B,
executed locally through Ollama.

The system will classify coding prompts into
four difficulty categories:

- Easy
- Medium
- Hard
- Cannot Solve

The initial MVP will focus on difficulty prediction
using a single reference LLM.

The architecture will remain modular to support
additional local or API-based LLMs in future versions.

The long-term objective is to support efficient
LLM selection based on predicted coding prompt
difficulty and model capabilities.

---

## 2. Development Phases

### Phase 1 — Dataset Research

Identify and prepare the initial coding prompt
dataset for experimentation.

The initial benchmark will be LiveCodeBench.

Main objectives:

- investigate LiveCodeBench dataset structure;
- identify available coding problems and test cases;
- review dataset versions and available subsets;
- verify licensing and usage requirements;
- identify the evaluation mechanisms required
  for generated code;
- select the initial experimental dataset;
- document dataset sources and versions.

The selected dataset will serve as the foundation
for LLM evaluation and difficulty labeling.

---

### Phase 2 — Data Audit and EDA

Evaluate the selected dataset before modeling.

Main objectives:

- inspect dataset structure and quality;
- detect missing values, duplicates, and inconsistencies;
- analyze prompt characteristics and task distribution;
- identify possible difficulty-related patterns.
- analyze available test case coverage;
- identify potential data leakage and benchmark
  contamination risks.
- define a preliminary dataset partitioning strategy;
- identify potential overlap between training,
  validation, and test problems;

---

### Phase 3 — Difficulty Labeling

Generate difficulty labels based on measurable
code-generation performance.

The initial reference LLM will be Llama 3 8B,
executed locally through Ollama.

The four difficulty categories are:

- Easy
- Medium
- Hard
- Cannot Solve

Main objectives:

- integrate Llama 3 8B through Ollama;
- develop a modular LLM integration interface;
- define the code-generation evaluation protocol;
- implement a secure sandbox for executing
  untrusted LLM-generated code;
- configure execution timeouts and resource limits;
- prevent unauthorized filesystem and network access;
- evaluate generated solutions using automated
  test cases from the selected benchmark;
- define the number of generation attempts per prompt;
- calculate success rates;
- establish difficulty labeling thresholds;
- assign difficulty labels to coding prompts;
- store experimental results and labels in JSON.

General labeling flow:

Coding Prompt
→ Llama 3 8B
→ Generated Code
→ Secure Sandbox
→ Test Case Execution
→ Success Rate Calculation
→ Difficulty Label

A code-generation attempt will be considered
successful only when the generated solution passes
all required test cases within the established
execution constraints.

The success rate will represent the percentage
of successful attempts for each coding prompt.

Difficulty thresholds and evaluation attempts
will be defined through experimental analysis.

The Cannot Solve category will represent prompts
for which no successful solution was observed
under the established evaluation protocol.

Experiment records will include model configuration,
generation parameters, execution results,
success rates, and assigned difficulty labels.

---

### Phase 4 — Data Preparation

Prepare the labeled coding prompt dataset
for supervised learning.

Main objectives:

- standardize the labeled dataset schema;
- validate generated difficulty labels;
- preprocess coding prompts when required;
- implement the tokenization pipeline;
- prepare inputs for pretrained representations;
- define training, validation, and test splits;
- prevent data leakage between dataset partitions;
- preserve raw experimental data;
- generate reproducible processed datasets;
- document preprocessing configurations.

Training, validation, and test partitions
will remain separate during model development.

Preprocessing transformations requiring
parameter estimation will be fitted only
using training data.

Dataset versions and partition information
will be recorded for reproducibility.

---

### Phase 5 — Baseline

Develop a simple baseline to establish a reference performance level.

Possible approaches include:

- TF-IDF;
- pretrained embeddings;
- simple machine learning classifiers.

Baseline models will be evaluated using the same
dataset partitions and classification metrics
as the proposed Deep Learning model.

---

### Phase 6 — Deep Learning Model

Develop and train the custom neural network
responsible for coding prompt difficulty prediction.

The model will use pretrained language
representations as input features.

Initial architecture:

Coding Prompt
→ Tokenization
→ Pretrained Representation
→ Custom Neural Network
→ Difficulty Class

Main objectives:

- select a pretrained representation model;
- implement the tokenization pipeline;
- develop the custom neural network classifier;
- define training configurations;
- evaluate different neural network architectures;
- experiment with relevant hyperparameters;
- train the model using labeled coding prompts;
- validate model performance;
- save model checkpoints and training metrics.

The neural network will predict one of four
difficulty classes:

- Easy
- Medium
- Hard
- Cannot Solve

Different pretrained representations and
neural network configurations may be evaluated.

Fine-tuning will only be introduced if justified
by experimental results.

---

### Phase 7 — Model Evaluation

Evaluate the performance of baseline models
and the proposed Deep Learning classifier.

The evaluation will measure how accurately
the system predicts coding prompt difficulty.

Main evaluation metrics:

- accuracy;
- precision;
- recall;
- macro-F1 score;
- per-class F1-score;
- confusion matrix.

Main objectives:

- evaluate classification performance;
- analyze prediction errors across difficulty classes;
- compare baseline and Deep Learning models;
- evaluate performance against a validated
  golden reference;
- analyze class imbalance;
- define model acceptance criteria before final testing;
- evaluate model performance against predefined criteria;
- identify model limitations;
- select the final difficulty predictor.

The evaluation will report overall performance
and class-specific metrics.

Model selection and tuning will use validation
results, while the held-out test set will be
reserved for final evaluation.

The final predictor must demonstrate acceptable
performance according to predefined evaluation
criteria before application integration.

---

### Phase 8 — Backend Development

Develop the backend required to expose the difficulty prediction functionality.

Main objectives:

- create the backend project structure;
- implement the prediction API;
- validate incoming coding prompts;
- connect the API with the difficulty predictor;
- support a mock predictor for isolated API testing;
- integrate the trained model once it is validated;
- maintain separation between application logic and external providers.

Initial backend flow:

Request  
→ Validation  
→ Application Logic  
→ Difficulty Predictor  
→ Prediction  
→ Response

Backend development will begin after the
difficulty prediction model has completed
the initial evaluation and validation stage.

The backend will expose the trained difficulty
predictor through a prediction API.

The initial prediction service will not require
executing coding prompts through Llama 3 8B.

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

Integrate the frontend, backend, and validated
difficulty prediction model.

Main objectives:

- connect the frontend with the backend API;
- replace temporary predictions with the
  validated trained model;
- integrate the model preprocessing
  and tokenization components;
- verify communication between application components;
- validate request and response handling;
- test the complete prediction workflow;
- verify error handling;
- confirm reproducible inference results.

Final application flow:

User
→ Frontend
→ Backend API
→ Input Validation
→ Tokenization
→ Difficulty Predictor
→ Predicted Difficulty
→ Frontend
→ User

The Llama 3 8B integration developed during
experimentation will remain available as a
separate component.

The initial prediction workflow will not require
executing the coding prompt using the target LLM.

Future versions may integrate additional
LLM providers and automatic model selection.

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

The experimental code execution sandbox and
the final application deployment environment
will be treated as separate components.

The sandbox will be implemented during the
experimental labeling stage.

Final application containerization will take
place after system integration.

---

## 3. Development Flow

The project will follow a sequential development
strategy divided into two main tracks.

The modeling and experimental evaluation track
will be completed and validated before beginning
the application development track.

### Modeling and Experimental Track

LiveCodeBench Research
→ Data Audit and EDA
→ Secure Sandbox Implementation
→ Llama 3 8B Experimental Integration
→ Automated Code Evaluation
→ Difficulty Labeling
→ Data Preparation and Tokenization
→ Baseline Development
→ Deep Learning Model
→ Model Evaluation
→ Validated Difficulty Predictor

Dataset partitioning and leakage prevention
will be planned before experimental calibration
and model training.

### Application Track

Backend Development
→ Frontend Development
→ System Integration
→ Deployment

The application track will begin after the
difficulty prediction model has demonstrated
acceptable performance.

The validated difficulty predictor will be
integrated into the backend and exposed
through the application API.

The final application will allow users to
submit coding prompts and receive predicted
difficulty classifications.

Automatic selection between multiple LLMs
will remain outside the initial MVP.

---

## 4. Collaboration Workflow

Development work will be isolated using Git branches.

Examples:

- `feature/dataset-research`
- `feature/data-audit`
- `feature/eda`
- `feature/sandbox`
- `feature/ollama-integration`
- `feature/code-evaluation`
- `feature/labeling`
- `feature/tokenization`
- `feature/baseline`
- `feature/neural-network`
- `feature/model-evaluation`
- `feature/backend`
- `feature/frontend`
- `feature/deployment`

Changes will be integrated into `master`
through Pull Requests.

Experimental configurations, results,
and evaluation metrics will be stored
in JSON format.

Model checkpoints will be stored using
the appropriate framework-specific format.

Detailed tasks, assignments, dependencies,
and task status will be maintained
separately from this document.

---

## 5. Current Open Decisions

The following elements remain under evaluation:

- final LiveCodeBench dataset version and partitioning;
- number of code-generation attempts per prompt;
- exact difficulty labeling thresholds;
- final code evaluation protocol;
- secure sandbox isolation mechanisms;
- pretrained representation model;
- custom neural network architecture;
- golden reference construction and validation;
- model acceptance criteria;
- minimum classification performance requirements;
- final frontend technology;
- final backend technology;
- final deployment configuration.

The following decisions have already been established:

- the project will focus exclusively on coding prompts;
- LiveCodeBench will be the initial benchmark;
- Llama 3 8B will be the reference LLM;
- Ollama will provide local LLM inference;
- Python will be the main programming language;
- generated code will be evaluated using automated tests;
- code evaluation will use isolated execution;
- difficulty labels will be based on measured success rates;
- tokenization will be part of the modeling pipeline;
- the main classifier will use pretrained representations
  and a custom neural network;
- classification evaluation will include accuracy,
  precision, recall, F1-score, and confusion matrices;
- experimental results and metrics will be stored in JSON;
- the modeling approach will be validated before
  application development;
- multi-model routing will remain outside the MVP.

Remaining technical decisions will be resolved
during the corresponding experimental
and development phases.