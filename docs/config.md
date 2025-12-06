# Configuración del proyecto

Este documento describe el módulo `config` del proyecto `api_signature_tester`, cómo funciona, y cómo se puede configurar el comportamiento de la aplicación.

## Archivos de configuración
En el directorio raíz del proyecto hay una carpeta `config/` que contiene los archivos JSON que definen la configuración por defecto y por ambiente:

- `config/base.json` — Configuración base con valores por defecto.
- `config/dev.json` — Sobreescribe o añade valores para el ambiente `dev`.
- `config/test.json` — Sobreescribe o añade valores para el ambiente `test`.
- `config/prod.json` — Sobreescribe o añade valores para el ambiente `prod`.

> Si un archivo por ambiente no existe o está vacío, la configuración final queda con los valores de `base.json`.

## Cómo carga la configuración

El módulo `src/api_signature_tester/config.py` implementa la lógica de carga de configuración. Puntos clave:

- La función `load_config()` lee primero `base.json` y luego el archivo del ambiente (`dev.json`/`test.json`/`prod.json`) y los mezcla (override) para formar la configuración final.
- El ambiente se obtiene de la variable de entorno `APP_ENV`. Si no está definida, el valor por defecto es `dev`.
- `load_config()` usa `functools.lru_cache` para que la configuración sólo se lea/parse una vez por proceso. Si cambias `APP_ENV` en tiempo de ejecución en tests o en tu proceso, deberás limpiar la caché con `load_config.cache_clear()`.
- El directorio de configuración es `config/` (resuelto a partir del `BASE_DIR` que apunta al root del proyecto).

Código principal (resumen):

```python
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"

@lru_cache
def load_config() -> dict:
    env = os.getenv("APP_ENV", "dev").lower()
    base_config = _load_json(CONFIG_DIR / "base.json")
    env_config = _load_json(CONFIG_DIR / f"{env}.json")
    merged = {**base_config, **env_config}
    return merged
```

## API pública del módulo

El módulo expose:

- `load_config()` — retorna un `dict` con la configuración cargada y mergeada (cacheada por proceso).
- `Settings` — clase singleton que simplifica el acceso a la configuración en toda la app.

La clase `Settings` ofrece los métodos:
- `get_properties(key)` — devuelve el valor asociado a `key` (o `None` si no existe).
- `get_environment()` — devuelve el valor de `environment` del config.
- `get_log_level()` — devuelve `log_level`.

Ejemplo de uso:

```python
from api_signature_tester.config import Settings
settings = Settings()  # Singleton
csv_path = settings.get_properties("csv_path")
log_level = settings.get_log_level()
```

## Valores por defecto (ejemplo)

El archivo `config/base.json` contiene valores por defecto, por ejemplo:

```json
{
  "log_level": "ERROR",
  "csv_path": "src/api_signature_tester/request.csv",
  "report_md_path": "reports/comparisons_report.md",
  "report_html_path": "reports/comparisons_report.html",
  "environment": "dev"
}
```

Esto significa que si no defines `APP_ENV`, se usará `dev` (según la lógica en `load_config`), y se aplicarán las opciones de `base.json` más los overrides del `dev.json`.

## Cómo cambiar el ambiente o modificar la configuración

1. Cambiar el ambiente mediante variable de entorno:

```bash
export APP_ENV=prod
python -m api_signature_tester.main
```

2. Modificar valores por ambiente:

- Edita `config/dev.json`, `config/prod.json` o `config/test.json` para agregar o sobreescribir claves.
- Por ejemplo, para cambiar el log level en `prod.json`:

```json
{
  "log_level": "INFO",
  "environment": "prod"
}
```

3. Pasar rutas por run-time (CLI/kwargs):

El `main` de la aplicación permite pasar rutas para los archivos (CSV y reportes). La implementación prefiere la configuración cargada por `Settings` y solo usa el argumento `kwargs` si la propiedad de configuración es `None`.

```python
csv_path_default = settings.get_properties("csv_path")
csv_path = csv_path_default if csv_path_default is not None else kwargs.get('input_csv_path')
```

> Nota: la aplicación busca usar las propiedades definidas en la configuración del proyecto por defecto; si quieres forzar otra ruta, puedes modificar `base.json` o hacer que `csv_path` sea `null` en la config y pasar `input_csv_path` al ejecutar `run()`.

## Consideraciones para tests

- `load_config()` está cacheada con `lru_cache`. Si en tests necesitas cambiar el valor de `APP_ENV`, debes borrar la caché antes de cargar la configuración:

```python
from api_signature_tester import config
monkeypatch.setenv("APP_ENV", "test")
config.load_config.cache_clear()
settings = config.Settings()
```

- Alternativamente, puedes usar `monkeypatch.setenv` y recargar el módulo con `importlib.reload`.

## Resumen rápido

- `config.load_config()` carga `base.json` y aplica `env.json` según `APP_ENV`.
- `Settings()` ofrece acceso sencillo a la configuración desde el resto del código.
- Para tests, recuerda limpiar la caché si cambias `APP_ENV`.
- Modifica `*.json` en la carpeta `config/` para agregar o cambiar configuraciones por ambiente.

---

Si quieres, puedo añadir esta sección al `README.md` del proyecto (o a `docs/README.md`) y crear un pequeño ejemplo de cómo cambiar `APP_ENV` y ejecutar `main.py` con config personalizada. ¿Deseas que también lo añada al README principal?
