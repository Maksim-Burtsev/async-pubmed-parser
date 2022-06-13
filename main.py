import re
import time

import requests
import fake_useragent
from bs4 import BeautifulSoup

from docx import Document
from docx.shared import Pt

from progress.bar import IncrementalBar


USER = fake_useragent.UserAgent().random
HEADER = {'user-agent': USER}

PUBMED_LINK = 'https://pubmed.ncbi.nlm.nih.gov'


def _clean_abstract(abstract: str) -> str:
    """
    Удаляет все лишние пробелы
    """

    if len(abstract) == 1:
        abstract[0] = re.sub(r'\s+', ' ', abstract[0].text)
        return (''.join(abstract))

    for i in range(len(abstract)):
        abstract[i] = re.sub(r'\s+', ' ', abstract[i].text) + '\n\n'

    return (''.join(abstract))


def _parser(url: str) -> list:
    """Собирает все ссылки на исследования со страницы"""

    response = requests.get(url, headers=HEADER)
    soup = BeautifulSoup(response.text, 'html.parser')

    div = soup.find('div', {'class': 'search-results-chunks'})
    links = div.findAll('a', {'class': 'docsum-title'})

    return links


def _get_all_research_links(link: str) -> list:
    """Собирает все ссылки на исследования с 5 страниц"""
    links_list = []

    bar = IncrementalBar('Обработано страниц', max=5)

    for i in range(1, 6):
        url = link + str(i)
        try:
            links = _parser(url)

            for link in links:
                links_list.append(link.get('href'))
        except:
            break

        else:
            bar.next()

    bar.finish()
    print("Ссылки собраны!")

    return links_list


def _write_missed_research(exception_links: list[str]) -> None:
    """Записывает в файл ссылки на все пропущенные исследования"""

    with open('Пропущенные исследования.txt', 'w', encoding='utf-8') as f:
        for i in range(len(exception_links)):
            f.write(str(exception_links[i])+'\n')


def _write_abstact_in_word(document: Document, abstract: str) -> None:
    """Записывает abstract в word-документ"""

    p = document.add_paragraph().add_run(f'\n{abstract}')
    font = p.font
    font.name = 'Calibri'
    font.size = Pt(14)


def _user_input() -> tuple[str, str]:
    """Используется для получения ввода пользователя"""

    link = input("Ссылка: ").strip() + '&page='
    file_name = input('Как назвать файл?')

    return link, file_name


def main():

    link, file_name = _user_input()
    exception_links = []
    start = time.time()
    k = 0

    links_list = _get_all_research_links(link=link)

    bar = IncrementalBar('Записано в файл', max=len(links_list))

    document = Document()
    document.add_heading(f'{file_name.capitalize()}', 0)

    run = document.add_paragraph().add_run()
    font = run.font
    font.name = 'Calibri'
    font.size = Pt(14)

    for i in links_list:

        link = PUBMED_LINK + str(i)
        response = requests.get(link, headers=HEADER).text
        soup = BeautifulSoup(response, 'html.parser')

        try:
            title = soup.find('h1', class_='heading-title').text.strip()
            document.add_heading(f'{title}', level=1)

            abstract_ps = soup.find('div', class_='abstract-content selected')
            abstract = abstract_ps.findAll('p')

        except Exception as e:
            exception_links.append(link)

        else:
            abstract = _clean_abstract(abstract)

            _write_abstact_in_word(document, abstract)

            document.add_heading(f'{link}', level=4)

        k += 1
        bar.next()

    document.save(f'{file_name}.docx')
    bar.finish()

    print(f"{k} исследований собрано.")
    print(f"\nвремя выполнения - {time.time() - start} sec")

    _write_missed_research(exception_links)


if __name__ == '__main__':
    main()
