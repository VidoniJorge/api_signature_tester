from datetime import datetime

"""Generador de reportes en formato Markdown."""


class MarkdownReportGenerator:
    def generate(
        self, test_results: list, output_file: str = "reports/report.md"
    ) -> None:
        """
        Genera un reporte en formato Markdown con resultados colapsables.
        Args:
            test_results (List): Lista de resultados de las pruebas.
            output_file (str): Ruta del archivo de salida.
        Returns:
            None"""
        total = len(test_results)
        passed = sum(1 for r in test_results if r.get_comparation_result().is_equal())
        failed = total - passed
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md = [
            "# 🧾 Reporte de Comparaciones",
            f"**Fecha de ejecución:** {date}",
            f"**Total de pruebas:** {total}",
            f"✅ **Exitosas:** {passed}",
            f"❌ **Con diferencias:** {failed}",
            "\n---\n",
        ]

        # Crear cada bloque colapsable
        for idx, test in enumerate(test_results, 1):
            comp = test.get_comparation_result()
            source = test.get_source()
            new = test.get_new()

            is_equal = comp.is_equal()
            icon = "✅" if is_equal else "❌"
            color_class = "success" if is_equal else "fail"

            md.append(f"<details id='comparacion-{idx}' class='{color_class}'>")
            md.append(
                f"<summary><strong>🧩 Comparación #{idx} {icon}</strong></summary>\n"
            )

            md.append(f"**Source URL:** `{source.get_url()}`  ")
            md.append(f"**New URL:** `{new.get_url()}`  ")
            md.append(f"**Método:** `{source.get_method()}`  ")

            diff_status = comp.get_diff_status_code()
            if diff_status:
                md.append(f"**Status Code Diff:** `{diff_status}`  ")
            else:
                md.append("**Status Code Diff:** `Sin diferencias`  ")

            diff_body = comp.get_diff_body()
            if diff_body:
                md.append("\n**Diferencias en Body:**\n")
                md.append("| Tipo | Ruta | Valor Anterior | Valor Nuevo |")
                md.append("|--------|--------|----------------|--------------|")
                for diff in diff_body:
                    tipo = diff.get("Tipo", "")
                    path = diff.get("Ruta", "")
                    old = diff.get("Valor anterior", "")
                    newv = diff.get("Valor nuevo", "")
                    md.append(f"| {tipo} | {path} | {old} | {newv} |")
            else:
                md.append("\n**Diferencias en Body:** `Sin diferencias`\n")

            md.append("</details>\n")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
