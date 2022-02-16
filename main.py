import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import re
from docx import Document
from docx.shared import Pt
from progress.bar import IncrementalBar


USER = fake_useragent.UserAgent().random
HEADER = {'user-agent': USER}

PUBMED_LINK = 'https://pubmed.ncbi.nlm.nih.gov'


def clean_abstract(abstract):
    """Удаляет все лишние пробелы"""

    if len(abstract) == 1:
        abstract[0] = re.sub(r'\s+', ' ', abstract[0].text)
        return (''.join(abstract))

    for i in range(len(abstract)):
        abstract[i] = re.sub(r'\s+', ' ', abstract[i].text) + '\n\n'

    return (''.join(abstract))


def parser(url: str) -> list:
    """Собирает все ссылки на исследования со страницы"""

    response = requests.get(url, headers=HEADER)
    soup = BeautifulSoup(response.text, 'html.parser')

    div = soup.find('div', class_='search-results-chunks')
    links = div.findAll('a', class_='docsum-title')

    return links


def get_s_links():
    """Собирает все ссылки на исследования с 5 страниц"""
    links_list = []

    bar = IncrementalBar('Обработано страниц', max=5)

    for i in range(1, 6):
        url = LINK + str(i)
        try:
            links = parser(url)

            for link in links:
                links_list.append(link.get('href'))
        except:
            break

        else:
            bar.next()

    bar.finish()
    print("Ссылки собраны!")

    return links_list


def missed_s(exception_links):
    """Записывает в файл ссылки на все пропущенные исследования"""

    with open('Пропущенные исследования.txt', 'w', encoding='utf-8') as f:
        for i in range(len(exception_links)):
            f.write(str(exception_links[i])+'\n')


def write_abstact(document, abstract):
    """Записывает abstract в word-документ"""
    
    p = document.add_paragraph().add_run(f'\n{abstract}')
    font = p.font
    font.name = 'Calibri'
    font.size = Pt(14)


def user_input():
    """Используется для получения ввода пользователя"""

    global LINK, file_name
    LINK = input("Ссылка: ").strip() + '&page='

    file_name = input('Как назвать файл?')


def main():

    user_input()
    exception_links = []
    k = 0

    start = time.time()
    links_list = get_s_links()

    bar = IncrementalBar('Записано в файл', max=len(links_list))

    document = Document()
    document.add_heading('Testosterone', 0)

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
            abstract = clean_abstract(abstract)

            write_abstact(document, abstract)

            document.add_heading(f'{link}', level=4)

        k += 1
        bar.next()

    document.save(f'{file_name}.docx')
    bar.finish()

    print(f"{k} исследований собрано.")
    print(f"\nвремя выполнения - {time.time() - start} sec")

    missed_s(exception_links)


if __name__ == '__main__':
    main()
