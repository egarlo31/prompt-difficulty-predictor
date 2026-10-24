# Project Scope

## 1. Purpose

The purpose of this project is to develop and evaluate
a Deep Learning system capable of predicting the
difficulty of coding prompts for a target Large
Language Model (LLM).

The initial reference model will be Llama 3 8B.

The system will classify coding prompts into four
difficulty categories:

- **Easy**
- **Medium**
- **Hard**
- **Cannot Solve**

Difficulty will be determined using measurable
code-generation success rates obtained through
automated evaluation.

The project will prioritize model development,
experimentation, reproducibility, and modularity.

The long-term objective is to support efficient
LLM selection based on predicted task difficulty,
model capabilities, and computational requirements.

## 2. In Scope

The project includes:

- research and selection of coding prompt datasets;
- acquisition of programming problems from LiveCodeBench;
- data auditing and exploratory data analysis;
- definition and validation of the four difficulty classes;
- development of a labeling methodology based on
  measurable LLM code-generation performance;
- evaluation of generated code using automated test cases;
- implementation of isolated execution mechanisms for untrusted LLM-generated code;
- calculation of success rates for coding prompts;
- generation and storage of difficulty labels;
- preprocessing and tokenization of coding prompts;
- use of pretrained language representations;
- development of a custom neural network classifier;
- implementation of baseline models for comparison;
- training, validation, and testing of the proposed models;
- evaluation using classification metrics;
- comparison against a validated golden reference;
- comparison between different modeling approaches;
- use of Llama 3 8B as the initial reference LLM;
- local LLM execution through Ollama;
- development of a modular LLM integration interface;
- storage of experiment configurations, results,
  and metrics using JSON;
- storage of trained model checkpoints;
- development of a backend for model inference;
- development of a frontend for user interaction;
- containerization of the final application;
- reproducible execution of experiments and predictions.

The initial MVP will use Llama 3 8B as its reference
LLM.

Support for additional LLMs and external API providers
will be considered in future development stages
through the modular integration architecture.

## 3. Initial Development Scope

The first development stage will focus on the
modeling and experimental evaluation pipeline:

1. dataset research;
2. LiveCodeBench dataset acquisition;
3. data audit;
4. exploratory data analysis;
5. difficulty label definition;
6. implementation of a secure code execution environment;
7. Llama 3 8B integration for experimental evaluation;
8. automated evaluation of generated code;
9. success rate calculation and difficulty labeling;
10. dataset preprocessing and tokenization;
11. training, validation, and test dataset preparation;
12. baseline development;
13. pretrained representation experiments;
14. custom neural network development;
15. model evaluation;
16. comparison against a golden reference.

Experiment configurations, outputs, labels, and
evaluation metrics will be stored in JSON format.

The secure execution environment will be developed
during the experimental stage because generated
code must be evaluated safely.

Frontend development, backend application development,
API integration, and final application deployment
will take place after the modeling approach has
demonstrated acceptable performance.

## 4. System Boundaries

The system will receive a coding prompt and predict
its expected difficulty relative to a target LLM.

The initial target model will be Llama 3 8B.

Prompt difficulty is model-dependent and will not
be considered universal.

The same coding prompt may receive different
difficulty classifications when evaluated against
different target LLMs.

The project separates two main processes:

### Experimental Evaluation

The target LLM generates code solutions for
coding prompts.

Generated solutions are executed in an isolated
environment and evaluated using automated test cases.

The resulting success rates are used to generate
difficulty labels for model training and evaluation.

### Difficulty Prediction

The trained Deep Learning model receives a coding
prompt and predicts its difficulty category.

Difficulty prediction does not require executing
the coding prompt using the target LLM.

### Future Model Selection

Future versions may use predicted difficulty to
select an appropriate LLM according to its
capabilities and computational requirements.

Automatic multi-model routing is not part of
the initial MVP.

The architecture will maintain separation between
the difficulty prediction model and the target
LLM integration layer.

Supporting another target LLM may require new
experimental labels, calibration, or retraining.

## 5. Out of Scope

The initial project will not include:

- training a foundation LLM from scratch;
- development of a general-purpose chatbot;
- autonomous agent systems;
- automatic routing between multiple LLMs;
- simultaneous integration of multiple LLM providers;
- distributed model training;
- large-scale production infrastructure;
- complex cloud orchestration;
- real-time optimization across large clusters;
- development of new tokenizers or language models
  from scratch;
- replacement of existing LLM inference engines.

These capabilities may be evaluated in future
versions if they provide clear value to the project.

## 6. Expected Deliverables

The project is expected to produce:

- documented LiveCodeBench dataset sources;
- data audit and EDA reports;
- a defined difficulty-labeling methodology;
- a secure experimental code execution environment;
- automated code evaluation components;
- a labeled coding prompt dataset;
- success rate measurements for evaluated prompts;
- reproducible preprocessing and tokenization pipelines;
- baseline model results;
- a trained custom neural network;
- saved model checkpoints;
- experiment configurations and metrics stored in JSON;
- comparative experiment results;
- classification evaluation reports;
- a validated golden reference for evaluation;
- reusable inference components;
- modular LLM integration components;
- backend and frontend prototypes;
- containerized application configuration;
- technical documentation describing the architecture,
  experimental methodology, and evaluation process.

## 7. Scalability Requirement

The architecture should allow additional LLMs
to be integrated without redesigning the main
experimental and modeling infrastructure.

The initial implementation will use Llama 3 8B
through Ollama.

The LLM integration layer should provide a common
interface for communicating with target models.

Future implementations may support:

- additional local models;
- local inference servers;
- external APIs;
- different LLM providers;
- configuration-based model selection.

Provider-specific implementations should remain
isolated from the main modeling and application logic.

The difficulty prediction model will remain separate
from the LLM integration layer.

Compatibility with additional target LLMs will
require validation of model-specific difficulty
labels and prediction performance.

## 8. Current Limitations

The following elements are still pending validation:

- final LiveCodeBench dataset version and partitioning;
- exact difficulty classification thresholds;
- number of code-generation attempts per prompt;
- final success rate evaluation protocol;
- pretrained representation model selection;
- custom neural network architecture;
- golden reference construction and validation;
- model acceptance criteria;
- minimum classification performance requirements;
- final sandbox isolation and security mechanisms;
- deployment infrastructure.

The following decisions have already been established:

- coding prompts are the exclusive task domain;
- LiveCodeBench will be the initial benchmark;
- Llama 3 8B will be the reference LLM;
- Python will be the main development language;
- tokenization will be part of the modeling pipeline;
- difficulty labels will be based on code-generation
  success rates;
- prediction performance will be evaluated using
  accuracy, precision, recall, F1-score,
  and confusion matrices;
- experiment configurations and metrics will
  be stored in JSON;
- the initial MVP will focus on difficulty prediction;
- additional LLM providers will be considered
  in future development stages.