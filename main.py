import re
import time
import asyncio
from typing import NamedTuple

import aiohttp
from bs4 import BeautifulSoup
from aiohttp import ClientSession

PUBMED_URL = "https://pubmed.ncbi.nlm.nih.gov"


class UserInputError(ValueError):
    pass


class ParseDataError(Exception):
    pass


class UserInput(NamedTuple):
    url: str
    filename: str


class UrlPage(NamedTuple):
    url: str
    html_page: str | None


class TitleAbstract(NamedTuple):
    title: str
    abstract: list[str]


def user_input() -> UserInput:
    """Получения ввода пользователя."""

    url = input("Ссылка: ").strip()
    if not url:
        raise UserInputError("\nПустая строка вместо ссылки!")

    filename = input("Как назвать файл? ")
    if not filename:
        raise UserInputError("\nПустое имя файла!")

    return UserInput(url + "&page={}", filename)


def parse_research_urls_from_page(html_page: str) -> list[str]:
    """Парсит ссылки на все исследования с одной страницы."""
    soup = BeautifulSoup(html_page, "html.parser")
    try:
        div = soup.find("div", {"class": "search-results-chunks"})
        urls = div.findAll("a", {"class": "docsum-title"})
    except:
        raise ParseDataError(
            "Проблема со сбором исследований, проверьте введённую ссылку!"
        )

    return urls


def parse_title_and_abstact(research_page: str) -> TitleAbstract:
    """Достаёт название и абстракт исследования из его html-страницы."""
    soup = BeautifulSoup(research_page, "html.parser")
    try:
        title = soup.find("h1", class_="heading-title").text.strip()
        abstract_ps = soup.find("div", class_="abstract-content selected")
        abstract = abstract_ps.findAll("p")
    except:
        raise ParseDataError("Ошибка при парсинге исследования!")

    return TitleAbstract(title, abstract)


async def get_research_urls(url: str) -> list[str | None]:
    """Возвращает список с ссылками на исследования."""
    async with ClientSession() as session:
        async with session.get(url=url) as response:
            if response.status == 200:
                urls = parse_research_urls_from_page(await response.text())
                return [f"{PUBMED_URL}{url.get('href')}" for url in urls]
            return []


async def get_research_page(page_url: str) -> UrlPage:
    """Парсит страницу исследования. Если status code ответа != 200, то вместо содержимого страницы возвращается None."""
    async with ClientSession() as session:
        async with session.get(page_url) as response:
            if response.status == 200:
                page = await response.text()
                return UrlPage(page_url, page)
            else:
                return UrlPage(page_url, None)


def clean_abstract(abstract: list[str]) -> str:
    """Очищает абстракт от служебных символов. Изначально абстракт представляет собой список абзацев."""
    if len(abstract) == 1:
        abstract[0] = re.sub(r"\s+", " ", abstract[0].text)
        return "".join(abstract)

    for i in range(len(abstract)):
        abstract[i] = re.sub(r"\s+", " ", abstract[i].text) + "\n\n"

    return "".join(abstract)


def write_in_md_file(filename: str, text: str) -> None:
    """Записывает текст в Markdown-файл."""
    with open(f"{filename}.md", "w", encoding="utf-8") as f:
        f.write(text)


async def main(url: str, filename: str) -> None:
    start = time.time()

    try:
        tasks = [get_research_urls(url.format(page)) for page in range(1, 4)]
        research_urls: list[list[str | None]] = await asyncio.gather(*tasks)
    except ParseDataError as e:
        print(e)
        return
    except aiohttp.client_exceptions.InvalidURL:
        print("Введите правильную ссылку!")
        return

    all_urls = []
    for urls in research_urls:
        all_urls.extend(urls)
    print("\nСсылки на исследования собраны.\nНачинается сбор данных...")

    tasks = [get_research_page(research_url) for research_url in all_urls]
    research_data: list[UrlPage] = await asyncio.gather(*tasks)

    print("\nДанные собраны!\nПодготовка и запись в файл...")

    formatted_research, skipped_urls = [], []
    for url, research_page in research_data:
        try:
            title, abstract = parse_title_and_abstact(research_page)
        except ParseDataError:
            skipped_urls.append(url)
        else:
            formatted_research.append(
                f"## **{title}**\n*{url}*<br>{clean_abstract(abstract)}\n"
            )
    if skipped_urls:
        print(f"\nБыло пропущенно {len(skipped_urls)} исследований.")

    write_in_md_file(filename, text="".join(formatted_research))

    print(
        f"\nДанные успешно записаны!\nВремя работы программы составило {time.time()-start:.1f} сек."
    )


if __name__ == "__main__":
    try:
        url, filename = user_input()
    except UserInputError as e:
        print(e)
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main(url, filename))
