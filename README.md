# 🪨 Rupestre AI

Sistema multiagente de análisis y documentación de **arte rupestre colombiano**, construido con LangGraph, FastAPI y ChromaDB.

---

## 📋 Tabla de contenidos

- [¿Qué hace este sistema?](#-qué-hace-este-sistema)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Requisitos previos](#-requisitos-previos)
- [Configuración inicial (primera vez)](#-configuración-inicial-primera-vez)
- [Cómo levantar el proyecto](#-cómo-levantar-el-proyecto)
- [Guía de uso de cada función](#-guía-de-uso-de-cada-función)
  - [1. Indexar el corpus de documentos en ChromaDB](#1-indexar-el-corpus-de-documentos-en-chromadb)
  - [2. Probar el pipeline completo desde la terminal](#2-probar-el-pipeline-completo-desde-la-terminal)
  - [3. Levantar la API REST (FastAPI)](#3-levantar-la-api-rest-fastapi)
  - [4. Analizar una imagen vía API](#4-analizar-una-imagen-vía-api)
  - [5. Consultar una ficha generada](#5-consultar-una-ficha-generada)
  - [6. Descargar el PDF de una ficha](#6-descargar-el-pdf-de-una-ficha)
- [Variables de entorno (.env)](#-variables-de-entorno-env)
- [Proveedores de LLM](#-proveedores-de-llm)
- [Pipeline de agentes](#-pipeline-de-agentes)
- [Carpeta data/ — dónde van los archivos](#-carpeta-data--dónde-van-los-archivos)
- [Tests](#-tests)

---

## 🤖 ¿Qué hace este sistema?

Rupestre AI toma una **foto de un sitio rupestre** (pictograma o petroglifo) y ejecuta un pipeline de 6 agentes que:

1. **Mejora la imagen** y verifica su calidad mínima
2. **Detecta motivos** presentes en la roca
3. **Busca paralelos iconográficos** en el corpus académico (ChromaDB)
4. **Genera una interpretación cultural** con nivel de confianza
5. **Reconstruye digitalmente** la imagen si aplica
6. **Produce una ficha ICANH** en formato PDF y JSON

---

## 📁 Estructura del proyecto

```
Rupestre-AI/
├── agents/               # Los 6 agentes autónomos del pipeline
│   ├── image_processor/  # AG1 – mejora y validación de imagen
│   ├── motif_detector/   # AG2 – detección de motivos rupestres
│   ├── iconographic_comparator/  # AG3 – búsqueda en corpus
│   ├── cultural_analyst/ # AG4 – interpretación cultural
│   ├── reconstructor/    # AG5 – reconstrucción digital
│   └── heritage_documenter/      # AG6 – ficha ICANH (PDF)
├── api/                  # Backend FastAPI
│   ├── main.py           # Punto de entrada de la API
│   └── routers/
│       └── analysis.py   # Endpoints /analyze, /records, /pdf
├── core/                 # Núcleo del sistema
│   ├── config.py         # Configuración centralizada (desde .env)
│   ├── graph.py          # Grafo LangGraph que orquesta los agentes
│   ├── state.py          # Estado compartido entre agentes
│   └── logger.py         # Logger unificado
├── corpus/               # Pipeline de ingesta del corpus académico
│   ├── ingest/           # Carga PDFs y otros formatos
│   ├── processing/       # Chunking y limpieza de texto
│   └── vectorstore/      # Indexación en ChromaDB
├── data/                 # Datos locales (NO se suben a Git)
│   ├── icanh_docs/       # ← Aquí colocas los PDFs del corpus
│   ├── chroma/           # Base vectorial generada automáticamente
│   ├── samples/          # Imágenes de prueba
│   └── fichas/           # Fichas PDF generadas por el pipeline
├── scripts/              # Herramientas de línea de comandos
│   ├── ingest_corpus.py  # Indexar documentos en ChromaDB
│   └── run_graph_test.py # Probar el pipeline completo
├── docker/               # Dockerfiles por servicio
├── .env                  # Variables de entorno (NO subir a Git)
├── .env.example          # Plantilla de variables (sí subir a Git)
└── requirements-dev.txt  # Dependencias de desarrollo
```

---

## ✅ Requisitos previos

- **Python 3.12+**
- **pip** actualizado
- *(Opcional)* [Ollama](https://ollama.com) si quieres usar un LLM local
- *(Opcional)* OpenAI API Key si usas `LLM_PROVIDER=openai`

---

## 🚀 Configuración inicial (primera vez)

### 1. Clona el repositorio y entra a la carpeta

```bash
git clone <url-del-repo>
cd Rupestre-AI
```

### 2. Crea el entorno virtual e instala dependencias

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activar en macOS/Linux
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements-dev.txt
```

### 3. Configura las variables de entorno

```bash
# Copia la plantilla
cp .env.example .env

# Edita .env con tus valores reales
# (ver sección "Variables de entorno" más abajo)
```

### 4. Ajusta el PYTHONPATH (necesario siempre que abras una terminal nueva)

```powershell
# Windows PowerShell
$env:PYTHONPATH = "C:\ruta\a\Rupestre-AI"

# macOS/Linux
export PYTHONPATH="/ruta/a/Rupestre-AI"
```

> 💡 **Tip:** Para no tener que repetir esto, agrega la línea anterior a tu perfil de PowerShell (`$PROFILE`) o al archivo `.env` de activación del venv.

---

## ▶️ Cómo levantar el proyecto

### Opción A — Solo la API REST (modo más común)

```powershell
# Desde la raíz del proyecto, con el venv activado:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

La API queda disponible en:
- **Swagger UI (documentación interactiva):** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **Health check:** http://localhost:8000/api/health

### Opción B — Prueba rápida del pipeline por terminal

```powershell
python scripts/run_graph_test.py
```

### Opción C — Pipeline completo desde cero

```powershell
# 1. Coloca los PDFs en data/icanh_docs/
# 2. Indexa el corpus
python scripts/ingest_corpus.py --source ./data/icanh_docs/

# 3. Levanta la API
uvicorn api.main:app --reload --port 8000
```

---

## 📖 Guía de uso de cada función

### 1. Indexar el corpus de documentos en ChromaDB

**Cuándo usarlo:** Antes de la primera ejecución del sistema, y cada vez que agregues nuevos documentos académicos.

**Pasos:**
1. Coloca los PDFs de publicaciones, tesis o informes en la carpeta `data/icanh_docs/`
2. Ejecuta el script de ingesta:

```powershell
python scripts/ingest_corpus.py --source ./data/icanh_docs/
```

**Opciones disponibles:**

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--source` | `data/icanh_docs/rupestre` | Carpeta raíz con los PDFs a indexar |
| `--collection` | `corpus_rupestre` | Nombre de la colección en ChromaDB |

**Ejemplo con opciones personalizadas:**
```powershell
python scripts/ingest_corpus.py --source ./data/icanh_docs/ --collection mi_coleccion
```

**Qué hace internamente:**
```
PDFs en data/icanh_docs/
    → corpus/ingest/pdf_loader.py   (carga y extrae texto)
    → corpus/processing/chunker.py  (divide en fragmentos)
    → corpus/vectorstore/indexer.py (genera embeddings y guarda en ChromaDB)
    → data/chroma/                  (base vectorial persistida en disco)
```

---

### 2. Probar el pipeline completo desde la terminal

**Cuándo usarlo:** Para verificar que todos los agentes funcionan correctamente sin necesidad de levantar la API.

```powershell
# Con imagen de prueba generada automáticamente
python scripts/run_graph_test.py

# Con una imagen real
python scripts/run_graph_test.py --image ./data/samples/mi_pictograma.jpg
```

**Opciones disponibles:**

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--image` | `data/samples/pictograma.jpg` | Ruta a la imagen de entrada |

Si la imagen no existe, el script crea automáticamente una imagen de prueba genérica.

**Salida esperada:**
```
✅ Pipeline completado en 2.3s
   AG1: imagen realzada ✓
   AG2: 5 motivos detectados ✓
   AG3: paralelos encontrados ✓
   AG4: interpretación generada ✓
   AG5: reconstrucción omitida (sin GAN) ✓
   AG6: ficha ICANH generada ✓
       Record ID: abc-123
       PDF: ./data/fichas/abc-123_ficha_icanh.pdf ✓
```

---

### 3. Levantar la API REST (FastAPI)

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

| Flag | Descripción |
|------|-------------|
| `--reload` | Recarga automática al guardar cambios (solo desarrollo) |
| `--host 0.0.0.0` | Acepta conexiones desde cualquier IP de la red local |
| `--port 8000` | Puerto donde escucha la API |

Una vez levantada, abre http://localhost:8000/api/docs para ver todos los endpoints con su documentación interactiva.

---

### 4. Analizar una imagen vía API

**Endpoint:** `POST /api/analyze`

**Desde la terminal con curl:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "image=@./data/samples/pictograma.jpg" \
  -F "site_name=Chiribiquete" \
  -F "latitude=0.9167" \
  -F "longitude=-72.8500"
```

**Desde Python:**
```python
import requests

with open("./data/samples/pictograma.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"image": f},
        data={
            "site_name": "Chiribiquete",
            "latitude": 0.9167,
            "longitude": -72.8500,
        },
    )

print(response.json())
```

**Respuesta:**
```json
{
  "record_id": "abc-123-uuid",
  "motif_count": 5,
  "cultural_interpretation": "Representación zoomorfa asociada...",
  "interpretation_confidence": 0.82,
  "reconstruction_applied": false,
  "pdf_available": true,
  "requires_human_review": false,
  "processing_time_seconds": 3.14
}
```

> ⚠️ Si `requires_human_review: true`, la confianza de interpretación fue menor a `HITL_CONFIDENCE_THRESHOLD` (0.6 por defecto). El registro existe pero necesita revisión manual.

---

### 5. Consultar una ficha generada

**Endpoint:** `GET /api/records/{record_id}`

```bash
curl http://localhost:8000/api/records/abc-123-uuid
```

Devuelve el JSON completo de la ficha ICANH con todos los datos del análisis.

---

### 6. Descargar el PDF de una ficha

**Endpoint:** `GET /api/records/{record_id}/pdf`

```bash
curl -O http://localhost:8000/api/records/abc-123-uuid/pdf
```

O simplemente abre la URL en el navegador para descargar el PDF directamente.

Los PDFs también se guardan localmente en `data/fichas/`.

---

## 🔧 Variables de entorno (.env)

Copia `.env.example` como `.env` y ajusta los valores:

```env
# ── Proveedor de LLM ──────────────────────────────────────────
# Opciones: mock | ollama | openai
# "mock" no necesita API key, ideal para desarrollo y tests
LLM_PROVIDER=mock

# ── OpenAI (solo si LLM_PROVIDER=openai) ─────────────────────
OPENAI_API_KEY=sk-...

# ── Ollama local (solo si LLM_PROVIDER=ollama) ────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.3

# ── ChromaDB ──────────────────────────────────────────────────
CHROMADB_PATH=./data/chroma
CHROMADB_COLLECTION=corpus_rupestre

# ── Directorios de salida ─────────────────────────────────────
OUTPUT_DIR=./data/fichas
SAMPLES_DIR=./data/samples

# ── Control de calidad de imagen ──────────────────────────────
MIN_IMAGE_RESOLUTION=1000000   # mínimo 1 megapíxel
BLUR_THRESHOLD=100.0           # varianza de Laplaciano mínima

# ── Human-in-the-Loop ─────────────────────────────────────────
HITL_CONFIDENCE_THRESHOLD=0.6  # debajo de esto pide revisión humana

# ── Langfuse (observabilidad) — opcional ──────────────────────
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## 🧠 Proveedores de LLM

| `LLM_PROVIDER` | Requiere | Costo | Ideal para |
|----------------|----------|-------|-----------|
| `mock` | Nada | Gratis | Desarrollo y tests rápidos |
| `ollama` | Ollama instalado + modelo descargado | Gratis (local) | Desarrollo sin internet |
| `openai` | `OPENAI_API_KEY` válida | De pago | Producción |

**Para usar Ollama:**
```bash
# Instalar Ollama desde https://ollama.com
ollama pull llama3.3   # descarga el modelo (~4GB)
ollama serve           # inicia el servidor en localhost:11434
```

---

## 🔄 Pipeline de agentes

El grafo LangGraph ejecuta los agentes en esta secuencia:

```
[Imagen + Metadatos]
        │
        ▼
   AG1 image_processor   → mejora imagen, valida calidad
        │ (si calidad OK)
        ▼
   AG2 motif_detector    → detecta motivos rupestres
        │
        ▼
   AG3 iconographic_comparator → busca paralelos en ChromaDB
        │
        ▼
   AG4 cultural_analyst  → genera interpretación cultural
        │ (si confianza >= umbral)
        ▼
   AG5 reconstructor     → reconstrucción digital (opcional)
        │
        ▼
   AG6 heritage_documenter → genera ficha ICANH (PDF + JSON)
        │
        ▼
   [Ficha lista en data/fichas/]
```

---

## 📂 Carpeta `data/` — dónde van los archivos

| Carpeta | Qué va ahí | Se sube a Git |
|---------|-----------|---------------|
| `data/icanh_docs/` | PDFs del corpus académico (publicaciones ICANH, tesis UPTC, informes) | ❌ No |
| `data/chroma/` | Base vectorial ChromaDB (se genera con `ingest_corpus.py`) | ❌ No |
| `data/samples/` | Imágenes de prueba de sitios rupestres (<5MB) | ✅ Sí |
| `data/fichas/` | PDFs de fichas generados por el pipeline | ❌ No |

> Para agregar nuevos documentos al corpus:
> 1. Copia los PDFs a `data/icanh_docs/`
> 2. Ejecuta `python scripts/ingest_corpus.py --source ./data/icanh_docs/`

---

## 🧪 Tests

```powershell
# Ejecutar todos los tests
pytest

# Con salida detallada
pytest -v

# Solo un módulo específico
pytest tests/test_image_processor.py -v
```

La configuración de pytest está en `pytest.ini`.

---

> **Nota:** El archivo `.env` **nunca** debe subirse a Git. Está incluido en `.gitignore`. Si accidentalmente subiste una API key, revócala inmediatamente en el panel del proveedor.
