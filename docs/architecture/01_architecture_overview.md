# Architecture Overview

## 1. Purpose

This document describes the general architecture of the Prompt Difficulty Predictor.

The system is designed to estimate the difficulty of coding prompts for a target Large Language Model before task execution.

The architecture combines:

- pretrained language representations;
- a custom neural network classifier;
- LLM-based evaluation;
- local and API-based LLM integration;
- frontend and backend components.

## 2. General System Architecture

The system is organized into four main components:

- **Frontend**
- **Backend**
- **Modeling**
- **LLM Integration**

The frontend provides the user interface, while the backend coordinates application logic and model inference.

The modeling component is responsible for developing the prompt difficulty classifier.

The LLM integration component provides access to local or API-based target LLMs without coupling the rest of the system to a specific provider.

![General System Architecture](images/general_system_architecture.svg)

## 3. Modeling Architecture

The modeling component develops and evaluates the prompt difficulty predictor.

The initial modeling flow is:

Prompt → Preprocessing / Tokenization → Pretrained Representation → Custom Neural Network → Difficulty Class

The pretrained component transforms the coding prompt into a semantic representation.

The custom neural network uses that representation to classify the prompt into one of four categories:

- **Easy**
- **Medium**
- **Hard**
- **Cannot Solve**

The target LLM is not part of the prediction path itself. It is used during experimentation, labeling, benchmarking, and evaluation.

![Modeling Architecture](images/modeling_inference_architecture.svg)

## 4. Target LLM

The target LLM is the model whose ability to solve a coding prompt is being estimated.

The initial reference model is **Llama 3 8B**.

Difficulty is defined relative to the selected target model. A prompt may therefore receive a different difficulty classification when evaluated against another LLM.

The target LLM is separate from the pretrained representation model used by the difficulty predictor.

The architecture must allow additional target LLMs to be evaluated without redesigning the predictor.

## 5. LLM Integration

The LLM integration component provides a common interface for interacting with target LLMs.

It should support:

- local models;
- local inference services;
- API-based models;
- multiple providers.

Provider-specific logic should remain isolated from the main application and modeling components.

The purpose of this layer is to allow target LLMs to be replaced or added without modifying the core system.

![LLM Integration](images/llm_integration_architecture.svg)

## 6. Training and Data Flow

The initial modeling workflow is:

Dataset → Data Audit / EDA → Difficulty Labeling → Data Preparation → Training → Evaluation → Trained Model

Raw datasets should remain unchanged.

Any transformation should generate intermediate or processed data so that experiments remain reproducible.

![Training and Data Flow](images/training_data_flow.svg)

## 7. Application Architecture

Once the modeling approach is validated, the trained difficulty predictor will be integrated into the application.

The expected runtime flow is:

User → Frontend → Backend API → Difficulty Predictor → Prediction

The backend coordinates inference and may communicate with the selected target LLM through the LLM integration component when required.

The application logic should remain independent from specific LLM providers or infrastructure implementations.

![Application Architecture](images/system_architecture.svg)

## 8. Deployment

The final system is expected to support containerized execution.

The main deployable components are:

- frontend;
- backend;
- optional local LLM service.

External LLM APIs will remain outside the local container infrastructure.

![Deployment](images/container_deployment_architecture.svg)

## 9. Architectural Principles

The architecture should maintain:

- separation between modeling and application code;
- independence from a specific LLM provider;
- replaceable model components;
- reproducible experiments;
- containerized deployment.

## 10. Current Open Decisions

The following elements remain under evaluation:

- final datasets;
- pretrained representation model;
- neural network architecture;
- difficulty labeling thresholds;
- additional target LLMs;
- final frontend framework;
- final backend framework;
- final deployment configuration.