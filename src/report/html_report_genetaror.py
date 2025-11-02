from datetime import datetime

"""Generador de reportes en formato HTML."""


class HTMLReportGenerator:
    def generate(
        self, test_results: list, output_file: str = "reports/report.html"
    ) -> None:
        """
        Genera un reporte en formato HTML con resultados colapsables y filtrables.
        Args:
            test_results (List): Lista de resultados de las pruebas.
            output_file (str): Ruta del archivo de salida.
        Returns:
            None
        """

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = len(test_results)
        passed = sum(1 for tr in test_results if tr.get_comparation_result().is_equal())
        failed = total - passed

        html = [
            """
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <title>Reporte de Comparaciones</title>
    <style>
        body {
            font-family: "Inter", "Segoe UI", sans-serif;
            background-color: #fafafa;
            color: #333;
            margin: 40px auto;
            max-width: 950px;
            line-height: 1.6;
        }
        h1, h2 {
            color: #222;
            text-align: center;
        }
        summary {
            cursor: pointer;
            font-weight: 600;
            padding: 10px 14px;
            background: #f0f0f0;
            border-radius: 8px;
            transition: background 0.2s ease;
        }
        summary:hover {
            background: #e4e4e4;
        }
        details {
            margin: 15px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fff;
            padding: 12px 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 0.95em;
        }
        th, td {
            border: 1px solid #e0e0e0;
            padding: 8px 10px;
            text-align: left;
        }
        th {
            background-color: #f8f8f8;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #fcfcfc;
        }
        pre {
            background: #f8f8f8;
            border-left: 3px solid #ccc;
            padding: 8px;
            overflow-x: auto;
            border-radius: 5px;
        }
        .success { color: #2e7d32; font-weight: bold; }
        .fail { color: #c62828; font-weight: bold; }
        .info {
            text-align: center;
            font-size: 0.9em;
            color: #666;
            margin-bottom: 1em;
        }
        ul {
            list-style-type: none;
            padding: 0;
            text-align: center;
        }
        ul li {
            display: inline-block;
            margin: 0 8px;
        }
        ul li a {
            text-decoration: none;
            color: #1565c0;
        }
        ul li a:hover {
            text-decoration: underline;
        }
        #filter-bar {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
        }
        #filter-bar button {
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s ease, transform 0.1s ease;
        }
        #filter-bar button:hover {
            transform: scale(1.05);
        }
        #btn-all { background: #e0e0e0; }
        #btn-passed { background: #c8e6c9; }
        #btn-failed { background: #ffcdd2; }
    </style>
    </head>
    <body>
    """
        ]

        html.append("<h1>Reporte de Comparaciones</h1>")
        html.append(f"<p class='info'>Fecha de ejecución: {now}</p>")
        html.append(
            f"<p class='info'>Total de casos: {total} | ✅ {passed} exitosos " + 
            f"| ❌ {failed} con diferencias</p>"
        )

        # Barra de filtro
        html.append("""
        <div id="filter-bar">
            <button id="btn-all">🔁 Ver Todos</button>
            <button id="btn-passed">✅ Solo Éxitos</button>
            <button id="btn-failed">❌ Solo Errores</button>
        </div>
        """)

        # Casos
        for i, test_result in enumerate(test_results, start=1):
            comp_result = test_result.get_comparation_result()
            source = test_result.get_source()
            new = test_result.get_new()
            are_equal = comp_result.is_equal()
            diff_status = comp_result.get_diff_status_code()
            diff_body = comp_result.get_diff_body()

            status_class = "success" if are_equal else "fail"
            symbol = "✅" if are_equal else "❌"

            html.append(
                f"<details class='case {status_class}' id='caso{i}'>" +
                f"<summary>{symbol} Caso {i}</summary>"
            )
            html.append("<div>")
            html.append(f"<p><strong>Source URL:</strong> {source.url}</p>")
            html.append(f"<p><strong>New URL:</strong> {new.url}</p>")
            html.append(f"<p><strong>Método:</strong> {source.method}</p>")

            # Status Code
            if diff_status:
                html.append("<p><strong>Diferencias en Status Code:</strong></p>")
                html.append(f"<pre>{diff_status}</pre>")
            else:
                html.append(
                    "<p><strong>Diferencias en Status Code:" +
                    "</strong> Sin diferencias</p>"
                )

            # Body
            if diff_body:
                html.append("<p><strong>Diferencias en Body:</strong></p>")
                html.append(
                    "<table><tr><th>Tipo</th><th>Ruta</th>"+
                    "<th>Valor Anterior</th><th>Valor Nuevo</th></tr>"
                )
                for diff in diff_body:
                    tipo = diff.get("Tipo", "")
                    path = diff.get("Ruta", "")
                    old = diff.get("Valor anterior", "")
                    newv = diff.get("Valor nuevo", "")
                    html.append(
                        f"<tr><td>{tipo}</td><td>{path}</td><td>{old}</td><td>{newv}</td></tr>"
                    )
                html.append("</table>")
            else:
                html.append(
                    "<p><strong>Diferencias en Body:</strong> Sin diferencias</p>"
                )

            html.append("</div></details>")

        # Script JS
        html.append("""
    <script>
    document.getElementById('btn-all').addEventListener('click', () => {
        document.querySelectorAll('.case').forEach(el => el.style.display = '');
    });
    document.getElementById('btn-passed').addEventListener('click', () => {
        document.querySelectorAll('.case').forEach(el => {
            el.style.display = el.classList.contains('success') ? '' : 'none';
        });
    });
    document.getElementById('btn-failed').addEventListener('click', () => {
        document.querySelectorAll('.case').forEach(el => {
            el.style.display = el.classList.contains('fail') ? '' : 'none';
        });
    });
    </script>
    """)

        html.append("</body></html>")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(html))
