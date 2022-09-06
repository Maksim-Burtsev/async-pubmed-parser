import re
import sys
import time
import asyncio
import functools
import validators
from typing import NamedTuple

import aiohttp
from bs4 import BeautifulSoup
from aiohttp import ClientSession

PUBMED_URL = "https://pubmed.ncbi.nlm.nih.gov"
DEFAULT_PAGES_AMOUNT = 5


FILE_FORMATS = {
    "1": ".md",
    "2": ".txt",
}

# TODO input pages amount
# TODO if not formatted_researches
# https://breakpoint.black/review/4d143bfd-5b12-441f-b820-c3e45eb3f61e/


class ParseDataError(Exception):
    pass


class UserInputError(ValueError):
    pass


class FileFormatError(ValueError):
    pass


class UrlPage(NamedTuple):
    url: str
    html_page: str | None


class UrlStatus(NamedTuple):
    url: str
    status: int


class TitleAbstract(NamedTuple):
    title: str
    abstract: list[str]


class AllUrlsSkippedPages(NamedTuple):
    all_urls: list[str | None]
    skipped_pages: list[UrlStatus | None]


class FormattedSkippedResearches(NamedTuple):
    formatted_research: list[str]
    skipped_research: list[str | None]


def timer(func):
    @functools.wraps(func)
    async def inner(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        print(
            f"\nSuccess! Now you can view collected researches in your file.\nThe running time was {time.time()-start:.1f} sec."
        )
        return result

    return inner


def chain_research_urls(urls: list[list[str | None]] | str) -> AllUrlsSkippedPages:
    """Join nested lists with researches into a single list.

    [[...], [...], [...]] -> [..., ..., ...]

    All skipped pages (str's in list) saved in separeted list.
    """

    all_urls, skipped_pages = [], []
    for url in urls:
        if isinstance(url, str):
            skipped_pages.append(url)
        else:
            all_urls.extend(url)

    return AllUrlsSkippedPages(all_urls, skipped_pages)


def print_skipped_urls(
    skipped_pages: list[str | None], skipped_urls: list[str | None]
) -> None:
    """Print on the screen list of skipped researches."""
    if skipped_pages:
        print(f"\nWas skipped {len(skipped_pages)} pages. Here are URL's to them:\n")
        for url in skipped_pages:
            print(url)

    if skipped_urls:
        print(f"\nWas skipped {len(skipped_urls)} research. Here are URL's to them:\n")
        for url in skipped_urls:
            print(url)


class Url:
    def __get__(self, instance, owner=None) -> str:
        return self.value

    def __set__(self, instance, value: str) -> None:
        if not value:
            raise UserInputError("Empty string instead of URL.")

        if (
            not validators.url(value)
            or not value.startswith("https://pubmed.ncbi.nlm.nih.gov/?")
            or "term=" not in value
        ):
            raise UserInputError("Invalid URL.")

        self.value = value.strip().replace(" ", "+")


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

    def __set__(self, instance, value: str) -> None:

        if not value:
            self.value = FILE_FORMATS["1"]
            return None

        try:
            self.value = FILE_FORMATS[value]
        except KeyError as exc:
            raise UserInputError(
                "Invalid format. To choose type of file type the number of one of the suggested choises or empty string to choose Markdown."
            ) from exc


class PagesAmount:
    def __get__(self, instance, owner=None) -> int:
        return self.value

    def __set__(self, instance, value: int) -> None:
        try:
            value = int(value)
        except ValueError as exc:
            raise UserInputError("Pages amount must be digit.") from exc

        if not 1 <= value <= 1_000:
            raise UserInputError("Page amout must be in between [1, 1000].")

        self.value = value


class Input:

    url = Url()
    filename = Filename()
    file_format = FileFormat()
    pages_amount = PagesAmount()

    def __init__(
        self, url: str, filename: str, file_format: str, pages_amount: int
    ) -> None:
        self.url = url
        self.filename = filename
        self.file_format = file_format
        self.pages_amount = pages_amount


class Parser:
    def __init__(self, session: ClientSession) -> None:
        self.session = session

    def parse_research_urls_from_page(self, html_page: str) -> list[str | None]:
        """Parse urls to all studies from one page."""
        soup = BeautifulSoup(html_page, "html.parser")
        div = soup.find("div", {"class": "search-results-chunks"})
        try:
            urls = div.findAll("a", {"class": "docsum-title"})
        except AttributeError as exc:
            raise ParseDataError(
                "Problem with parse researches, please check entered URL for corectless!"
            ) from exc
        return [url.get("href") for url in urls]

    def parse_title_and_abstact(self, research_page: str) -> TitleAbstract:
        """Get title and abstract of research from his html-page"""
        soup = BeautifulSoup(research_page, "html.parser")
        try:
            title = soup.find("h1", class_="heading-title").text.strip()
            abstract_ps = soup.find("div", class_="abstract-content selected")
            abstract = abstract_ps.findAll("p")
        except Exception as exc:
            raise ParseDataError("Error when parsing a research!") from exc
        return TitleAbstract(title, [par.text for par in abstract])

    async def get_research_urls(self, url: str) -> list[str | None] | str:
        """Return a list with URL's of researches"""
        async with self.session.get(url=url) as response:
            if response.status == 200:
                urls = self.parse_research_urls_from_page(await response.text())
                return [f"{PUBMED_URL}{url}" for url in urls]
            return url

    async def get_research_page(self, page_url: str) -> UrlPage:
        """Parse page of research. If response.status_code != 200, then instead of page content return's None."""
        async with self.session.get(page_url) as response:
            if response.status == 200:
                page = await response.text()
                return UrlPage(page_url, page)
            return UrlPage(page_url, None)


class Editor:
    def clean_abstract(self, abstract: list[str]) -> str:
        """Clean abstract from service characters. Initially abstract  is a list of paragraphs."""
        for i in range(len(abstract)):
            abstract[i] = re.sub(r"\s+", " ", abstract[i]) + "\n\n"
        return "".join(abstract)

    def format_research(
        self, title: str, url: str, cleaned_abstract: str, file_format: str
    ) -> str | None:
        """Format research to write in file."""
        match file_format:
            case ".md":
                return f"## **{title}**\n*{url}*<br>{cleaned_abstract}\n"
            case ".txt":
                return f"{title}\n\n{url}\n\n{cleaned_abstract}\n\n\n"
            case _:
                raise FileFormatError("Unsupported file format.")

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
        if not text:
            return
        with open(f"{filename}{file_format}", "w", encoding="utf-8") as f:
            f.write(text)


def user_input() -> Input:
    """Getting user's input."""
    url = input("URL: ").strip()
    filename = input("Filename: ")
    file_format = input(
        "What type of output file: .txt or .md?(default is .md)\n1 - .md\n2 - .txt\n"
    )

    pages_amount = (
        input("\nHow many pages do you want to get? ")
        if input(
            "Default amount of pages is 5 (1 page = 50 research).\nDo you want to change it? [Y-yes, N-no] "
        ).lower()
        in ["yes", "y", "ye", "ys"]
        else DEFAULT_PAGES_AMOUNT
    )

    return Input(url + "&page={}", filename, file_format, pages_amount)


@timer
async def main(
    url: str,
    filename: str,
    file_format: str,
    pages_amount: int,
    editor: Editor,
    writer: Writer,
) -> None:

    async with ClientSession() as session:
        parser = Parser(session)
        try:
            tasks = [
                parser.get_research_urls(url.format(page))
                for page in range(1, pages_amount + 1)
            ]
            research_urls = await asyncio.gather(*tasks)
        except ParseDataError as e:
            print(e)
            sys.exit()
        except aiohttp.client_exceptions.InvalidURL:
            print("Enter correct URL!")
            sys.exit()

        all_urls, skipped_pages = chain_research_urls(
            research_urls
        )  # [[.], [..],] -> [., ..,]
        if not all_urls:
            raise UserInputError("There is no research on your URL. Please check it!")

        print(
            "\nResearch links have been successfully collected.\nData collection begins..."
        )

        tasks = [parser.get_research_page(research_url) for research_url in all_urls]
        research_data = await asyncio.gather(*tasks)

    print("\nData successfully collected!\nPreparing and writing to file...")

    formatted_research, skipped_researches = editor.get_formatted_research(
        research_data, parser, file_format
    )

    writer.write_in_file(
        filename, text="".join(formatted_research), file_format=file_format
    )

    print_skipped_urls(skipped_pages, skipped_researches)


if __name__ == "__main__":
    try:
        input_ = user_input()
    except UserInputError as e:
        print(e)
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        editor, writer = Editor(), Writer()
        asyncio.run(
            main(
                url=input_.url,
                filename=input_.filename,
                file_format=input_.file_format,
                pages_amount=input_.pages_amount,
                editor=editor,
                writer=writer,
            )
        )
