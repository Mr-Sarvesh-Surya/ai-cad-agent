# agents.md — Layer 1: Intent Classification Pipeline
# Agentic CAD System — Production Build Guide

---

## AGENT INSTRUCTIONS — READ BEFORE STARTING

You are building Layer 1 of an Agentic CAD system.
This layer converts raw natural language into a fully resolved
engineering specification JSON that Layer 2 (RAG Template Engine) consumes.

### Non-Negotiable Rules
- Complete every PHASE fully before moving to the next
- At the end of every PHASE: stop, review all files written,
  confirm they are correct, then proceed
- Never write logic inside `__init__.py` files
- Never hardcode model names, thresholds, or API keys in logic files
- Every LLM prompt lives in a `.txt` file under `layer1/prompts/`
- Never call the LLM library directly — always use `LLMClient`
- The `InferenceEngine` must have zero LLM calls — pure Python only
- All exceptions must be typed custom exceptions — never raise raw `Exception`
- All log lines must be structured JSON — never plain strings

### This is the file structure 
agentic_cad/
├── layer1/
│ ├── substage1_classifier/
│ ├── substage2_extractor/
│ ├── substage3_dag/
│ ├── substage4_relationships/
│ ├── gate/
│ │ └── checks/
│ ├── schemas/
│ ├── prompts/
│ └── knowledge_base/
│ ├── parameter_schemas/
│ ├── standards_defaults/
│ └── template_registry.json
├── core/
├── config/
└── tests/
├── integration/
└── fixtures/

