import sys
import requests
from bs4 import BeautifulSoup, Tag
from processor import process_fandom_page
from utils import get_fandom_link, fetch_page, find_title

# Author :    Qiaoo

def main():
    link = get_fandom_link(sys.argv)
    if not link:
        print("Link tidak boleh kosong. Program berhenti.")
        sys.exit(1)

    # Determine intro link
    intro_link = link
    if link.endswith("/Lore") or link.endswith("/Dialogue") or link.endswith("/Backstory"):
        intro_link = link.rsplit("/", 1)[0]

    # Fetch pages
    try:
        main_soup = fetch_page(link)
        intro_soup = fetch_page(intro_link, is_intro=True) if intro_link != link else None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        sys.exit(1)

    # Find character name
    title_source_soup = intro_soup if intro_soup else main_soup
    char_name = find_title(title_source_soup)
    if not char_name:
        print("Judul artikel (h1 dengan class 'page-header__title') tidak ditemukan.")
        sys.exit(1)

    # Process and write output
    output_lines = process_fandom_page(main_soup, intro_soup, intro_link, char_name, link)

    with open("output/fandom_output.py", "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    print("Output berhasil ditulis ke fandom_output.py")

if __name__ == "__main__":
    main()
