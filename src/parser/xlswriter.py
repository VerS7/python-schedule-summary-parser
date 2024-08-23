"""
Excel .xls writer
"""
from os import path
from datetime import datetime

from openpyxl import Workbook

DEFAULT_DUMP_DIR = path.join(path.dirname(path.dirname(path.dirname(__file__))), "dumps")


class XLSWriter:
    def __init__(self, data, metadata: dict = None, file_name: str = None, dump_directory: str = DEFAULT_DUMP_DIR):
        self.dump_dir = dump_directory
        self._wb = Workbook()
        self._ws = self._wb.active

        self.data = data

        if file_name is None:
            self.file_name = f"DUMP_{datetime.today().strftime('%d_%m_%y_%H-%M-%S')}.xls"
        else:
            self.file_name = file_name

        if metadata:
            self._ws.title = (f"20{metadata.get('from', '00')} - 20{metadata.get('to', '00')} | "
                              f"{metadata.get('semester', 'N/A')}")

        self.full_path = path.join(self.dump_dir, self.file_name)

    def write(self):
        """Записывает данные из data в файл"""
        for i in range(len(self.data)):
            for j, key in enumerate(self.data[0].keys()):
                value = self.data[i][key] if not isinstance(self.data[i][key], list) else ", ".join(self.data[i][key])
                self._ws.cell(row=i + 1, column=j + 1, value=value)
        self._wb.save(self.full_path)
