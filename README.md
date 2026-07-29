<div align="center">

# Project Amadeus

### An Open-Source Personal AI Assistant powered by Modern LLM Technologies

[![Status](https://img.shields.io/badge/status-active%20development-orange)](#)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](#)
[![LangChain](https://img.shields.io/badge/LangChain-AI%20Framework-1C3C3C)](#)

*A learning-driven project exploring the architecture behind modern AI assistants.*

</div>

---

# About

**Project Amadeus** is an open-source AI assistant project focused on exploring and implementing modern AI application architecture.

The goal of Amadeus is to create a modular personal assistant capable of natural conversations, contextual understanding, long-term memory, knowledge retrieval and customizable AI personalities.

The project combines backend engineering principles with modern AI technologies to understand how real-world LLM applications are designed, structured and deployed.

Rather than building a simple chatbot, Amadeus focuses on creating a flexible architecture where AI models, memory systems and external capabilities can evolve independently.

---

# Vision

The long-term vision of Project Amadeus is to create a personal AI assistant framework that can:

- Understand conversations and context
- Remember important information
- Retrieve knowledge from personal sources
- Use external tools when needed
- Support different AI personalities
- Provide future voice-based interaction
- Run locally or in the cloud

Inspired by fictional AI assistants, Amadeus explores the idea of creating a more personal and adaptable AI experience.

---

# Core Features

## AI Conversation Engine

- Natural language conversations
- Multi-turn dialogue support
- Context management
- LLM provider abstraction
- Streaming responses

---

## Memory System

Amadeus is designed around a flexible memory architecture.

Planned capabilities:

- Conversation history
- User-defined memories
- Long-term information storage
- Context retrieval
- Memory management and deletion

Example:

> "Remember that I prefer concise answers."

The assistant should be able to store, retrieve and manage this information when needed.

---

## Knowledge & RAG System

Future support for Retrieval-Augmented Generation:

- Document processing
- Personal knowledge bases
- Semantic search
- Vector storage
- Context-aware answers

Possible use cases:

- Documentation assistant
- Personal notes
- Learning materials
- Project knowledge base

---

## AI Personality System

Amadeus is designed to support customizable AI personas.

A personality can define:

- Communication style
- Response behavior
- Tone
- Preferences
- Future voice profile

Possible examples:

**Kurisu-inspired persona**
- Analytical
- Scientific-minded
- Curious
- Direct communication style
- Occasional sarcasm and witty responses

**Jarvis-inspired persona**
- Professional
- Highly organized
- Helpful and proactive
- Task-oriented communication

---

# Technology Stack

## Backend

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend API framework |
| SQLModel | Database models and ORM |
| PostgreSQL | Persistent storage |
| Alembic | Database migrations |
| Docker | Development and deployment environment |

---

## Artificial Intelligence

| Technology | Purpose |
|---|---|
| LangChain | LLM application orchestration |
| OpenAI API | External language models |
| Ollama | Local LLM experimentation |
| Vector Database | Future semantic memory |

---

## Future Interaction Layer

Planned:

- Speech-to-Text
- Text-to-Speech
- Voice interaction
- Custom voice profiles

---

# Architecture Overview

Project Amadeus follows a modular architecture designed around separation of responsibilities.

```text
                         User

                          │

                          ▼

                    FastAPI API

                          │

        ┌─────────────────┼─────────────────┐

        ▼                 ▼                 ▼

 Authentication       Conversation       Audio Layer

                          │

                          ▼

                  Application Services

                          │

        ┌─────────────────┼─────────────────┐

        ▼                 ▼                 ▼

      Memory            Tools          LLM Adapter

        │                 │                 │

        └─────────────────┼─────────────────┘

                          ▼

                    PostgreSQL
````

---

# Development Approach

The project follows:

* Clean Architecture principles
* SOLID design principles
* Dependency Injection
* Modular service design
* Provider abstraction
* Testable components

The goal is not only to build an AI assistant, but to understand the engineering principles behind scalable AI systems.

---

# Roadmap

## Foundation

* [x] Project concept
* [x] Architecture planning
* [x] FastAPI backend foundation
* [x] Database layer
* [x] Configuration system

---

## AI Core

* [x] LLM integration
* [x] LLM Adapter implementation
* [ ] Conversation management
* [ ] LangChain integration
* [ ] Prompt management

---

## Memory & Knowledge

* [ ] Conversation memory
* [ ] User memory system
* [ ] Memory management
* [ ] RAG pipeline
* [ ] Document processing

---

## Assistant Capabilities

* [ ] Tool execution system
* [ ] External integrations
* [ ] Personality system
* [ ] Context analysis

---

## Voice Interaction

* [ ] Speech-to-Text
* [ ] Text-to-Speech
* [ ] Voice profiles
* [ ] Real-time voice communication

---

## Deployment

* [ ] Production Docker setup
* [ ] Cloud deployment
* [ ] Monitoring
* [ ] CI/CD pipeline

---

# Project Status

Project Amadeus is currently in the **architecture and development phase**.

The current focus is building a strong foundation:

* Backend architecture
* AI integration layer
* Database design
* Memory system planning

AI capabilities will be introduced gradually as each architectural layer becomes stable.

---

# Why Amadeus?

Modern AI applications are not only about connecting to an LLM API.

A real AI assistant requires:

* Context management
* Memory systems
* Retrieval mechanisms
* Tool execution
* Scalable backend architecture
* User-focused design

Project Amadeus is an exploration of these technologies through practical implementation.

---

<div align="center">

**El Psy Kongroo**

</div>
