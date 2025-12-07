# api_signature_tester — Documentación

Proyecto para comparar las respuestas de dos versiones del mismo endpoint HTTP y generar reportes legibles en Markdown y HTML.

**Resumen**
- Compara `status_code` y `body` de respuestas HTTP entre dos entornos/versions.
- Soporta comparación completa de JSON y comparación parcial usando expresiones JMESPath.
- Carga casos de prueba desde CSV y genera reportes en `reports/`.

**Características principales**
- Validadores: `PipelineFullJsonApiValidator` (compara todo el JSON) y `PipelineJsonApiParcialValidator` (aplica expresión `jmespath` antes de comparar).
- Comparación profunda de JSON mediante `deepdiff`.
- Generadores de reporte: Markdown (`MarkdownReportGenerator`) y HTML (`HTMLReportGenerator`).
- ETL sencillo para CSV (`LoaderCsv`).

**Requisitos**
- Python >= 3.13 (según `pyproject.toml`).
- Dependencias principales: `deepdiff`, `jmespath`, `requests`.
- Ver `pyproject.toml` y `requirement.txt` para versiones.

## Instalación rápida

Se recomienda usar las dependencias y la configuración declaradas en `pyproject.toml` (este proyecto usa `hatchling` como backend).

1. Crear y activar un virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Actualizar `pip` y herramientas de build:

```bash
python -m pip install --upgrade pip build hatchling
```

3. Instalar el paquete y las dependencias desde `pyproject.toml` (modo editable recomendado durante desarrollo):

```bash
pip install -e .
```

4. (Opcional) Instalar dependencias de desarrollo si están disponibles como extras:

```bash
pip install -e .[dev]
```

Nota: el `pyproject.toml` en este repo define `dependency-groups` para el grupo `dev`. Algunas versiones de `pip` no mapean automáticamente esos grupos a extras; si `pip install -e .[dev]` falla, instala las dependencias de desarrollo manualmente según la sección `[dependency-groups]` del `pyproject.toml` o utiliza `hatch` para gestionar entornos de desarrollo.

5. (Opcional) Si no instalaste el paquete en modo editable, añade `src` al `PYTHONPATH` para ejecutar los módulos directamente:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

## Estructura relevante
- `src/api_signature_tester/`
  - `main.py` — entrada principal, definición de pipeline y logger.
  - `config.py` — carga configuración desde `config/*.json` según `APP_ENV`.
  - `etl/etl_csv.py` — Loader CSV para convertir filas en `EndpointData`.
  - `validator/` — lógica de comparación y modelos (ver `pipeline_api_validaror.py`, `pipeline_json_api.py`, `validator_model.py`).
  - `report/` — generadores Markdown y HTML.
- `tests/` — tests del proyecto.
- `config/` — archivos JSON por ambiente (`base.json`, `dev.json`, `test.json`, `prod.json`).

## Formato CSV esperado
El loader (`LoaderCsv`) espera un CSV con encabezado (se salta la primera fila) y por cada fila estas columnas en orden:

0. `source_url`
1. `source_method` (get/post/head/options)
2. `source_params` (ej: `a=1&b=2`) — cadena vacía si no hay
3. `source_headers` (ej: `Auth=token&Accept=application/json`) — cadena vacía si no hay
4. `new_url`
5. `new_method`
6. `new_params`
7. `new_headers`

Ejemplo (una fila):

```
https://api.example.com/v1/item,GET,,Accept=application/json,https://staging.api.example.com/v1/item,GET,,Accept=application/json
```

El loader transforma `a=1&b=2` en `{ "a": "1", "b": "2" }` y análogamente para headers.

## Flujo de ejecución
1. `ApiSignatureTesterSynchBase` (en `pipeline/sync_process.py`) carga los casos desde el CSV mediante `LoaderCsv`.
2. Por cada caso, el `PipelineApiValidaror.execute` realiza una request a la `source` y a la `new` usando `requests`.
3. Se comparan `status_code` y `body`:
   - Si alguno de los bodies no es JSON, se añade un diff de formato.
   - Si ambos son JSON, `PipelineFullJsonApiValidator` usa `deepdiff` (con `ignore_order=True`) para obtener diferencias y las normaliza para el reporte.
   - `PipelineJsonApiParcialValidator` aplica primero la expresión `jmespath` para extraer sólo la porción a comparar.
4. Se generan `report.md` y `report.html` en las rutas indicadas en la configuración.

## Uso básico
Desde la raíz del repo, con el entorno virtual activo y dependencias instaladas:

```bash
python -m api_signature_tester.main
```

O (si no instalaste editable):

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python src/api_signature_tester/main.py
```

La selección del validador se realiza en `main.py` mediante `definePipelineValidator(settings, content_type, path_to_validate)`.

- Para comparar todo el JSON: `PipelineFullJsonApiValidator()`.
- Para comparar una porción: `PipelineJsonApiParcialValidator(path_to_validate)` donde `path_to_validate` es una expresión JMESPath.

## JMESPath — uso y ejemplos
`jmespath` permite consultar estructuras JSON en Python de forma declarativa.

Import básico:
```py
import jmespath
result = jmespath.search('a.b', {'a': {'b': 1}})  # -> 1
```

Ejemplos útiles:
- `items[*].id` → lista con todos los `id` dentro de `items`.
- `items[?price > `10`].name` → nombres de items con `price > 10`.
- `sort_by(items, &price)[*].name` → nombres ordenados por `price`.

En este proyecto `PipelineJsonApiParcialValidator` recibe `path_to_validate` y hace `jmespath.search(path_to_validate, json)` sobre ambas respuestas antes de comparar.

## Tests
Ejecuta todos los tests con:

```bash
pytest
```

Generar reporte de cobertura HTML:

```bash
pytest --cov=src --cov-report=html
```

## Configuración
`src/api_signature_tester/config.py` carga `config/base.json` y luego sobrescribe con `config/{env}.json` según la variable `APP_ENV` (por defecto `dev`). Las keys importantes en los JSON de configuración son:
- `csv_path` — ruta al CSV de entrada.
- `report_md_path` — ruta de salida para el reporte Markdown.
- `report_html_path` — ruta de salida para el reporte HTML.
