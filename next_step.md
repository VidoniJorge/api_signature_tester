## Buenas prácticas y notas
- Para expresiones JMESPath usadas frecuentemente, precompílalas con `jmespath.compile(expr)` y reutiliza el objeto.
- `deepdiff` puede devolver sets (`dictionary_item_added`/`removed`) — el validador los normaliza para el reporte.
- El proyecto no implementa aún validadores para HTML/XML; es una posible mejora.

## Siguientes pasos recomendados
- Añadir un CSV de ejemplo en `examples/` para documentar filas típicas.
- Crear una CLI simple (por ejemplo con `argparse` o `typer`) para pasar `csv`, `report_md`, `report_html`, `content_type` y `path_to_validate` desde la línea de comandos.
- Añadir más tests de integración (mocking de `requests`) para validar la lógica de comparación sin llamar a servicios reales.
