# LectureLens AI

LectureLens AI is an AI-powered Chrome extension that transforms YouTube lectures into an interactive learning experience using Retrieval-Augmented Generation (RAG), semantic search, and intelligent transcript understanding.

The system enables users to ask natural language questions directly while watching educational videos and receive context-aware answers with timestamped references from the lecture.

Designed with a production-oriented architecture, LectureLens AI combines FastAPI, FAISS, Redis, Celery, MongoDB, and modern NLP models to support scalable video ingestion and intelligent retrieval workflows.

---

## 🚀 Features

* 🔎 Semantic search over lecture transcripts
* ⏱ Timestamp-based source navigation
* 🧠 Dense vector retrieval using Sentence Transformers
* ⚡ Fast similarity search with FAISS
* 🎯 Cross-encoder reranking for improved answer precision
* 📝 AI-generated notes and flashcards
* 📊 Evaluation pipeline for:

  * Precision
  * Recall
  * Faithfulness
  * Answer relevance
* 🛡 Confidence badge for hallucination detection
* 🔄 Asynchronous background ingestion using Celery + Redis
* 💾 Transcript and chunk caching for faster responses
* 🌐 Chrome extension interface integrated directly into YouTube

---

# 🏗 Architecture Overview

## 1️⃣ Ingestion Pipeline

When a user interacts with a lecture video:

* Transcript is fetched automatically
* Transcript is semantically chunked
* Dense embeddings are generated
* Embeddings are stored in FAISS
* Metadata and processing status are tracked in MongoDB

Background ingestion is handled asynchronously using Celery workers and Redis queues.

---

## 2️⃣ Retrieval Pipeline

For every user query:

* Query embeddings are generated
* Relevant transcript chunks are retrieved from FAISS
* MMR filtering improves diversity
* Cross-encoder reranking improves relevance
* Context-aware answers are generated using the LLM pipeline

---

## 3️⃣ Fallback Retrieval System

To improve first-query responsiveness:

* A lightweight fallback pipeline answers questions immediately from transcript chunks
* Background ingestion continues asynchronously
* Once processing completes, the system automatically switches to full RAG retrieval

---

## 4️⃣ Chrome Extension Integration

The extension injects an AI assistant directly into YouTube and supports:

* Asking lecture-related questions
* Viewing timestamped sources
* Navigating to exact lecture moments
* Generating notes and flashcards
* Displaying confidence indicators

---

# 🛠 Tech Stack

## Backend

* FastAPI
* Celery
* Redis
* MongoDB

## Retrieval & NLP

* FAISS
* Sentence Transformers (`all-MiniLM-L6-v2`)
* Cross Encoder (`ms-marco-MiniLM`)
* Groq LLM API (`llama-3.1-8b-instant`)

## Frontend

* Chrome Extension
* JavaScript
* CSS

---

# 🎯 Current Focus

* Async scalable ingestion architecture
* Multi-video retrieval support
* Production-ready vector database migration
* Spaced repetition learning workflows
* Concept graph and learning gap detection

---

# 📌 Vision

LectureLens AI aims to become an intelligent learning companion for long-form educational content by combining semantic retrieval, contextual reasoning, and interactive learning workflows into a seamless YouTube experience.
