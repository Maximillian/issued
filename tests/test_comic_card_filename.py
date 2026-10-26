from pathlib import Path

from jinja2 import Environment, FileSystemLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = PROJECT_ROOT / "reader" / "templates"


def render_comic_card_filename(filename: str) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    template = env.from_string(
        "{% from 'partials/comics-section.html' import comic_card_filename %}"
        "{{ comic_card_filename(filename) }}"
    )
    return template.render(filename=filename)


def test_comic_card_filename_markup():
    issue = render_comic_card_filename("Issue 1.cbz")
    assert 'Issue 1<span class="comic-card-extension">.cbz</span>' in issue
    assert "Issue 1 <span" not in issue

    archive = render_comic_card_filename("Archive.tar.cbz")
    assert 'Archive.tar<span class="comic-card-extension">.cbz</span>' in archive

    readme = render_comic_card_filename("README")
    assert "comic-card-extension" not in readme
    assert '<span class="line-clamp-2 block text-center text-sm font-medium text-gray-800">README</span>' in readme

    dotfile = render_comic_card_filename(".cbz")
    assert "comic-card-extension" not in dotfile
    assert '<span class="line-clamp-2 block text-center text-sm font-medium text-gray-800">.cbz</span>' in dotfile


def test_continue_reading_title_hides_with_the_same_extension_span():
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    env.globals["url_path"] = lambda *args, **kwargs: "/reader/comic"
    html = env.get_template("partials/continue-reading.html").render(
        continue_reading_comics=[
            {
                "uuid": "abc",
                "filename": "Issue 1.cbz",
                "page_count": 12,
                "current_page": 3,
            }
        ],
        request=None,
    )

    assert 'text-xs' in html
    assert 'Issue 1<span class="comic-card-extension">.cbz</span>' in html
    assert "12 pages" in html


def test_last_added_and_table_titles_use_the_extension_span():
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    env.globals["url_path"] = lambda *args, **kwargs: "/reader/comic"
    comic = {"uuid": "abc", "filename": "Archive.tar.cbz", "page_count": 20}

    last_added = env.get_template("partials/last-added.html").render(
        show_last_added=True,
        last_added_comics=[comic],
        request=None,
    )
    assert 'text-xs' in last_added
    assert 'Archive.tar<span class="comic-card-extension">.cbz</span>' in last_added
    assert "20 pages" in last_added

    table = env.from_string(
        "{% from 'partials/comics-section.html' import comic_table %}"
        "{{ comic_table(comics, request) }}"
    ).render(comics=[comic], request=None)
    assert '<p class="font-semibold text-gray-900 leading-snug line-clamp-2">Archive.tar<span class="comic-card-extension">.cbz</span></p>' in table
