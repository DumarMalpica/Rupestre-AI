# 🪨 Rupestre AI

<div align="center">

### Sistema de IA para la Reconstrucción de Pictogramas y Figuras Rupestres
### en la Zona Andina de Colombia

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![LangFuse](https://img.shields.io/badge/LangFuse-Trazas-FF6B35?style=for-the-badge&logo=grafana&logoColor=white)

**Plataforma de inteligencia artificial para la documentación, análisis y reconstrucción digital
del patrimonio rupestre precolombino del altiplano andino colombiano**

[📡 Ver API en vivo](#) · [📖 Documentación Swagger](#) · [🗺️ Mapa de Sitios](#) · [📋 Fichas ICANH](#)

</div>

---

## 📌 Descripción

**Rupestre AI** es una plataforma de inteligencia artificial de cuatro capas tecnológicas diseñada para transformar la forma en que arqueólogos, investigadores y gestores culturales documentan, analizan y reconstruyen el arte rupestre de la zona andina colombiana — departamentos de **Boyacá, Cundinamarca, Huila, Nariño y Santander**.

El sistema aborda el deterioro acelerado de miles de petroglifos y pictogramas de culturas **muisca, herrera y otras tradiciones precolombinas** (3.000–10.000 años de antigüedad) que enfrentan erosión, biocolonización por líquenes, vandalismo y expansión agropecuaria a un ritmo que supera la capacidad de registro convencional.

Desarrollado en coordinación con el **ICANH** y el grupo de investigación en arqueología de la **UPTC**, con sitios piloto en Villa de Leyva, Facatativá (Piedras del Tunjo), Sogamoso, Gámeza y San Agustín.

---

## ✨ Características

- 🎨 **Reconstrucción GAN** — DeepFillv2 con gated convolution y contextual attention para restaurar zonas deterioradas de pictogramas
- 🧠 **RAG Arqueológico** — LLM con recuperación aumentada sobre corpus ICANH + UPTC para interpretación cultural sin alucinaciones
- 🤖 **6 Agentes Autónomos** — Red orquestada con LangGraph: procesamiento, detección, comparación, interpretación, reconstrucción y documentación
- 📱 **Bot de Campo** — Telegram bot para arqueólogos: foto de entrada → ficha ICANH en PDF en menos de 45 minutos
- 🗺️ **Plataforma Web Pública** — Mapa interactivo de sitios rupestres andinos con galerías de reconstrucciones digitales
- 🔍 **Observabilidad Total** — Trazas de ejecución de agentes y RAG con LangFuse
- 🏛️ **Ficha ICANH Automatizada** — Generación autónoma del formato oficial en PDF y JSON estructurado
- 🔬 **Realce Multiespectral** — Pipeline DStretch + RTI para revelar pigmentos invisibles al ojo humano

---

## 🏗️ Arquitectura

```
Foto de campo (arqueólogo vía Telegram / Web)
                    │
                    ▼
         ┌─────────────────────┐
         │   FastAPI Backend   │  ← API central unificada
         └─────────┬───────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │      LangGraph Classifier    │  ← Orquestador central
    │   (Grafo de estados + HITL)  │
    └──────────────────────────────┘
          │    │    │    │    │    │
          ▼    ▼    ▼    ▼    ▼    ▼
    ┌─────┐ ┌────┐ ┌────┐ ┌────┐ ┌─────┐ ┌─────┐
    │ AG1 │ │AG2 │ │AG3 │ │AG4 │ │ AG5 │ │ AG6 │
    │Proc.│ │Det.│ │Comp│ │Cult│ │Rec. │ │Doc. │
    └─────┘ └────┘ └────┘ └────┘ └─────┘ └─────┘
       │                    │        │
    OpenCV               RAG +    DeepFill
    DStretch             LLM       v2 GAN
                      ChromaDB
                          │
                    ┌─────────────┐
                    │  LangFuse   │  ← Trazabilidad completa
                    └─────────────┘
```

### Las Cuatro Capas

| Capa | Tecnología Central | Responsabilidad |
|------|--------------------|-----------------|
| **1 — GANs** | PyTorch + DeepFillv2 | Reconstrucción generativa de pictogramas deteriorados |
| **2 — LLM + RAG** | LangChain + ChromaDB + Ollama | Interpretación arqueológica basada en corpus local |
| **3 — Agentes** | LangGraph + CrewAI | Orquestación autónoma del pipeline de análisis |
| **4 — Bot / Web** | FastAPI + Next.js + Telegram | Interfaz de campo y plataforma pública patrimonial |

---

## 🤖 Red de Agentes

| # | Agente | Responsabilidad | Tools | Dev |
|---|--------|-----------------|-------|-----|
| AG1 | **Image Processor** | Realce multiespectral y estandarización | OpenCV, DStretch, RTI | Dev 1 |
| AG2 | **Motif Detector** | Detección y segmentación de motivos | YOLOv11, SAM2 | Dev 1 |
| AG3 | **Iconographic Comparator** | Búsqueda de paralelos en inventario regional | ChromaDB, FAISS | Dev 2 |
| AG4 | **Cultural Analyst** | Interpretación arqueológica con RAG | LangChain, LLM, RAG | Dev 2 |
| AG5 | **Reconstructor** | Reconstrucción GAN de zonas dañadas | DeepFillv2, LaMa | Dev 1 |
| AG6 | **Heritage Documenter** | Generación de ficha ICANH en PDF/JSON | Jinja2, WeasyPrint | Dev 2 |

---

## 📊 Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| Reconstrucciones validadas por expertos | ≥ 80% |
| Precisión detección de motivos (IoU) | > 82% |
| FID score reconstrucciones GAN | < 45 |
| Tasa de éxito autónomo de agentes | > 83% |
| Satisfacción de investigadores (1–5) | > 4.1 |
| Tiempo de generación de ficha por sitio | < 45 min |

---

## 🗂️ Estructura del Proyecto

```
rupestre-ai/
├── core/                        # Núcleo compartido — contrato entre agentes
│   ├── state.py                 # Estado LangGraph compartido
│   ├── graph.py                 # Grafo clasificador central
│   ├── config.py                # Configuración global + LangFuse
│   └── logger.py                # Trazas LangFuse
├── agents/
│   ├── image_processor/         # AG1 — Procesamiento de imagen
│   ├── motif_detector/          # AG2 — Detección de motivos
│   ├── iconographic_comparator/ # AG3 — Comparación iconográfica
│   ├── cultural_analyst/        # AG4 — Análisis cultural RAG
│   ├── reconstructor/           # AG5 — Reconstrucción GAN
│   └── heritage_documenter/     # AG6 — Documentación ICANH
├── corpus/                      # Ingesta y vectorización del corpus
├── models/                      # Pesos GAN y configs de modelos
├── api/                         # FastAPI backend unificado
├── bot/                         # Telegram bot de campo
├── infrastructure/              # Redis, PostgreSQL, MinIO
└── tests/                       # Tests de integración del grafo
```

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.12+
- Docker + Docker Compose v2
- GPU NVIDIA con 8 GB VRAM mínimo (RTX 3070 / A4000)
- CUDA 12.x

### 1. Clonar el repositorio

```bash
git clone https://github.com/uptc-sistemas/rupestre-ai.git
cd rupestre-ai
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

```env
# LangFuse — Observabilidad
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# LLM
OPENAI_API_KEY=sk-...           # Opcional: para producción
OLLAMA_BASE_URL=http://localhost:11434  # Para desarrollo local

# Base de datos
POSTGRES_URL=postgresql://user:pass@localhost:5432/rupestre
CHROMA_PATH=./data/chroma

# Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Telegram Bot
TELEGRAM_BOT_TOKEN=...
```

### 3. Levantar servicios con Docker

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 4. Instalar dependencias Python

```bash
pip install uv
uv pip install -r requirements.txt
```

### 5. Descargar modelos

```bash
# LLM local (Llama 3.3 para desarrollo)
ollama pull llama3.3

# Pesos preentrenados DeepFillv2
bash scripts/setup_env.sh
```

### 6. Ingestar corpus inicial

```bash
python scripts/ingest_corpus.py --source ./data/icanh_docs/
```

### 7. Probar el grafo completo

```bash
python scripts/run_graph_test.py --image samples/pictograma_villa_leyva.jpg
```

### 8. Levantar la API

```bash
uvicorn api.main:app --reload --port 8000
# Swagger UI disponible en http://localhost:8000/api/docs
```

---

## 🧪 Pruebas

### Ejecutar todos los tests

```bash
pytest tests/ -v
```

### Probar un agente de forma independiente

```bash
# Cada agente tiene sus propios tests sin depender del grafo completo
pytest agents/image_processor/tests/ -v
pytest agents/cultural_analyst/tests/ -v
pytest agents/motif_detector/tests/ -v
```

### Test de integración del grafo

```bash
pytest tests/test_graph_integration.py -v
```

---

## 🔍 Observabilidad con LangFuse

Cada ejecución del grafo genera una traza completa visible en el dashboard de LangFuse:

```
Traza: analisis_rupestre — Villa de Leyva
│
├── image_processor          ✅  1.2s   — imagen realzada con DStretch
├── motif_detector           ✅  3.4s   — 4 motivos detectados (IoU: 0.87)
├── iconographic_comparator  ✅  0.8s   — 3 paralelos encontrados en inventario
├── cultural_analyst         ✅  12.1s
│   ├── rag_retrieval        ✅  0.6s   — 5 fragmentos ICANH recuperados
│   └── llm_generation       ✅  11.5s  — 850 tokens — fuentes citadas: 3
├── reconstructor            ✅  8.3s   — zona reconstructed (confianza: 0.91)
└── heritage_documenter      ✅  2.1s   — ficha_villa_leyva_001.pdf generada
```

---

## 🗺️ Sitios Piloto

| Sitio | Departamento | Coordenadas | Estado |
|-------|-------------|-------------|--------|
| Villa de Leyva | Boyacá | 5.634°N, 73.525°W | 🟡 En proceso |
| Facatativá — Piedras del Tunjo | Cundinamarca | 4.815°N, 74.355°W | 🟡 En proceso |
| Sogamoso | Boyacá | 5.715°N, 72.931°W | 🔴 Pendiente |
| Gámeza | Boyacá | 5.890°N, 72.786°W | 🔴 Pendiente |
| San Agustín | Huila | 1.887°N, 76.274°W | 🔴 Pendiente |

---

## 🛠️ Stack Tecnológico

### Capa 1 — Reconstrucción GAN
![PyTorch](https://img.shields.io/badge/PyTorch-2.2-EE4C2C?style=flat&logo=pytorch)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-5C3EE8?style=flat&logo=opencv)
![CUDA](https://img.shields.io/badge/CUDA-12.x-76B900?style=flat&logo=nvidia)

### Capa 2 — LLM + RAG
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=flat)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Latest-FF6B35?style=flat)
![Ollama](https://img.shields.io/badge/Ollama-Llama3.3-000000?style=flat)

### Capa 3 — Agentes
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C?style=flat)
![CrewAI](https://img.shields.io/badge/CrewAI-0.80-FF4B4B?style=flat)
![YOLOv11](https://img.shields.io/badge/YOLOv11-Ultralytics-00FFFF?style=flat)

### Capa 4 — Interfaz
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)
![NextJS](https://img.shields.io/badge/Next.js-15-000000?style=flat&logo=nextdotjs)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat&logo=telegram)

---

## 👥 Equipo de Desarrollo

| Desarrollador | Agentes | Módulos |
|---------------|---------|---------|
| **Dev 1** | AG1 Image Processor · AG2 Motif Detector · AG5 Reconstructor | `agents/image_processor` · `agents/motif_detector` · `agents/reconstructor` · `models/` |
| **Dev 2** | AG3 Iconographic Comparator · AG4 Cultural Analyst · AG6 Heritage Documenter | `agents/iconographic_comparator` · `agents/cultural_analyst` · `agents/heritage_documenter` · `corpus/` · `bot/` |
| **Compartido** | Clasificador LangGraph · API · Infraestructura | `core/` · `api/` · `infrastructure/` · `tests/` |

---

## 🤝 Flujo de Trabajo Git

```bash
# Cada desarrollador trabaja en su rama de agente
git checkout -b feature/ag1-image-processor
git checkout -b feature/ag4-cultural-analyst

# PR hacia develop cuando el agente pasa sus tests independientes
# Merge a main solo cuando el grafo de integración completo pasa
```

### Ramas

| Rama | Propósito |
|------|-----------|
| `main` | Producción estable |
| `develop` | Integración continua |
| `feature/ag{N}-{nombre}` | Desarrollo de cada agente |
| `hotfix/*` | Correcciones urgentes en producción |

---

## 📄 Licencia

Proyecto académico desarrollado en la **Universidad Pedagógica y Tecnológica de Colombia (UPTC)** — Ingeniería de Sistemas y Computación, 2026.

En coordinación con el **Instituto Colombiano de Antropología e Historia (ICANH)**.

---

<div align="center">

**UPTC · Ingeniería de Sistemas y Computación · 2026**

*Preservando el patrimonio rupestre andino con inteligencia artificial*

</div>
