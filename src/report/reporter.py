from typing import Protocol
from typing import List

'''
Interfaz para generadores de reportes.
'''
class ReportGenerator(Protocol):
    def generate(self, test_results: List, output_file: str) -> None:
        '''
        Args:
            test_results (List): Lista de resultados de las pruebas.
            output_file (str): Ruta del archivo de salida.
        Returns:
            None
        '''
        ...


