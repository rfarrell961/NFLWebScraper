import requests
from bs4 import BeautifulSoup
import pprint
import boto3

#links
base_url = "https://www.nfl.com"
passing_leaders_url = "https://www.nfl.com/stats/player-stats/"
rushing_leaders_url = "https://www.nfl.com/stats/player-stats/category/rushing/2024/reg/all/rushingyards/desc"
receiving_leaders_url = "https://www.nfl.com/stats/player-stats/category/receiving/2024/reg/all/receivingreceptions/desc"

players = {}
headers = []

def ScrapeCategory(link):
    
    page = requests.get(link, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(page.content, "html.parser")
    
    # Retreive headers from first page
    headers.clear()
    main = soup.find(id="main-content")
    table = main.find("table")
    table_headers = table.find("thead").find("tr").find_all("th")
    for header in table_headers:
        a = header.find("a")
        if a is not None:
            headers.append(a.contents[0])

    # Read first page
    ScrapePage(soup)
    next_page = soup.find(class_="nfl-o-table-pagination__next")    

    # Read remaining pages
    n = 1
    while next_page is not None:

        # Get next page
        page = requests.get(base_url + next_page["href"], headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")
        ScrapePage(soup)

        next_page = soup.find(class_="nfl-o-table-pagination__next")   
        n += 1

    print(str(n) + " Pages Scraped")

def ScrapePage(soup):

    main = soup.find(id="main-content")
    table = main.find("table")
    if table is None:
        return
    
    table_rows = table.find("tbody").find_all("tr")
    for row in table_rows:

        columns = row.find_all("td")
        name = row.find(class_="d3-o-player-fullname nfl-o-cta--link").contents[0].strip()

        if name not in players.keys():
            players[name] = {}

        for i in range(0, len(headers)):
            value = columns[i + 1].contents[0].strip()
            players[name][headers[i]] = value

def WritePlayersToDB():

    # Get the service resource.
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('NFL_Player_Stats')
    
    with table.batch_writer() as batch:
        for k, v in players.items():
            v["Player_Name"] = k
            batch.put_item(Item = v)

if __name__ == "__main__":  
    ScrapeCategory(passing_leaders_url)
    ScrapeCategory(rushing_leaders_url)
    ScrapeCategory(receiving_leaders_url)

    response = input("Would you like to upload to DB? (y/n): ")
    if response == "y" or response == "Y":
        print("Writing Players To DynamoDB...")
        WritePlayersToDB()

    query = input("Enter a players name: ")
    while query != "exit":
        if query in players.keys():
            pprint.pprint(players[query])
        else:
            print("Player not found")
        query = input("Enter a players name: ")
    
