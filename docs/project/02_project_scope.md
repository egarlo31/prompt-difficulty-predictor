# Project Scope

## 1. Purpose

The purpose of this project is to develop and evaluate a Deep Learning system capable of estimating the difficulty of a natural-language prompt for a target Large Language Model (LLM).

The system will classify prompts into four categories:

- **Easy**
- **Medium**
- **Hard**
- **Cannot Solve**

The project will prioritize model development, experimentation, reproducibility, and compatibility with different LLMs.

## 2. In Scope

The project includes:

- research and selection of suitable datasets;
- data auditing and exploratory data analysis;
- definition and validation of the four difficulty classes;
- development of a labeling methodology based on measurable LLM performance;
- preprocessing and preparation of prompt datasets;
- use of pretrained language representations or embeddings;
- development of a custom neural network classifier;
- implementation of baseline models for comparison;
- training, validation, and testing of the proposed models;
- evaluation using classification metrics;
- comparison between different modeling approaches;
- support for multiple target LLMs;
- support for local LLM execution;
- support for API-based LLM providers;
- configuration-based model selection;
- storage of experiment results, metrics, and checkpoints;
- development of a backend for model inference;
- development of a frontend for user interaction;
- containerization of the application using Docker;
- reproducible execution of the final system.

## 3. Initial Development Scope

The first stage of development will focus only on the modeling pipeline:

1. dataset research;
2. dataset acquisition;
3. data audit;
4. exploratory data analysis;
5. label definition;
6. preprocessing;
7. baseline development;
8. pretrained representation experiments;
9. neural network development;
10. model evaluation.

Frontend, backend, API integration, and containerization will be implemented after the modeling approach has demonstrated acceptable performance.

## 4. System Boundaries

The system will receive a prompt and estimate its expected difficulty relative to a selected target LLM.

The project will not assume that difficulty is universal.

The same prompt may receive different classifications when evaluated against different models.

The architecture should therefore allow the target LLM or provider to be changed without redesigning the complete system.

## 5. Out of Scope

The initial project will not include:

- training a foundation LLM from scratch;
- development of a general-purpose chatbot;
- autonomous agent systems;
- distributed model training;
- large-scale production infrastructure;
- complex cloud orchestration;
- real-time optimization across large clusters;
- development of new tokenizers or language models from scratch;
- replacement of existing LLM inference engines.

These capabilities may be evaluated in future versions if they provide clear value to the project.

## 6. Expected Deliverables

The project is expected to produce:

- documented dataset sources;
- data audit and EDA results;
- a defined difficulty-labeling methodology;
- reproducible preprocessing pipelines;
- baseline model results;
- a trained custom neural network;
- comparative experiment results;
- model evaluation reports;
- reusable inference components;
- backend and frontend prototypes;
- containerized execution configuration;
- technical documentation describing the architecture and experimental process.

## 7. Scalability Requirement

The architecture should allow additional LLMs to be integrated without modifying the core difficulty-classification logic.

The system should support different execution mechanisms, including:

- local models;
- local inference servers;
- external APIs;
- different LLM providers.

Provider-specific implementations should remain isolated from the main modeling and application logic.

## 8. Current Limitations

The following elements are still pending validation:

- final dataset selection;
- target LLMs;
- exact difficulty thresholds;
- labeling methodology;
- pretrained representation model;
- neural network architecture;
- performance requirements;
- deployment infrastructure.