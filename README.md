# api_signature_tester

Librería para comparar respuestas HTTP entre dos versiones de un mismo endpoint. Proporciona componentes para cargar casos desde CSV, ejecutar solicitudes a ambos endpoints, comparar códigos de estado y cuerpos JSON (con soporte de JMESPath para validación parcial) y generar reportes en Markdown y HTML. Diseñada para integrarse como dependencia en proyectos y usarse programáticamente.

## Características principales

- Carga de casos desde CSV con `LoaderCsv` (parseo de params y headers).
- Validación completa de JSON con `deepdiff` y validación parcial con `jmespath`.
- Comparación de códigos de estado y detección de diferencias en body (valores, claves añadidas/eliminadas, elementos añadidos/removidos).
- Generación de reportes en Markdown y HTML (archivos configurables).

## Dependencias

Las dependencias necesarias para ejecutar la librería son:

- `deepdiff` >= 8.6.1 — comparación profunda de estructuras JSON.
- `jmespath` >= 1.0.1 — consultas sobre estructuras JSON.
- `requests` >= 2.32.5 — para realizar solicitudes HTTP.


## Instalación desde Test PyPI

Por ahora la librería está publicada en el índice de pruebas de PyPI. Para instalarla desde allí:

```bash
pip install -i https://test.pypi.org/simple/ api-signature-tester
```

Si más adelante la publicás en PyPI oficial, se podrá instalar simplemente con `pip install api-signature-tester`.
