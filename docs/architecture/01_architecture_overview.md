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

The system is divided into four main components:

- **Frontend**
- **Backend**
- **Modeling**
- **LLM Integration**

The general flow is:

Prompt → Frontend → Backend → Difficulty Predictor → Difficulty Class

The output classes are:

- **Easy**
- **Medium**
- **Hard**
- **Cannot Solve**

**[General system architecture diagram]**

## 3. Modeling Architecture

The modeling component is responsible for developing and evaluating the difficulty classifier.

The initial architecture is:

Prompt → Preprocessing / Tokenization → Pretrained Representation → Custom Neural Network → Difficulty Class

The pretrained component provides a representation of the coding prompt, while the custom neural network performs the final classification.

Different pretrained representations and neural network configurations may be evaluated experimentally.

**[Modeling architecture diagram]**

## 4. Target LLM

The target LLM represents the model whose ability to solve a prompt is being estimated.

The initial reference model is **Llama 3 8B**.

Difficulty is therefore relative to the selected target model. A prompt may be easy for one LLM and difficult for another.

The architecture must allow additional LLMs to be evaluated without redesigning the complete system.

## 5. LLM Integration

LLM communication will be separated from the main application logic through an abstraction layer.

The system should support:

- local LLMs;
- local inference services;
- API-based LLMs;
- multiple providers.

Possible execution mechanisms include:

- Ollama;
- Hugging Face;
- llama.cpp;
- OpenRouter;
- other compatible providers.

**[LLM integration architecture diagram]**

## 6. Training and Data Flow

The initial modeling workflow is:

Dataset → Data Audit → EDA → Difficulty Labeling → Preprocessing → Training → Evaluation → Trained Model

Raw datasets should remain unchanged. Any transformation should generate new intermediate or processed data.

**[Training and data flow diagram]**

## 7. Application Architecture

Once the modeling approach is validated, the trained model will be integrated into the application.

The expected runtime flow is:

User → Frontend → Backend API → Difficulty Predictor → Prediction

When required, the backend may also communicate with the selected LLM through the LLM integration layer.

**[Application runtime diagram]**

## 8. Deployment

The final system is expected to support containerized execution.

The main deployable components are expected to be:

- frontend;
- backend;
- optional local LLM service.

External LLM APIs will remain outside the local container infrastructure.

**[Container deployment diagram]**

## 9. Architectural Principles

The architecture should maintain:

- separation between experimentation and application code;
- independence from a specific LLM provider;
- replaceable pretrained models;
- replaceable neural network architectures;
- reproducible experiments;
- support for local and API-based inference;
- containerized deployment.

## 10. Current Open Decisions

The following elements remain under evaluation:

- final datasets;
- pretrained representation model;
- neural network architecture;
- difficulty labeling thresholds;
- additional target LLMs;
- final frontend and backend technologies;
- final deployment configuration.