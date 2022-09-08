import pytest

from main import (
    get_format_by_code,
    chain_research_urls,
    Editor,
    InputValidator,
    UserInputError,
    AllUrlsSkippedPages,
)


@pytest.fixture
def validator():
    return InputValidator()


@pytest.fixture
def editor():
    return Editor()

class TestChain:

    def test_chain(self):
        assert chain_research_urls(
            [
                ["url1", "url2"],
                ["url3", "url4"],
                ["url5", "url6"],
                "skipped_url",
            ]
        ) == AllUrlsSkippedPages(
            all_urls=["url1", "url2", "url3", "url4", "url5", "url6"],
            skipped_pages=[
                "skipped_url",
            ],
        )


    def test_chain_skipped_urls_only(self):
        assert chain_research_urls(
            [[], [], [], "skipped_url1", "skipped_url2", "skipped_url3"]
        ) == AllUrlsSkippedPages(
            all_urls=[], skipped_pages=["skipped_url1", "skipped_url2", "skipped_url3"]
        )


class TestInputValidation:
    def test_wrong_url(self, validator):
        with pytest.raises(ValueError):
            validator.url("wrong url")

    def test_correct_url(self, validator):
        assert validator.url("https://pubmed.ncbi.nlm.nih.gov/?term=test+url")

    def test_incorrect_filename(self, validator):
        with pytest.raises(ValueError):
            validator.filename("\n\t\n")

    def test_empty_filename(self, validator):
        with pytest.raises(ValueError):
            validator.filename("")

    def test_correct_filname(self, validator):
        assert validator.filename("correct name")

    def test_incorrect_pages_amount(self, validator):
        with pytest.raises(ValueError):
            validator.pages_amount(10_000)

        with pytest.raises(ValueError):
            validator.pages_amount(-1)

    def test_pages_amount(self, validator):
        assert validator.pages_amount(77)

    def test_get_format_by_code(self):
        assert get_format_by_code("1")

    def test_get_format_by_empty_code(self):
        assert get_format_by_code("") == ".md"

    def test_get_format_by_wrong_code(self):
        with pytest.raises(UserInputError):
            get_format_by_code("12453531632958285")


class TestEditor:
    def test_clean_abstract(self, editor):
        test_abstract = [
            "fdsj     fdj     fdjjf   d   \t\t",
        ]
        assert editor.clean_abstract(test_abstract) == "fdsj fdj fdjjf d \n\n"

    def test_clean_abstract_with_paragraphs(self, editor):
        test_abstract = ["fdsg  ", "fds dfd", "   ddfff"]
        assert editor.clean_abstract(test_abstract) == "fdsg \n\nfds dfd\n\n ddfff\n\n"

    def test_format_research_md(self, editor):
        assert (
            editor.format_research(
                title="test title",
                url="https://test.com",
                cleaned_abstract="this is cleaned abstract",
                file_format=".md",
            )
            == "## **test title**\n*https://test.com*<br>this is cleaned abstract\n"
        )

    def test_format_research_txt(self, editor):
        editor.format_research(
            title="test title",
            url="https://test.com",
            cleaned_abstract="this is cleaned abstract",
            file_format=".txt",
        ) == "test title\n\nhttps://test.com\n\nthis is cleaned abstract\n\n\n"

    def test_format_research_wrong_type(self, editor):
        with pytest.raises(ValueError):
            editor.format_research(
                title="test title",
                url="https://test.com",
                cleaned_abstract="this is cleaned abstract",
                file_format=".wrong_format",
            )
