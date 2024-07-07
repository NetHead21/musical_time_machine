import httpx
import selectolax.parser
from selectolax.parser import HTMLParser
from collections import namedtuple
from datetime import date, timedelta


Music = namedtuple("Music", ["title", "artist"])
entry_node = selectolax.parser.Node


def get_saturday_date(given_date: date):
    days_to_add = (5 - given_date.weekday() + 7) % 7
    return given_date + timedelta(days=days_to_add)


def check_date(input_date: date) -> bool:
    return input_date <= date.today()


def get_date() -> tuple:
    return tuple(
        int(part) for part in input("Enter date in (mm/dd/yyyy) format: ").split("/")
    )


def get_entry_attr(entry: entry_node, selector: str) -> str:
    element = entry.css_first(selector)
    return element.text().strip()


def extract_music_info(
    html: HTMLParser, title_selector: str, artist_selector: str
) -> list[Music]:
    top_music = []
    for i, music_entry in enumerate(
        html.css("ul.o-chart-results-list-row > li:nth-child(4)")
    ):
        if i == 20: # I limit it to top 20 only.
            break

        title = get_entry_attr(music_entry, title_selector)
        artist = get_entry_attr(music_entry, artist_selector)
        top_music.append(Music(title, artist))
    return top_music


def get_top_music(target_date: date) -> list[Music]:
    url = f"https://www.billboard.com/charts/hot-100/{target_date}/"
    response = httpx.get(url)
    html = HTMLParser(response.text)
    return extract_music_info(
        html, "#title-of-a-story", "#title-of-a-story + span.c-label"
    )


def get_input_date() -> date:
    while True:
        try:
            month, day, year = get_date()
            input_date = date(year, month, day)
            if input_date <= date.today():
                return input_date
            else:
                print("Invalid input! inputted date is greater than the current date.")
        except ValueError:
            print("Invalid date! please try again.")


if __name__ == "__main__":
    input_date = get_input_date()
    saturday_date = get_saturday_date(
        date(input_date.year, input_date.month, input_date.day)
    )

    top_music = get_top_music(saturday_date)
    print(top_music)
    for music in top_music:
        print(f"{music.title} by {music.artist}")
