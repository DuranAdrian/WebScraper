from bs4 import BeautifulSoup
import requests

class Network:
    # Insert Own ScraperAPI Key here
    scraperAPI_Key = ""
    header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,'referer':'https://www.google.com/'}

    def __init__(self, baseURL):
        self.baseUrl = baseURL
        
    def getPageData(self, url) -> BeautifulSoup:
        payload = { "api_key": self.scraperAPI_Key, "url": url }
        req = requests.get("http://api.scraperapi.com",params=payload,headers=self.header)
        contents = req.text.strip()
        return BeautifulSoup(contents, "html.parser")

    # def requestNewURL(self, url):
    #     """
    #     Takes in base url to scrape through and converts into BeautifulSoup
    #     """
    #     print("Looking at webpage: %s" % url)
        
    #     payload = { "api_key": self.scraperAPI_Key, "url": url }
    #     req = requests.get("http://api.scraperapi.com",params=payload,headers=self.header)

    #     if req.status_code != 200:
    #         print("STATUS CODE FOR %s : %s" % (url, req.status_code))
    #     if req.status_code == 500:
    #         print("Request error 500. Trying again")
    #         req = requests.get("http://api.scraperapi.com",params=payload,headers=self.header)
        
    #     contents = req.text.strip()
    #     soup = BeautifulSoup(contents, "html.parser")
    #     if not parseContent(soup, False):
    #         # something went wrong getting property container. Try URL again.
    #         print("Trying URL Again")
    #         self.requestNewURL(url)
