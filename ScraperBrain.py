from bs4 import BeautifulSoup
import requests
import datetime

from Network import *

class ScraperBrain:
    """ ScraperBrain Handles all of the logic of figuring out how to parse Realtor Data
    after getting webSoup html code. Must be created with webSoup data.
    """
    results_list = []
    baseSite = "Https://www.realtor.com"
    max_Pages = 0
    lastHouseFound = False
    withinDaysSold = 7

    def __init__(self, webSoup):
        self.webSoup = webSoup

    def parseSoldContent(self, soup):
        """ 
        Takes in a BeautifulSoup Object that has already been converted and takes in a date
        """
        if not isinstance(soup, BeautifulSoup):
            raise ValueError("webSoup must be of Type: 'BeautifulSoup'")
        else:
            # Get all Property Cards and Parse Through All
            try:
                self.properties_Container: list = soup.find_all("section", class_="srp-content")[0].find_all("li", attrs={"data-testid":"result-card"}, class_="component_property-card")
                print(f"Number of properties on this page: {len(self.properties_Container)}")
            except Exception as ex:
                print(f"{type(ex)} Error occurred initializing Properties_Container: {ex}")
                 # Return False to retry URL
                return False
            
            # Parse through list of all Property Cards on single Page
            for prop in self.properties_Container:
                # Store each home data in a dictionary
                # TODO - Create class of Home with needed attributes
                home = {}

                # Find Home Simple Detail Div
                try:
                    homeDetailWrapper = prop.find("div", attrs={"data-testid":"property-detail"})
                except: 
                    print(f"{type(ex)} Error occured initializing detailWrapper: {ex}")
                    return False

                # Extract Home Status
                try:
                    status = homeDetailWrapper.find("span", class_="statusText").text
                    
                    # Determine date sold
                    if self.isStillInDateRange(self.formatDate(status)):
                        print("House sold within last week of today")
                        home["Status"] = status
                        self.lastHouseFound = False
                    else:
                        print("House not sold within past week")
                        self.lastHouseFound = True
                        break

                except AttributeError:
                    home["Status"] = None
                except Exception as ex:
                    print(f"{type(ex)} Error occured in Status: {ex}")
                    home["Status"] = None

                # Extract Price
                try:
                    home["Price"] = homeDetailWrapper.find("span", attrs={"data-label":"pc-price-sold"}).text
                except AttributeError:
                    home["Price"] = None
                except Exception as ex:
                    print(f"{type(ex)} Error occured in Status: {ex}")
                    home["Price"] = None

                # Extract Address
                try:
                    home["Address"] = homeDetailWrapper.find("div", class_="address", attrs={"data-label":"pc-address"}).text
                except AttributeError:
                    home["Address"] = None
                except Exception as ex:
                    print(f"{type(ex)} Error occured in Status: {ex}")
                    home["Address"] = None

                # Extract Web Address
                try:
                    home["Link"] = self.baseSite + (prop.find("div", class_="photo-wrap").find("a", href=True)['href'])
                except AttributeError:
                    home["Link"] = "Attribute Error"
                except Exception as ex:
                    print(f"{type(ex)} Error occured in Status: {ex}")
                    home["Link"] = "Exception Error"

                self.results_list.append(home)

    def requestNewURL(self, mainNetwork: Network, url) -> BeautifulSoup:
        """
        Takes in base url to scrape through and converts into BeautifulSoup
        """
        print(f"Looking at webpage: {url}")
        
        payload = { "api_key": mainNetwork.scraperAPI_Key, "url": url }
        req = requests.get("http://api.scraperapi.com",params=payload,headers=mainNetwork.header)

        if req.status_code != 200:
            print(f"STATUS CODE FOR {url} : {req.status_code}")
        if req.status_code == 500:
            print("Request error 500. Trying again")
            req = requests.get("http://api.scraperapi.com",params=payload,headers=mainNetwork.header)
        
        contents = req.text.strip()
        
        return BeautifulSoup(contents, "html.parser")
        # if not self.parseSoldContent(soup):
        #     # something went wrong getting property container. Try URL again.
        #     print("Trying URL Again")
        #     self.requestNewURL(mainNetwork, url)
        # else:
        #     return soup

    def formatDate(self, stringToFormat) -> datetime.date:
        """
        Takes in Date String data and returns a datatime.date object representation.
        """
        splitString = stringToFormat.split(" - ")
        formatedDate = datetime.datetime.strptime(splitString[-1], '%b %d, %Y').date()
        return formatedDate

    def isStillInDateRange(self, dateToCheck: datetime.date) -> bool:
        """
        Determines if property is within days sold
        """
        past =  (datetime.datetime.now() - datetime.timedelta(days=self.withinDaysSold)).date()
        present = datetime.datetime.now().date()
        return present >= dateToCheck >= past

