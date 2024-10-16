import requests
from bs4 import BeautifulSoup, NavigableString
import pprint
import boto3

# Links
baseUrl = "https://www.cbssports.com"

players = {}
categories = ["passing", "rushing", "receiving", "kicking", "scoring", "defense", "punt-Returns", "punting"]
# categories = ["kicking"] # DEBUG

def ScrapeCategories():

    for category in categories:
        link = f"https://www.cbssports.com/nfl/stats/player/{category}/nfl/regular/qualifiers/"
        page = requests.get(link, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")
        print(category)
        ScrapeCategory(soup)

def ScrapeCategory(soup: BeautifulSoup):

    headers = []

    # Find Headers
    tableRowHeaders = soup.find("tr", class_="TableBase-headTr")
    tableHeaders = tableRowHeaders.find_all("th")
    for tableHeader in tableHeaders:
        headers.append(tableHeader.find("div", class_="Tablebase-tooltipInner").contents[0].strip())

    hasPage = True
    while hasPage:

        tableRows = soup.find_all("tr", class_="TableBase-bodyTr")
        for tableRow in tableRows:

            player = {}
            name = ""
            tableRowColumns = tableRow.find_all("td")
            for i in range(0, len(headers)):   

                tableRowColumn = tableRowColumns[i]

                # Handle Player name, team, and position first
                if i == 0:
                    nameSpan = tableRowColumn.find("span", class_="CellPlayerName--long")
                    nameSpan = nameSpan.contents[0]

                    # Rare, but some players only have name
                    if isinstance(nameSpan.contents[0], NavigableString):
                        name = nameSpan.contents[0].strip()
                    else:
                        name = nameSpan.contents[0].contents[0].strip()
                        player["Position"] = nameSpan.contents[1].contents[0].strip()
                        player["Team"] = nameSpan.contents[2].contents[0].strip()
                    continue

                else:
                    
                    player[headers[i]] = tableRowColumn.contents[0].strip()
                    continue
            
            # Merge existing if player already exists
            if name in players.keys():
                players[name] = {**players[name], **player}
            else:
                players[name] = player


        nextPage = soup.find("a", attrs={"aria-label": "Go to Next Page"})
        if nextPage is None:
            hasPage = False
        else:
            page = requests.get(baseUrl + nextPage["href"], headers={"User-Agent":"Mozilla/5.0"})
            soup = BeautifulSoup(page.content, "html.parser")

def WritePlayersToDB():

    # Get the service resource.
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('NFL_Player_Stats')
    
    with table.batch_writer() as batch:
        for k, v in players.items():
            v["Player"] = k
            batch.put_item(Item = v)

if __name__ == "__main__":  

    # Execute Scraping
    ScrapeCategories()

    # Write to DB
    response = input("Would you like to upload to DB? (y/n): ")
    if response == "y" or response == "Y":
        print("Writing Players To DynamoDB...")
        WritePlayersToDB()


    # Query Players
    query = input("Enter a players name: ")
    while query != "exit":
        if query in players.keys():
            pprint.pprint(players[query])
        else:
            print("Player not found")
        query = input("Enter a players name: ")
    
