# AI CAD Agent - Specification-Driven Parametric CAD Generator

> Convert natural language design specifications into production-ready 3D CAD models using AI and deterministic engineering logic.



---

## 🎯 Project Vision

An agentic AI system that converts fully-defined mechanical design inputs into valid, parametric 3D CAD models (STEP/STL) using established engineering principles, LLMs, and CadQuery.

**MVP Target:** Involute spur gear generation from natural language or structured parameters.

**Future:** Shafts, assemblies, gear trains, IC engine components.

---

## ✨ Features

### Current (MVP - Phase X)
- [ ] **Phase 1: Engineering Core** *(Update status as you complete)*
  - [ ] Standard gear formula implementation (ISO/AGMA)
  - [ ] `GearParameters` data class
  - [ ] `SpurGearCalculator` with unit tests
  - [ ] Involute profile calculation

- [ ] **Phase 2: CAD Generation**
  - [ ] CadQuery integration
  - [ ] Tooth profile generation
  - [ ] Circular pattern for full gear
  - [ ] STEP/STL export

- [ ] **Phase 3: AI Interface**
  - [ ] LLM parameter extraction (natural language → JSON)
  - [ ] Prompt engineering for structured output
  - [ ] Default value inference

- [ ] **Phase 4: Simple Interface**
  - [ ] CLI tool
  - [ ] Basic web UI (Streamlit/Gradio)

### Planned (Future Phases)
- Multi-agent system (Parser, Engineer, CAD, Reviewer agents)
- RAG for standards and design guidelines
- FastAPI backend with async processing
- React/Next.js frontend with 3D viewer
- Additional components: shafts, assemblies, bearings

---

## 🏗️ Architecture
-----




