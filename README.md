# Парсер итогов по преподователям из https://shedule.uni-dmitrov.ru

## Использование

### Для конкретного года и семестра

```python
# -- Парсинг конкретного года и семестра --
from parser.parser import Summary

from_ = 23  # год начала семестра (22, 23...)
to_ = 24  # год конца семестра (23, 24...)
# from_ = 21; to_ = 24 - выдаст ошибку
semester = 1  # семестр (1/2)

# Парсер
summary = Summary(from_, to_, semester)

# Полученные данные
data = summary.parse_summary()

print(data)
```

### Для периода с одного года по другой (Оба семестра)

```python
# -- Парсинг периода --
from parser.parser import SummaryRetrospective

from_ = 17  # год начала (17, 18...)
to_ = 24  # год конца (23, 24...)

# Парсер
retrospective = SummaryRetrospective(from_, to_)

# Полученные данные
data = retrospective.parse_retrospective()

print(data)
```

### Экспорт в .xls

```python
# -- Экспорт данных --
from parser.parser import Summary, SummaryRetrospective
from parser.xlswriter import XLSWriter

# Парсинг с 23 по 24 год за первый семестр
summary = Summary(23, 24, 1)
data1 = summary.parse_format_summary()

# Запись в файл данных с 23 по 24 год за первый семестр
writer1 = XLSWriter(data=data1,
                    metadata={"from": 23,
                              "to": 24,
                              "semester": 1})
writer1.write()

# Парсинг с 17 по 24 год за оба семестра
retrospective = SummaryRetrospective(17, 24)
data2 = retrospective.parse_format_retrospective()

# Запись в файл данных с 17 по 24 год за оба семестра
writer2 = XLSWriter(data=data2,
                    metadata={"from": 17,
                              "to": 24,
                              "semester": "both"})
writer2.write()
```

## Requirements

> - Python 3.10+
>   - beautifulsoup4
>   - openpyxl
>   - requests
