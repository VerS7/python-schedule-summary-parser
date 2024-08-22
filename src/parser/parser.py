"""
Парсер итогов по преподам из https://shedule.uni-dmitrov.ru/
"""
from typing import List, Dict

from requests import Session, Response, HTTPError
from bs4 import BeautifulSoup

URL_TEMPLATE = "https://shedule.uni-dmitrov.ru/20{FROM}{TO}_{SEMESTER}"


def _decode(text: str) -> str:
    return text.encode('latin1').decode('cp1251')


class Summary:
    def __init__(self, from_: int, to_: int, semester: int):
        self.from_ = from_
        self.to_ = to_
        self.semester = semester
        self._url = self._generate_url()

        self._session = Session()

    def parse_all_teachers(self) -> List[Dict[str, str]]:
        """Парсит ФИО преподавателей и URL на итоги"""
        response = self._get_response(self._url + "/vp.htm")
        soup = BeautifulSoup(response.text, "html.parser")
        teachers = []
        for row in soup.find("table", {"class": "inf"}).find_all("a"):
            teachers.append({"ФИО": _decode(row.text),
                             "URL": self._url + f"/{row.attrs['href']}"})
        return teachers

    def parse_summary(self):
        """Парсит всю информацию по всем преподам"""
        teachers = self.parse_all_teachers()
        summary = []
        for teacher in teachers:
            t_data = self._parse_total(self._get_response(teacher["URL"]))
            summary.append({"ФИО": teacher["ФИО"],
                            "Группы": [d["Группа"] for d in t_data],
                            "Дисциплины": list(set([d["Дисциплина"] for d in t_data])),
                            "Сумм. часов": sum([d["Часы"] for d in t_data])})
        return summary

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
