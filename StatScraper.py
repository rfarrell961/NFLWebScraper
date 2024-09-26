import requests
from bs4 import BeautifulSoup

#links
base_url = "https://www.nfl.com"
passing_leaders_url = "https://www.nfl.com/stats/player-stats/"
rushing_leaders_url = "https://www.espn.com/nfl/stats/player/_/stat/rushing"
receiving_leaders_url = "https://www.espn.com/nfl/stats/player/_/stat/receiving"

def ScrapePassingLeaders():

    params = {
        "user": "cp-8uaAAAAAJ",       # user-id
        "hl": "en",                   # language
        "gl": "us",                   # country to search from
        "cstart": 0,                  # articles page. 0 is the first page
        "pagesize": "100"             # articles per page
    }

    page = requests.get(passing_leaders_url, params, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(page.content, "html.parser")
    
    headers = []
    main = soup.find(id="main-content")
    table = main.find("table")
    table_headers = table.find("thead").find("tr").find_all("th")
    for header in table_headers:
        a = header.find("a")
        if a is not None:
            headers.append(a.contents[0])

    players = []
    next_page = soup.find(class_="nfl-o-table-pagination__next")
    n = 0
    while next_page is not None:
        main = soup.find(id="main-content")
        table = main.find("table")
        table_rows = table.find("tbody").find_all("tr")
        for row in table_rows:
            players.append(row.find(class_="d3-o-player-fullname nfl-o-cta--link").contents[0].strip())

        next_page = soup.find(class_="nfl-o-table-pagination__next")
        if next_page is not None:
            page = requests.get(base_url + next_page["href"], params, headers={"User-Agent":"Mozilla/5.0"})
            soup = BeautifulSoup(page.content, "html.parser")

        n += 1

    print(players)
    print(str(n) + " Pages Scraped")

if __name__ == "__main__":  
    ScrapePassingLeaders()
