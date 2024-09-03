"""
Парсер итогов по преподам из https://shedule.uni-dmitrov.ru/
"""
from typing import List, Dict, Any

from requests import Session, Response, HTTPError
from bs4 import BeautifulSoup, Tag

URL_TEMPLATE = "https://shedule.uni-dmitrov.ru/20{FROM}{TO}_{SEMESTER}"


def format_data(parsed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Форматирует данные с итогов или ретроспективы в единый список для экспорта"""
    result = []

    for elem in parsed:
        if isinstance(elem["data"], list):
            for fragment in elem["data"]:
                result.append({**fragment, "отрезок": int(f"{elem['from']}{elem['to']}"), "семестр": elem["semester"]})
        else:
            result.append({**elem["data"], "отрезок": int(f"{elem['from']}{elem['to']}"), "семестр": elem["semester"]})
    return result


def _decode(text: str) -> str:
    return text.encode('latin1').decode('cp1251')


class Summary:
    def __init__(self, from_: int, to_: int, semester: int, session: Session = Session()):
        self.from_ = from_
        self.to_ = to_
        self.semester = semester
        self._url = self._generate_url()

        self._session = session

    def parse_all_teachers(self) -> List[Dict[str, str]]:
        """Парсит ФИО преподавателей и URL на итоги"""
        response = self._get_response(self._url + "/vp.htm")
        soup = BeautifulSoup(response.text, "html.parser")
        teachers = []

        for row in soup.find("table", {"class": "inf"}).find_all("a"):
            teachers.append({"ФИО": _decode(row.get_text()), "URL": self._url + f"/{row.attrs['href']}"})

        return teachers

    def parse_summary(self) -> List[Dict[str, Any]]:
        """Парсит основную информацию по всем преподам"""
        teachers = self.parse_all_teachers()
        summary = []

        for teacher in teachers:
            t_data = self._parse_total(self._get_response(teacher["URL"]))

            groups = list(set([d["Группа"] for d in t_data]))
            disciples = list(set([d["Дисциплина"] for d in t_data]))

            summary.append({"from": self.from_,
                            "to": self.to_,
                            "semester": self.semester,
                            "data": {"ФИО": teacher["ФИО"],
                                     "Группы": groups,
                                     "Кол-во групп": len(groups),
                                     "Дисциплины": disciples,
                                     "Кол-во дисциплин": len(disciples),
                                     "Сумм. часов": sum([d["Всего, ч"] for d in t_data])}})

        return summary

    def parse_all(self) -> List[Dict[str, Any]]:
        """Парсит всю информацию по всем преподам"""
        teachers = self.parse_all_teachers()
        total = []

        for teacher in teachers:
            total.append({"from": self.from_,
                          "to": self.to_,
                          "semester": self.semester,
                          "data": self._parse_total(self._get_response(teacher["URL"]))
                          })
        return total

    def parse_format_summary(self) -> List[Dict[str, Any]]:
        """Форматирует основные данные с итогов в единый список для экспорта"""
        return format_data(self.parse_summary())

    def parse_format_all(self) -> List[Dict[str, Any]]:
        """Форматирует все данные с итогов в единый список для экспорта"""
        return format_data(self.parse_all())

    def _get_response(self, url: str) -> Response:
        response = self._session.post(url)

        if response.status_code == 404:
            raise HTTPError(f"Ничего не найдено по URL {url}")
        if response.status_code != 200:
            raise HTTPError(f"Произошла непредвиденная ошибка. URL: {url}")

        return response

    def _parse_new_table(self, data: List[Tag]) -> Dict[str, Any]:
        return {"ФИО": _decode(data[1].get_text()),
                "Группа": _decode(data[2].get_text()),
                "П/г": int(data[3].get_text()),
                "Дисциплина": _decode(data[4].get_text()),
                "Тип": _decode(data[5].get_text()),
                "Всего, ч": int(data[6].get_text()),
                "План, ч": int(data[7].get_text()),
                "Факт, ч": int(data[8].get_text()),
                "Остаток, ч": float(data[9].get_text().replace(",", ".")),
                "План 2н, ч": float(data[10].get_text().replace(",", ".")),
                "Факт 2н, ч": int(data[11].get_text()),
                "Окончание": data[12].get_text()}

    def _parse_old_table(self, data: List[Tag]) -> Dict[str, Any]:
        return {"ФИО": _decode(data[1].get_text()),
                "Группа": _decode(data[2].get_text()),
                "П/г": int(data[3].get_text()),
                "Дисциплина": _decode(data[4].get_text()),
                "Тип": "",
                "Всего, ч": int(data[5].get_text()),
                "План, ч": int(data[6].get_text()),
                "Факт, ч": int(data[7].get_text()),
                "Остаток, ч": float(data[8].get_text().replace(",", ".")),
                "План 2н, ч": float(data[9].get_text().replace(",", ".")),
                "Факт 2н, ч": int(data[10].get_text()),
                "Окончание": data[11].get_text()}

    def _parse_total(self, response: Response) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(response.text, "html.parser")
        total = []

        if len(soup.find("table", {"class": "inf"}).find_all("td", {"class": "hd"})) == 14:
            # Костыльная проверка на старый/новый формат таблиц
            parse_func = self._parse_new_table
        else:
            parse_func = self._parse_old_table

        for row in soup.find("table", {"class": "inf"}).find_all("tr")[1::]:
            total.append(parse_func(row.find_all("td")))

        return total

    def _generate_url(self) -> str:
        args = {"FROM": self.from_, "TO": self.to_, "SEMESTER": self.semester}
        return URL_TEMPLATE.format(**args)


class SummaryRetrospective:
    def __init__(self, from_: int, to_: int, session: Session = Session()):
        self.from_ = from_
        self.to_ = to_

        self._session = session

    def parse_retrospective(self) -> List[Dict[str, Any]]:
        """Парсит основную информацию по всем преподам и всем семестрам за определённый период"""
        summaries = []

        for i in range(self.from_, self.to_):
            try:
                summaries.extend(Summary(i, i + 1, 1, session=self._session).parse_summary())
                summaries.extend(Summary(i, i + 1, 2, session=self._session).parse_summary())
            except HTTPError:
                continue

        return summaries

    def parse_retrospective_all(self) -> List[Dict[str, Any]]:
        """Парсит всю информацию по всем преподам и всем семестрам за определённый период"""
        totals = []

        for i in range(self.from_, self.to_):
            try:
                totals.extend(Summary(i, i + 1, 1, session=self._session).parse_all())
                totals.extend(Summary(i, i + 1, 2, session=self._session).parse_all())
            except HTTPError:
                continue

        return totals

    def parse_format_retrospective(self) -> List[Dict[str, Any]]:
        """Форматирует ретроспективу основных данных в единый список для экспорта"""
        return format_data(self.parse_retrospective())

    def parse_format_retrospective_all(self) -> List[Dict[str, Any]]:
        """Форматирует ретроспективу всех данных в единый список для экспорта"""
        return format_data(self.parse_retrospective_all())
