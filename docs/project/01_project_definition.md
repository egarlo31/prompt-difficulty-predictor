# Problem Definition

## 1. Problem

Large Language Models (LLMs) have different capabilities and do not solve every prompt with the same level of success.

A prompt may be simple for one model, difficult for another, or outside the model's practical capabilities. Sending every prompt directly to an LLM without estimating its difficulty can lead to unnecessary computation, poor model selection, repeated failures, and inefficient use of resources.

This project addresses the problem of estimating the difficulty of coding prompts before their execution by a target LLM.
By predicting task difficulty in advance, the system aims to support more efficient model selection, reduce unnecessary computational costs, and improve resource utilization.

## 2. Objective

Develop a Deep Learning system capable of predicting the difficulty of coding prompts for a target Large Language Model (LLM).
The initial system will focus on Llama 3 8B and classify coding prompts into four difficulty categories:

- Easy
- Medium
- Hard
- Cannot Solve

The long-term objective is to use these predictions to support automatic LLM selection, assigning coding tasks to models according to their demonstrated capabilities and computational requirements.
The initial MVP will focus on difficulty prediction rather than implementing a complete multi-model routing system.

## 3. Input

The main input is a natural-language coding prompt describing a programming task to be solved by a target LLM.
The initial experimental dataset will be based on LiveCodeBench, which provides coding problems and associated evaluation mechanisms.
Coding prompts may include:

- algorithmic programming problems;
- data structure problems;
- computational problem-solving tasks;
- programming challenges requiring code generation.

Each prompt will be processed through a tokenization and representation pipeline before being evaluated by the difficulty prediction model.

## 4. Output

The system returns a predicted difficulty classification for a coding prompt.
The four difficulty categories are defined according to the observed success rate of the target LLM:

- Easy: coding tasks associated with a high success rate.
- Medium: coding tasks associated with an intermediate success rate.
- Hard: coding tasks associated with a low success rate.
- Cannot Solve: coding tasks for which the target LLM demonstrates no successful solutions under the established evaluation protocol.

Success will be measured by evaluating generated code against predefined test cases.
Numerical thresholds separating the four categories will be established through experimental analysis.

## 5. Proposed Solution

The project will use a hybrid architecture composed of:

- pretrained language representations;
- a custom neural network classifier;
- LLM-based evaluation for generating difficulty labels;
- automated code evaluation using LiveCodeBench;
- an extensible LLM integration layer.

The initial target model will be Llama 3 8B, executed
locally through Ollama.

The system will follow two main workflows:

### Difficulty Labeling

Coding Prompt
→ Target LLM
→ Generated Code
→ Isolated Code Execution
→ Test Case Evaluation
→ Success Rate
→ Difficulty Label

### Difficulty Prediction

Coding Prompt
→ Tokenization
→ Pretrained Representation
→ Custom Neural Network
→ Predicted Difficulty Class

The target LLM will be used during experimentation
to generate solutions and establish difficulty labels.

The trained neural network will predict difficulty
without requiring the target LLM to execute the
coding prompt beforehand.

The architecture will allow additional LLM providers
to be integrated in future versions.

## 6. Difficulty Definition

Prompt difficulty is defined relative to the capabilities of the target LLM.

The initial reference model will be Llama 3 8B.
Difficulty labels will be derived from measurable performance on coding tasks using automated test cases.

The success rate will represent the percentage of successful code-generation attempts for a given prompt under a predefined evaluation protocol.

The resulting success rates will be used to assign prompts to the four difficulty categories.

The exact thresholds and number of evaluation attempts will be determined experimentally.

The trained difficulty predictor will be evaluated separately using classification metrics, including accuracy, precision, recall, F1-score, and confusion matrices.

## 7. Initial Scope

The first development stage will focus on:

- acquiring coding prompts from LiveCodeBench;
- auditing and analyzing the dataset;
- defining the four difficulty classes;
- establishing a success-rate-based labeling methodology;
- evaluating generated code using automated test cases;
- implementing controlled execution for generated code;
- generating and storing difficulty labels;
- preprocessing and tokenizing coding prompts;
- creating baseline models;
- training the custom neural network;
- evaluating classification performance;
- comparing results against a golden reference.

The initial experiments will use Llama 3 8B
as the reference LLM.

Experiment configurations, results, and evaluation
metrics will be stored in JSON format.

Frontend, backend, API integration, and containerized
application deployment will be developed after the
modeling approach has been validated.

## 8. Current Open Decisions

The following elements are still under evaluation:

- exact difficulty labeling thresholds;
- number of code-generation attempts per prompt;
- final LiveCodeBench dataset selection and partitioning;
- pretrained representation model;
- custom neural network architecture;
- golden reference construction and validation;
- final experimental evaluation protocol;
- secure sandbox execution mechanisms.

The initial implementation will use:

- Python as the main programming language;
- LiveCodeBench as the initial benchmark;
- Llama 3 8B as the reference LLM;
- tokenization and pretrained representations;
- JSON for storing experiment results;
- classification metrics including accuracy,
  precision, recall, F1-score, and confusion matrices.