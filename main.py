import re
import time
import asyncio
import functools
import validators
from itertools import chain
from typing import NamedTuple

import aiohttp
from bs4 import BeautifulSoup
from aiohttp import ClientSession

PUBMED_URL = "https://pubmed.ncbi.nlm.nih.gov"
PAGES_AMOUNT = 5


FILE_FORMATS = {
    "1": ".md",
    "2": ".txt",
}


def timer(func):
    @functools.wraps(func)
    async def inner(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        print(
            f"\nДанные успешно записаны!\nВремя работы программы составило {time.time()-start:.1f} сек."
        )
        return result

    return inner


class UserInputError(ValueError):
    pass


class ParseDataError(Exception):
    pass


class UrlPage(NamedTuple):
    url: str
    html_page: str | None


class TitleAbstract(NamedTuple):
    title: str
    abstract: list[str]


class FormattedSkippedResearches(NamedTuple):
    formatted_research: list[str]
    skipped_research: list[str | None]


class Url:
    def __get__(self, instance, owner=None) -> str:
        return self.value

    def __set__(self, instance, value: str) -> None:
        if value:
            if validators.url(value) and "https://pubmed.ncbi.nlm.nih.gov/?" in value:
                self.value = value
                return
            raise UserInputError("Invalid URL.")
        raise UserInputError("Empty string instead of URL.")


class Filename:
    def __get__(self, instance, owner=None) -> str:
        return self.value

    def __set__(self, instance, value: str) -> None:
        if value:
            raw_filename = value.strip().replace(" ", "_")
            clean_filename = re.sub(r"(?u)[^-\w.]", "", raw_filename)
            if clean_filename:
                self.value = clean_filename
                return
            raise UserInputError("Filename consists invalid characters.")

        raise UserInputError("Empty string instead of filename.")


class FileFormat:
    def __get__(self, instance, owner=None) -> str:
        return self.value

    def __set__(self, instance, value: str) -> str:

        if not value:
            self.value = FILE_FORMATS["1"]
            return

        if value not in FILE_FORMATS.keys():
            raise UserInputError(
                "Invalid format. To choose type of file type the number of one of the suggested choises or empty string to choose Markdown."
            )

        self.value = FILE_FORMATS[value]


class Input:

    url = Url()
    filename = Filename()
    file_format = FileFormat()

    def __init__(self, url: str, filename: str, file_format: str) -> None:
        self.url = url
        self.filename = filename
        self.file_format = file_format


class Parser:
    def __init__(self, session: ClientSession) -> None:
        self.session = session

    def parse_research_urls_from_page(self, html_page: str) -> list[str]:
        """Parse urls to all studies from one page."""
        soup = BeautifulSoup(html_page, "html.parser")
        try:
            div = soup.find("div", {"class": "search-results-chunks"})
            urls = div.findAll("a", {"class": "docsum-title"})
        except Exception as exc:
            raise ParseDataError(
                "Problem with parse researches, please check entered URL for corectless!"
            ) from exc

        return urls

    def parse_title_and_abstact(self, research_page: str) -> TitleAbstract:
        """Get title and abstract of research from his html-page"""
        soup = BeautifulSoup(research_page, "html.parser")
        try:
            title = soup.find("h1", class_="heading-title").text.strip()
            abstract_ps = soup.find("div", class_="abstract-content selected")
            abstract = abstract_ps.findAll("p")
        except Exception as exc:
            raise ParseDataError("Error when parsing a research!") from exc

        return TitleAbstract(title, abstract)

    async def get_research_urls(self, url: str) -> list[str | None]:
        """Return a list with URL's of researches"""
        """Возвращает список с ссылками на исследования."""
        async with self.session.get(url=url) as response:
            if response.status == 200:
                urls = self.parse_research_urls_from_page(await response.text())
                return [f"{PUBMED_URL}{url.get('href')}" for url in urls]
            return []

    async def get_research_page(self, page_url: str) -> UrlPage:
        """Parse page of research. If response.status_code != 200, then instead of page content return's None."""
        async with self.session.get(page_url) as response:
            if response.status == 200:
                page = await response.text()
                return UrlPage(page_url, page)
            else:
                return UrlPage(page_url, None)


class Editor:
    def clean_abstract(self, abstract: list[str]) -> str:
        """Clean abstract from service characters. Initially abstract  is a list of paragraphs."""
        if len(abstract) == 1:
            abstract[0] = re.sub(r"\s+", " ", abstract[0].text)
            return "".join(abstract)

        for i in range(len(abstract)):
            abstract[i] = re.sub(r"\s+", " ", abstract[i].text) + "\n\n"

        return "".join(abstract)

    def format_research(
        self, title: str, url: str, cleaned_abstract: str, file_format: str = ".md"
    ) -> str:
        """Format research to write in file."""
        match file_format:
            case ".md":
                return f"## **{title}**\n*{url}*<br>{cleaned_abstract}\n"
            case ".txt":
                return f"{title}\n\n{url}\n\n{cleaned_abstract}\n\n\n"
            case _:
                pass

    def get_formatted_research(
        self, research_data: list[UrlPage], parser: Parser, file_format: str
    ) -> FormattedSkippedResearches:
        """Parse title and abstract from html-page of research. Format them to write in file: add spaces, break lines and change size of fonts (for Mardown).

        Return two lists - formatted and skipped researches.
        """
        formatted_research, skipped_urls = [], []
        for url, research_page in research_data:
            try:
                title, abstract = parser.parse_title_and_abstact(research_page)
            except ParseDataError:
                skipped_urls.append(url)
            else:
                formatted_research.append(
                    editor.format_research(
                        title, url, editor.clean_abstract(abstract), file_format
                    )
                )
        return FormattedSkippedResearches(formatted_research, skipped_urls)


class Writer:
    def write_in_file(self, filename: str, text: str, file_format: str = ".md") -> None:
        """Write test into file with the passed extension."""
        with open(f"{filename}{file_format}", "w", encoding="utf-8") as f:
            f.write(text)


def user_input() -> Input:
    """Getting user's input."""
    url = input("URL: ").strip()
    filename = input("Filename: ")
    file_format = input(
        "What type of output file: .txt or .md?(default is .md)\n1 - .md\n2 - .txt\n"
    )

    return Input(url + "&page={}", filename, file_format)


def print_skipped_urls(skipped_urls: list[str] | None) -> None:
    """Print on the screen list of skipped researches."""
    if not skipped_urls:
        return

    print(f"\nWas skipped {len(skipped_urls)} research. Here are URL's to them:\n")
    for url in skipped_urls:
        print(url)


@timer
async def main(
    url: str, filename: str, file_format: str, editor: Editor, writer: Writer
) -> None:

    async with ClientSession() as session:
        parser = Parser(session)
        try:
            tasks = [
                parser.get_research_urls(url.format(page))
                for page in range(1, PAGES_AMOUNT + 1)
            ]
            research_urls: list[list[str | None]] = await asyncio.gather(*tasks)
        except ParseDataError as e:
            print(e)
            return
        except aiohttp.client_exceptions.InvalidURL:
            print("Enter correct URL!")
            return

        all_urls = list(chain(*research_urls))  # [[.], [..],] -> [., ..,]
        print(
            "\nResearch links have been successfully collected.\nData collection begins..."
        )

        tasks = [parser.get_research_page(research_url) for research_url in all_urls]
        research_data: list[UrlPage] = await asyncio.gather(*tasks)

    print("\nData successfully collected!\nPreparing and writing to file...")

    formatted_research, skipped_urls = editor.get_formatted_research(
        research_data, parser, file_format
    )

    writer.write_in_file(
        filename, text="".join(formatted_research), file_format=file_format
    )

    print_skipped_urls(skipped_urls)


if __name__ == "__main__":
    try:
        input_ = user_input()
    except UserInputError as e:
        print(e)
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        editor, writer = Editor(), Writer()
        asyncio.run(
            main(input_.url, input_.filename, input_.file_format, editor, writer)
        )
