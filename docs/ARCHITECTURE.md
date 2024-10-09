Here's how the source code is currently organized :

*Note: only the most important directories and sub-directories are listed.*

```
.
├── matcha-------------------------- Matcha is a Django app, this directory contains settings and root urls
├── api ---------------------------- API Endpoints
├── cache -------------------------- Can be used by a file-based cache backend
├── conf --------------------------- (obsolescent) This directory stores configuration for nginx and supervisor
├── contrib ------------------------ Is the place that will holder contributions
│   └── castoretpollux ------------- Yes, we also do some contributions to our own project
│       ├── stablediffusion -------- (obsolete)
│       └── whisper ---------------- (obsolete)
├── core --------------------------- One of the most important directory : it contains core Django models
│   ├── locale --------------------- i18n and l10n
│   ├── migrations ----------------- Django models migration. Must be appplied
├── docs --------------------------- The current doc folder
│   ├── images --------------------- doc images
│   └── tutorials ------------------ tutorials
├── frontend ----------------------- Vue3 Matcha frontend
├── lib ---------------------------- Various helpers 
│   ├── locale --------------------- i18n and l10n
├── locale ------------------------- i18n and l10n
├── log ---------------------------- Matcha logs (it uses Django and Python loggers)
│   └── mails ---------------------- File based log emails
├── machinery ---------------------- Most important directory : the machinery behind Matcha
│   ├── bridges -------------------- Bridges between Matcha and external AI Providers or sass solutions
│   ├── common --------------------- Currently, contains common pydantic schema
│   ├── factories ------------------ Factories are Pipeline class factories
│   │   ├── ollama ----------------- A generic pipeline factory that uses ollama as backend
│   │   ├── replicate -------------- A generic pipeline factory that uses replicate as backend
│   │   ├── search ----------------- To search documents and pages that are indexed in a vector database
│   │   └── translation ------------ Translation factory
│   ├── locale --------------------- i18n and l10n
│   ├── mixins --------------------- useful mixins for pipelines and factories
│   ├── pipelines ------------------ contains all pipelines (see [TERMINOLOGY](/docs/TERMINOLOGY))
│   │   ├── demo ------------------- a simple pipeline example that is only useful to show how pipeline can be created
│   │   ├── featureextractor ------- extract features from documents and pages
│   │   ├── img2txt ---------------- convert images to text
│   │   ├── speech2txt ------------- convert speech to text
│   │   └── stablediffusionxl ------ (obsolescent) generate image from text, using stablediffusionxl
│   └── templates ------------------ used by pipeline renderers
├── media -------------------------- contains uploaded files
├── processes ---------------------- contains helper processes that are not currently integrated in the core
│   ├── searchapp ------------------ searchapp indexes documents and make them searchable
│   │   ├── api -------------------- api endpoints
│   │   ├── core ------------------- searchapp core directory, it contains document and document-related models 
│   │   │   ├── management --------- contains commands
│   │   │   │   └── commands ------- commands allows you to upload documents in a CLI
│   │   │   ├── migrations --------- searchapp models migrations, they must be applied
│   │   │   │   ├── datasets ------- for data migrations
│   │   ├── lib -------------------- helper modules
│   │   ├── locale ----------------- i18n and l10n
│   │   ├── media ------------------ contains uploaded documents
│   │   └── searchapp -------------- searchapp is a Django app, this directory contains settings and root urls
│   ├── stablediffusionapp --------- (obsolescent) external process for Stable Diffusion
│   └── suggestionapp -------------- (obsolete) external process to suggest pipelines that are relevant, given the input
├── requirements ------------------- classical Python requirement files (must be installed using pip)
├── scripts ------------------------ various scripts
│   ├── crawl_to_json -------------- crawl web site page and store them as json (must be fixed)
│   └── import_folder -------------- import json crawl results into searchapp
├── static ------------------------- Matcha static assets
│   └── img ------------------------ Matcha static image assets
├── tmp ---------------------------- To store temporary files...
└── wsock -------------------------- To store websockets related files

```