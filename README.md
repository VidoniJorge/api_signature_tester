# api_signature_tester
app to compare the response of two versions of the same endpoint

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

```bash
uv run src/main.py
```

## dependencies

### jmespath

[jmespath]( https://jmespath.org/ )


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

### pytest
Pytest es el estándar moderno en Python para pruebas unitarias.

[docu official](https://docs.pytest.org/en/stable/)

```bash
pytest
```

```bash
 pytest --cov=src --cov-report=html
 ```

 ```bash
 pytest -n auto --cov=src --cov-report=html -v
 ```

### snakeviz

Herramienta que nos ayuda a leer de forma más sencilla los profiles

[docu official](https://jiffyclub.github.io/snakeviz/)

**instalar**
```bash
uv add --dev snakeviz
```


**correr profile**
```bash
python -m cProfile -m main
```

o

```bash
python -m cProfile -o api_signature_tester.prof -m main
```


**leer profile con snakeviz**
```bash
snakeviz api_signature_tester.prof
```
