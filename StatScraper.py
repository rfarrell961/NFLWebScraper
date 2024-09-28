import requests
from bs4 import BeautifulSoup
import pprint

#links
base_url = "https://www.nfl.com"
passing_leaders_url = "https://www.nfl.com/stats/player-stats/"
rushing_leaders_url = "https://www.espn.com/nfl/stats/player/_/stat/rushing"
receiving_leaders_url = "https://www.espn.com/nfl/stats/player/_/stat/receiving"

players = {}
headers = []
def ScrapePassingLeaders():
    
    page = requests.get(passing_leaders_url, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(page.content, "html.parser")
    
    # Retreive headers from first page
    main = soup.find(id="main-content")
    table = main.find("table")
    table_headers = table.find("thead").find("tr").find_all("th")
    for header in table_headers:
        a = header.find("a")
        if a is not None:
            headers.append(a.contents[0])

    # Read first page
    ScrapePassingLeadersPage(soup)
    next_page = soup.find(class_="nfl-o-table-pagination__next")    

    # Read remaining pages
    n = 1
    while next_page is not None:

        # Get next page
        page = requests.get(base_url + next_page["href"], headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")
        ScrapePassingLeadersPage(soup)

        next_page = soup.find(class_="nfl-o-table-pagination__next")   
        n += 1

    pprint.pprint(players)
    print(str(n) + " Pages Scraped")
    print(headers)

def ScrapePassingLeadersPage(soup):

    main = soup.find(id="main-content")
    table = main.find("table")
    table_rows = table.find("tbody").find_all("tr")
    for row in table_rows:

        columns = row.find_all("td")
        name = row.find(class_="d3-o-player-fullname nfl-o-cta--link").contents[0].strip()
        players[name] = {}
        for i in range(0, len(headers)):
            value = columns[i + 1].contents[0].strip()
            players[name][headers[i]] = value



if __name__ == "__main__":  
    ScrapePassingLeaders()
