from parser.parser import Summary, SummaryRetrospective
from parser.xlswriter import XLSWriter

# # -- Парсинг конкретного года и семестра --
#
# from_ = 23  # год начала семестра (22, 23...);
# to_ = 24  # год конца семестра (23, 24...);
# semester = 1  # семестр (1/2).
#
# # Парсер
# summary = Summary(from_, to_, semester)
#
# print(f"Начинаем парсить...")
# # Занимает некоторое время. !!! Возможен отвал если сайт словит много запросов за раз, но я не проверял
# data = summary.parse_format_summary()
# print(f"Парсинг завершен!")
#
# writer = XLSWriter(data=data, metadata={"from": from_, "to": to_, "semester": semester})
#
# # Запись в xls-файл. Директория по умолчанию - dumps из этого репозитория
# print("Начинаем записывать дамп в Excel-файл...")
# writer.write()
# print("Запись завершена!")
#
#
# # -- Парсинг всех семестров с отрезка годов --
#
# from_ = 21  # год начала (21, 22...);
# to_ = 24  # год конца (23, 24...);
#
# # Парсер
# retrospective = SummaryRetrospective(from_, to_)
#
# print(f"Начинаем парсить период с {from_} по {to_}...")
#
# data = retrospective.parse_format_retrospective()
# print(f"Парсинг завершен!")
#
# writer = XLSWriter(data=data, metadata={"from": from_, "to": to_, "semester": "both"})
#
# print("Начинаем записывать дамп в Excel-файл...")
# writer.write()
# print("Запись завершена!")


# -- Парсинг всей информации --

from_ = 21  # год начала (21, 22...);
to_ = 24  # год конца (23, 24...);

# Парсеры
summary = Summary(23, 24, 1)
retrospective = SummaryRetrospective(from_, to_)

print(f"Начинаем парсить период и основные данные...")

data1 = summary.parse_format_all()
data2 = retrospective.parse_format_retrospective_all()
print(f"Парсинг завершен!")

writer1 = XLSWriter(data=data1, metadata={"from": 23, "to": 24, "semester": 1})
writer2 = XLSWriter(data=data2, metadata={"from": from_, "to": to_, "semester": "both"})

print("Начинаем записывать дамп в Excel-файл...")
writer1.write()
writer2.write()
print("Запись завершена!")
