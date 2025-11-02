# api_signature_tester
app to compare the response of two versions of the same endpoint


```bash
uv run src/main.py
```

## tools
Listado de tools que se utilizan en el proyecto

### ruff

Herramienta que nos ayuda a mantener el formato de nuestros archivos

[docu oficial](https://docs.astral.sh/ruff/)

```bash
ruff format ./src
```

```bash
ruff check
```

```bash
ruff check --fix
```

### mypy

Herramienta que nos ayuda a validar el typing de nustros archivos.

[docu oficial](https://mypy.readthedocs.io/en/stable/config_file.html)

```bash
mypy ./src
```

### pre-commit

Herramienta que nos ayuda a realizar validaciones de código de forma automática antes de que el commit quede efectivo, evitando de esta forma subir errores evitables a nuestra ramas.

[docu oficial](https://pre-commit.com/)
