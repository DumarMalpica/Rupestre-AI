# Rupestre AI

Sistema multiagente de análisis y documentación de **arte rupestre colombiano**, construido con LangGraph, FastAPI y ChromaDB — desarrollado en la UPTC.

---

## Tabla de contenidos

- [¿Qué hace?](#qué-hace)
- [Arquitectura del pipeline](#arquitectura-del-pipeline)
- [Estado actual del sistema](#estado-actual-del-sistema)
- [Requisitos previos](#requisitos-previos)
- [Configuración inicial (primera vez)](#configuración-inicial-primera-vez)
- [Variables de entorno](#variables-de-entorno)
- [Cómo ejecutar](#cómo-ejecutar)
  - [1. Indexar el corpus en ChromaDB](#1-indexar-el-corpus-en-chromadb)
  - [2. Prueba del pipeline por terminal](#2-prueba-del-pipeline-por-terminal)
  - [3. API REST (FastAPI)](#3-api-rest-fastapi)
  - [4. Analizar una imagen vía API](#4-analizar-una-imagen-vía-api)
  - [5. Consultar ficha y descargar PDF](#5-consultar-ficha-y-descargar-pdf)
- [Tests](#tests)
- [CI/CD](#cicd)
- [Observabilidad con LangFuse](#observabilidad-con-langfuse)
- [Proveedores de LLM](#proveedores-de-llm)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Carpeta data/](#carpeta-data)

---

## ¿Qué hace?

Rupestre AI recibe una **foto de un sitio con arte rupestre** (pictogramas o petroglifos) y ejecuta un pipeline de 6 agentes que:

1. Valida la calidad de la imagen y la realza con DStretch-LAB (OpenCV)
2. Detecta motivos rupestres presentes (YOLOv11 — mock hasta que el modelo esté entrenado)
3. Busca paralelos iconográficos en el corpus académico indexado en ChromaDB
4. Genera una interpretación cultural con nivel de confianza (LLM configurable)
5. Reconstruye digitalmente zonas deterioradas (DeepFillv2 — mock hasta que el modelo esté entrenado)
6. Produce una ficha ICANH en formato **PDF y JSON** lista para registro oficial

---

## Arquitectura del pipeline

```
[Imagen JPG/PNG + nombre del sitio + coordenadas]
          │
          ▼
   AG1 image_processor       valida resolución ≥ 1 MP, blur < umbral
          │ calidad OK?
          ├─── NO ──→ [FIN — imagen rechazada, sin registro]
          │
          ▼
   AG2 motif_detector         YOLOv11 + SAM2 (mock) → detección y segmentación
          │
          ▼
   AG3 iconographic_comparator  ChromaDB + embeddings multilingual-e5
          │
          ▼
   AG4 cultural_analyst         LLM (mock/ollama/openai) + RAG sobre corpus
          │ confianza ≥ 0.6?
          ├─── NO ──→ [FIN — requiere revisión humana, sin PDF]
          │
          ▼
   AG5 reconstructor            DeepFillv2 (mock) → inpainting zonas deterioradas
          │
          ▼
   AG6 heritage_documenter      ficha ICANH → PDF (ReportLab) + JSON
          │
          ▼
   [data/fichas/{RECORD_ID}_ficha_icanh.pdf]
```

---

## Estado actual del sistema

| Componente | Estado | Notas |
|---|---|---|
| AG1 — image_processor | **Funcional** | DStretch-LAB real con OpenCV |
| AG2 — motif_detector | **Mock** | Retorna 2 motivos fijos; YOLOv11 requiere entrenamiento |
| AG3 — iconographic_comparator | **Funcional** | ChromaDB real; fallback a mock si corpus vacío |
| AG4 — cultural_analyst | **Funcional** | `mock` / `ollama` / `openai` configurable en `.env` |
| AG5 — reconstructor | **Mock** | Máscara de deterioro real; inpainting DeepFillv2 pendiente |
| AG6 — heritage_documenter | **Funcional** | PDF real con ReportLab |
| API REST | **Funcional** | FastAPI con Swagger UI |
| Observabilidad | **Funcional** | LangFuse v4 con `@observe` por agente |

---

## Requisitos previos

- **Python 3.11 o 3.12** (recomendado 3.12)
- **pip** actualizado (`pip install --upgrade pip`)
- *(Opcional)* [Ollama](https://ollama.com) para usar un LLM local sin API key
- *(Opcional)* OpenAI API key para `LLM_PROVIDER=openai`
- *(Opcional)* Cuenta en [cloud.langfuse.com](https://cloud.langfuse.com) para observabilidad

---

## Configuración inicial (primera vez)

### 1. Clonar y entrar a la carpeta

```powershell
git clone <url-del-repo>
cd Rupestre-AI
```

### 2. Crear entorno virtual e instalar dependencias

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar en Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activar en macOS / Linux
source .venv/bin/activate

# Instalar todas las dependencias
pip install -r requirements-dev.txt
```

> No existe un `requirements.txt` separado — `requirements-dev.txt` contiene tanto
> las dependencias de runtime como las de desarrollo y test.

### 3. Configurar variables de entorno

```powershell
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Edita `.env` con tus valores reales (ver sección [Variables de entorno](#variables-de-entorno)).

### 4. Configurar PYTHONPATH (necesario en cada terminal nueva)

El proyecto usa imports absolutos (`from core.config import settings`). Python necesita
saber dónde está la raíz del proyecto:

```powershell
# Windows PowerShell — ejecutar desde la raíz del proyecto
$env:PYTHONPATH = (Get-Location).Path
```

```bash
# macOS / Linux
export PYTHONPATH=$(pwd)
```

> **Para no repetirlo:** agrega la línea a tu perfil de PowerShell (`$PROFILE`) o
> crea un script `activate_project.ps1` en la raíz que active el venv y establezca
> el PYTHONPATH en un solo paso.

---

## Variables de entorno

Todas las variables se configuran en `.env` (copia de `.env.example`):

```env
# ── Proveedor LLM ────────────────────────────────────────────────────────────
# Opciones: mock | ollama | openai
# "mock" funciona sin API key (ideal para desarrollo y tests)
LLM_PROVIDER=mock

# ── OpenAI (solo si LLM_PROVIDER=openai) ────────────────────────────────────
OPENAI_API_KEY=sk-...

# ── Ollama local (solo si LLM_PROVIDER=ollama) ───────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.3

# ── ChromaDB (vector store del corpus) ──────────────────────────────────────
CHROMADB_PATH=./data/chroma
CHROMADB_COLLECTION=corpus_rupestre

# ── Directorios de salida ────────────────────────────────────────────────────
OUTPUT_DIR=./data/fichas
SAMPLES_DIR=./data/samples

# ── Control de calidad de imagen ─────────────────────────────────────────────
MIN_IMAGE_RESOLUTION=1000000   # píxeles mínimos (1 MP)
BLUR_THRESHOLD=100.0            # varianza Laplaciano mínima

# ── Human-in-the-Loop ────────────────────────────────────────────────────────
HITL_CONFIDENCE_THRESHOLD=0.6  # por debajo de esto → revisión humana requerida

# ── LangFuse (observabilidad) — dejar vacío para desactivar ──────────────────
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
# Nota: LANGFUSE_BASE_URL también funciona como alias de LANGFUSE_HOST
```

---

## Cómo ejecutar

### 1. Indexar el corpus en ChromaDB

Ejecutar **una vez** antes del primer análisis, y cada vez que agregues nuevos PDFs al corpus.

**Pasos:**
1. Copia los PDFs académicos a `data/icanh_docs/rupestre/`
2. Ejecuta el script de ingesta:

```powershell
python scripts/ingest_corpus.py
```

**Opciones:**

| Opción | Default | Descripción |
|---|---|---|
| `--source` | `data/icanh_docs/rupestre` | Carpeta raíz con los PDFs |
| `--collection` | `corpus_rupestre` | Nombre de la colección en ChromaDB |

```powershell
# Con ruta y colección personalizadas
python scripts/ingest_corpus.py --source ./data/icanh_docs/ --collection mi_coleccion
```

**Salida esperada:**
```
✅ londono_2003_sutatausa.pdf: 47 chunks indexados
✅ arte_rupestre_boyaca.pdf: 83 chunks indexados

📚 Total: 130 chunks en colección 'corpus_rupestre'
```

> El script omite automáticamente el archivo `el archivo y las voces del silencio (2992.pdf)`.
> El modelo de embeddings (`paraphrase-multilingual-MiniLM-L12-v2`) se descarga
> automáticamente la primera vez (~420 MB, se cachea en `~/.cache/huggingface/`).

---

### 2. Prueba del pipeline por terminal

Ejecuta el pipeline completo de AG1→AG6 **sin levantar la API**. Ideal para verificar
que todos los agentes funcionan y para ver las trazas en LangFuse.

```powershell
# Usa imagen existente (o la crea si no existe)
python scripts/run_graph_test.py

# Con una imagen real
python scripts/run_graph_test.py --image data/samples/mi_pictograma.jpg
```

**Opciones:**

| Opción | Default | Descripción |
|---|---|---|
| `--image` | `data/samples/pictograma.jpg` | Ruta a la imagen de entrada |

Si la imagen no existe, el script genera automáticamente una imagen sólida 1200×800 px como placeholder.

**Salida esperada:**
```
Session ID: 8a8a9ca7-2a17-4ee8-bab5-5945431e2cee  (búscalo en LangFuse → Traces)
✅ Pipeline completado en 4.2s
   AG1: imagen realzada ✓
   AG2: 2 motivos detectados ✓
   AG3: paralelos encontrados ✓
   AG4: interpretación generada ✓
   AG5: reconstrucción omitida (sin GAN) ✓
   AG6: ficha ICANH generada ✓
       Record ID: A3F1B2C4
       PDF: ./data/fichas/A3F1B2C4_ficha_icanh.pdf ✓
📡 Trazas enviadas a LangFuse ✓
```

---

### 3. API REST (FastAPI)

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

| Flag | Descripción |
|---|---|
| `--reload` | Recarga automática al guardar cambios (solo desarrollo) |
| `--host 0.0.0.0` | Accesible desde otras máquinas de la red local |
| `--port 8000` | Puerto de escucha |

**URLs disponibles una vez levantada:**

| URL | Descripción |
|---|---|
| http://localhost:8000/api/docs | Swagger UI — interfaz interactiva |
| http://localhost:8000/api/redoc | ReDoc — documentación alternativa |
| http://localhost:8000/api/health | Health check (`{"status": "ok"}`) |

---

### 4. Analizar una imagen vía API

**Endpoint:** `POST /api/analyze`

**Con curl:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "image=@data/samples/pictograma.jpg" \
  -F "site_name=Chiribiquete" \
  -F "latitude=0.9167" \
  -F "longitude=-72.8500"
```

**Con Python:**
```python
import requests

with open("data/samples/pictograma.jpg", "rb") as f:
    r = requests.post(
        "http://localhost:8000/api/analyze",
        files={"image": ("pictograma.jpg", f, "image/jpeg")},
        data={"site_name": "Chiribiquete", "latitude": 0.9167, "longitude": -72.85},
    )

print(r.json())
```

**Respuesta exitosa (`200 OK`):**
```json
{
  "record_id": "A3F1B2C4",
  "motif_count": 2,
  "cultural_interpretation": "Los motivos en espiral presentan características...",
  "interpretation_confidence": 0.82,
  "reconstruction_applied": false,
  "pdf_available": true,
  "requires_human_review": false,
  "processing_time_seconds": 3.14
}
```

**Posibles respuestas de error:**

| Código | Causa |
|---|---|
| `422` | Imagen rechazada por calidad (resolución < 1 MP o muy borrosa) |
| `422` | Campos del formulario faltantes o inválidos |

> Si `requires_human_review: true`, la confianza de interpretación quedó por debajo
> del umbral (`HITL_CONFIDENCE_THRESHOLD=0.6`). El análisis está incompleto y
> requiere revisión manual antes de generar la ficha final.

---

### 5. Consultar ficha y descargar PDF

**Obtener ficha completa en JSON:**
```bash
curl http://localhost:8000/api/records/A3F1B2C4
```

**Descargar PDF:**
```bash
# Guarda como A3F1B2C4_ficha_icanh.pdf en el directorio actual
curl -O http://localhost:8000/api/records/A3F1B2C4/pdf
```

Los PDFs también quedan persistidos localmente en `data/fichas/` y no dependen de que la API esté corriendo para abrirlos.

---

## Tests

```powershell
# Ejecutar todos los tests (agentes + API)
pytest

# Con salida detallada
pytest -v

# Solo los tests de un agente específico
pytest agents/image_processor/tests/ -v

# Solo los tests de la API
pytest tests/test_api.py -v

# Con reporte de cobertura
pytest --cov=agents --cov-report=term-missing
```

**Dónde están los tests:**

| Archivo | Qué cubre |
|---|---|
| `agents/image_processor/tests/test_agent.py` | Calidad de imagen, realce, casos borde |
| `agents/motif_detector/tests/test_agent.py` | Detección de motivos, campos requeridos |
| `agents/iconographic_comparator/tests/test_agent.py` | Comparación iconográfica, scores |
| `agents/cultural_analyst/tests/test_agent.py` | Interpretación LLM, modo mock sin HTTP |
| `agents/reconstructor/tests/test_agent.py` | Máscara de deterioro, inpainting |
| `agents/heritage_documenter/tests/test_agent.py` | Ficha JSON, generación PDF (mockeado) |
| `tests/test_api.py` | Endpoints FastAPI con graph mockeado |

La configuración de pytest está en `pytest.ini` (testpaths, asyncio_mode, etc.).

---

## CI/CD

El pipeline de integración continua está en `.github/workflows/ci.yml` y se ejecuta
en cada `push` y `pull request` a `main`.

**Jobs:**

```
lint (ubuntu, Python 3.12)
  ├── ruff check .
  ├── black --check .
  └── mypy core/ agents/ api/

test-agents  (needs: lint)
  └── pytest agents/ --cov=agents --cov-fail-under=60

test-core  (needs: lint)
  └── pytest tests/ -k "not integration"
```

Para pasar el linter localmente antes de hacer push:

```powershell
# Verificar estilo
ruff check .
black --check .

# Corregir automáticamente lo que se pueda
ruff check . --fix
black .
```

---

## Observabilidad con LangFuse

Cada agente envía trazas a [cloud.langfuse.com](https://cloud.langfuse.com) cuando las
credenciales están configuradas en `.env`. Sin credenciales, el sistema funciona igual
pero sin trazas (degradación silenciosa).

**Configurar:**
1. Crear cuenta gratuita en [cloud.langfuse.com](https://cloud.langfuse.com)
2. Ir a **Settings → API Keys → Create new key pair**
3. Agregar al `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

> Si tu `.env` usa `LANGFUSE_BASE_URL` en lugar de `LANGFUSE_HOST`, el sistema lo
> detecta y lo mapea automáticamente. Ambos nombres funcionan.

**Lo que aparece en LangFuse por cada ejecución del pipeline:**

| Traza | Spans internos |
|---|---|
| `ag1_image_processor` | `quality_check`, `enhance_image` |
| `ag2_motif_detector` | `yolo_detection`, `sam_segmentation`, `annotation` |
| `ag3_iconographic_comparator` | `chroma_retrieve` |
| `ag4_cultural_analyst` | `build_prompt`, `llm_generation` (con usage tokens) |
| `ag5_reconstructor` | `mask_generation`, `inpainting` |
| `ag6_heritage_documenter` | `build_json`, `render_html`, `generate_pdf` |

Todas las trazas de un mismo análisis comparten el mismo `session_id`, visible en
**Traces → filter by session** para ver el pipeline completo de un vistazo.

---

## Proveedores de LLM

| `LLM_PROVIDER` | Requiere | Costo | Cuándo usar |
|---|---|---|---|
| `mock` | Nada | Gratis | Desarrollo, tests, CI |
| `ollama` | Ollama instalado + modelo descargado | Gratis (local) | Desarrollo sin internet |
| `openai` | `OPENAI_API_KEY` válida | De pago | Producción o demos |

**Para usar Ollama:**
```bash
# 1. Instalar desde https://ollama.com
# 2. Descargar el modelo (~4 GB):
ollama pull llama3.3

# 3. Iniciar el servidor (queda corriendo en background):
ollama serve

# 4. En .env:
#    LLM_PROVIDER=ollama
#    OLLAMA_BASE_URL=http://localhost:11434
#    OLLAMA_MODEL=llama3.3
```

---

## Estructura del proyecto

```
Rupestre-AI/
├── agents/                          # Los 6 agentes del pipeline
│   ├── image_processor/             # AG1: calidad + DStretch-LAB
│   │   ├── tools/quality.py         # check_quality()
│   │   ├── tools/enhancer.py        # enhance_image()
│   │   ├── tools/corrector.py       # correct_perspective() [TODO]
│   │   ├── agent.py
│   │   └── tests/test_agent.py
│   ├── motif_detector/              # AG2: YOLOv11 + SAM2 [mock]
│   ├── iconographic_comparator/     # AG3: ChromaDB + embeddings
│   ├── cultural_analyst/            # AG4: RAG + LLM configurable
│   ├── reconstructor/               # AG5: DeepFillv2 [mock]
│   └── heritage_documenter/         # AG6: ficha ICANH PDF/JSON
│       └── templates/ficha_icanh.html
│
├── api/                             # Backend REST
│   ├── main.py                      # FastAPI app + lifespan + CORS
│   ├── routers/analysis.py          # POST /analyze, GET /records, GET /health
│   └── schemas/                     # request.py, response.py
│
├── core/                            # Núcleo compartido
│   ├── config.py                    # Settings (pydantic-settings, lee .env)
│   ├── graph.py                     # StateGraph LangGraph (AG1→AG6)
│   ├── logger.py                    # get_logger() + @observe + langfuse_context
│   ├── state.py                     # RupestreState TypedDict
│   └── exceptions.py                # ImageQualityError, AgentExecutionError…
│
├── corpus/                          # Pipeline de ingesta del corpus
│   ├── ingest/pdf_loader.py         # load_pdf() con PyMuPDF
│   ├── processing/chunker.py        # chunk_documents() sliding-window
│   └── vectorstore/
│       ├── chroma_client.py         # get_collection() + embedding model
│       └── indexer.py               # index_documents() por batches de 50
│
├── scripts/
│   ├── ingest_corpus.py             # CLI: indexa PDFs en ChromaDB
│   └── run_graph_test.py            # CLI: prueba AG1→AG6 sin la API
│
├── tests/
│   └── test_api.py                  # Tests de los endpoints FastAPI
│
├── data/                            # Datos locales (ignorados por Git)
│   ├── icanh_docs/rupestre/         # PDFs del corpus académico
│   ├── chroma/                      # Base vectorial ChromaDB
│   ├── samples/                     # Imágenes de prueba
│   └── fichas/                      # Fichas PDF generadas
│
├── .env                             # Variables de entorno (NO subir a Git)
├── .env.example                     # Plantilla (sí subir a Git)
├── .gitignore                       # Excluye .env, imágenes, PDFs, pesos ML
├── pytest.ini                       # Configuración de tests
├── pyproject.toml                   # ruff, black, mypy
└── requirements-dev.txt             # Todas las dependencias (runtime + dev)
```

---

## Carpeta `data/`

| Subcarpeta | Contenido | Git |
|---|---|---|
| `data/icanh_docs/rupestre/` | PDFs académicos del corpus (publicaciones ICANH, tesis UPTC, informes arqueológicos) | No |
| `data/chroma/` | Base vectorial ChromaDB generada por `ingest_corpus.py` | No |
| `data/samples/` | Imágenes JPG/PNG de sitios rupestres para pruebas | No |
| `data/fichas/` | Fichas PDF y JSON generadas por el pipeline | No |
| `models/yolov11/` | Pesos del modelo YOLOv11 entrenado (pendiente) | No |
| `models/deepfillv2/` | Pesos del modelo DeepFillv2 (pendiente) | No |

Los directorios vacíos se preservan en Git con archivos `.gitkeep`.

---

> El archivo `.env` **nunca** debe subirse a Git (está en `.gitignore`).
> Si accidentalmente subes una API key, revócala inmediatamente en el panel
> del proveedor correspondiente.
