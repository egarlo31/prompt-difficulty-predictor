# Problem Definition

## 1. Problem

Large Language Models (LLMs) have different capabilities and do not solve every prompt with the same level of success.

A prompt may be simple for one model, difficult for another, or outside the model's practical capabilities. Sending every prompt directly to an LLM without estimating its difficulty can lead to unnecessary computation, poor model selection, repeated failures, and inefficient use of resources.

This project addresses the problem of estimating prompt difficulty before execution.

## 2. Objective

Develop a Deep Learning system that receives a natural-language prompt and predicts its expected difficulty for a target LLM.

The system will classify each prompt into one of four categories:

- **Easy**
- **Medium**
- **Hard**
- **Cannot Solve**

## 3. Input

The main input is a natural-language prompt representing a task to be solved by an LLM.

Examples include:

- mathematical reasoning problems;
- programming tasks;
- question answering;
- text analysis;
- logical reasoning tasks.

## 4. Output

The system returns a difficulty classification for the prompt:

- **Easy:** the target LLM is expected to solve the task reliably.
- **Medium:** the task is expected to be solvable but may require more reasoning or produce occasional failures.
- **Hard:** the task is expected to have a low success rate or require significant reasoning.
- **Cannot Solve:** the task is expected to exceed the demonstrated capabilities or limitations of the target LLM.

These definitions are initial and will later be refined using experimental results.

## 5. Proposed Solution

The project will use a hybrid architecture composed of:

- pretrained language representations;
- a custom neural network classifier;
- LLM evaluation for generating or validating difficulty labels;
- support for both local LLMs and API-based LLMs.

The general flow is:

Prompt → Pretrained Representation → Custom Neural Network → Difficulty Class

## 6. Difficulty Definition

Difficulty is relative to the target model.

The same prompt may receive different difficulty labels depending on the LLM being evaluated.

For this reason, the project will define difficulty using measurable model performance rather than only subjective human judgment.

## 7. Initial Scope

The first development stage will focus on:

- finding suitable datasets;
- auditing and analyzing the data;
- defining the four difficulty classes;
- establishing a labeling methodology;
- creating baseline models;
- training the custom neural network;
- evaluating classification performance.

Frontend, backend, API integration, and containerized deployment will be developed after the modeling approach has been validated.

## 8. Current Open Decisions

The following elements are still under evaluation:

- datasets;
- target LLMs;
- labeling thresholds;
- pretrained representation model;
- neural network architecture;
- final evaluation metrics.