"""
Парсер итогов по преподам из https://shedule.uni-dmitrov.ru/
"""
from typing import List, Dict, Any

from requests import Session, Response, HTTPError
from bs4 import BeautifulSoup

URL_TEMPLATE = "https://shedule.uni-dmitrov.ru/20{FROM}{TO}_{SEMESTER}"


def format_data(parsed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Форматирует данные с итогов или ретроспективы в единый список для экспорта"""
    result = []

    for elem in parsed:
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
            teachers.append({"ФИО": _decode(row.text),
                             "URL": self._url + f"/{row.attrs['href']}"})
        return teachers

    def parse_summary(self) -> List[Dict[str, Any]]:
        """Парсит всю информацию по всем преподам"""
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
                                     "Сумм. часов": sum([d["Часы"] for d in t_data])}})
        return summary

    def parse_format_summary(self) -> List[Dict[str, Any]]:
        """Форматирует данные с итогов в единый список для экспорта"""
        return format_data(self.parse_summary())

    def _get_response(self, url: str) -> Response:
        response = self._session.post(url)

        if response.status_code == 404:
            raise HTTPError(f"Ничего не найдено по URL {url}")
        if response.status_code != 200:
            raise HTTPError(f"Произошла непредвиденная ошибка. URL: {url}")

        return response

    def _parse_total(self, response: Response) -> List[Dict[str, str]]:
        soup = BeautifulSoup(response.text, "html.parser")
        total = []
        for row in soup.find("table", {"class": "inf"}).find_all("tr")[1::]:
            data = row.find_all("td")
            total.append({"ФИО": _decode(data[1].text),
                          "Группа": _decode(data[2].text),
                          "Дисциплина": _decode(data[4].text),
                          "Часы": int(data[6].text)})
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
        """Парсит всю информацию по всем преподам и всем семестрам за определённый период"""
        summaries = []

        for i in range(self.from_, self.to_):
            try:
                summaries.extend(Summary(i, i + 1, 1, session=self._session).parse_summary())
                summaries.extend(Summary(i, i + 1, 2, session=self._session).parse_summary())
            except HTTPError:
                continue

        return summaries

    def parse_format_retrospective(self) -> List[Dict[str, Any]]:
        """Форматирует данные с ретроспективы в единый список для экспорта"""
        return format_data(self.parse_retrospective())
