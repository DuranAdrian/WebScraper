import pandas
import requests
from bs4 import BeautifulSoup
import time, datetime

city = "San-Leandro"
realtor_base_url = "https://www.realtor.com/realestateandhomes-search/%s_CA" % city
scraperapi_Key = "01590a15f8f16d6015858b1424fdd3ac"
header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,'referer':'https://www.google.com/'}

# Will be used to store Property results
results_list = []

def parseContent(webSoup):
    """
    Takes in a BeautifulSoup object that has already been converted to parse webpage
    """
    if not isinstance(webSoup, BeautifulSoup):
        return
    else:
        # Get all property cards and parse through all
        properties_Container = webSoup.find_all("ul", class_="property-list")[0].find_all("li", class_="component_property-card", attrs={"data-testid":"result-card"})
        print(len(properties_Container))
        
        for prop in properties_Container:
            home = {}
            # Attempt to pull type
            try:
                home["Type"] = prop.find("div", class_="property-type", attrs={"data-label":"pc-type"}).text
            except:
                home["Type"] = None

            # Attempt to pull price and estimated payment
            priceWrapper = prop.find_all("div", attrs={"data-label":"pc-price-wrapper"}, class_="price")

            for wrap in priceWrapper:
                # pull price
                try:
                    home["Price"] = wrap.find("span", attrs={"data-label":"pc-price"}).text
                except:
                    home["Price"] = None
                # TODO: pull estimated payment
                try:
                    home["Estimate Payment"] = wrap.find("button", attrs={"estimate-payment-button"}, class_="estimate-payment-button").text
                except:
                    home["Estimate Payment"] = None
            
            # Find Home Details
            detailWrapper = prop.find("div", attrs={"data-testid":"property-meta-container"})

            # Attempt to pull Bed
            try:
                home["Beds"] = detailWrapper.find("li", attrs={"data-label":"pc-meta-beds"}).find("span", attrs={"data-label":"meta-value"}).text
            except:
                home["Beds"] = None

            # Attempt to pull baths
            try:
                home["Baths"] = detailWrapper.find("li", attrs={"data-label":"pc-meta-baths"}).find("span", attrs={"data-label":"meta-value"}).text
            except:
                home["Baths"] = None

            # Attempt to pull Home SqFt
            try:
                home["Home Square Footage"] = detailWrapper.find("li", attrs={"data-label":"pc-meta-sqft"}).find("span", attrs={"data-label":"meta-value"}).text
            except:
                home["Home Square Footage"] = None

            # Attempt to pull Lot SqFt
            try:
                home["Lot Square Footage"] = detailWrapper.find("li", attrs={"data-label":"pc-meta-sqftlot"}).find("span", attrs={"data-label":"meta-value"}).text
            except:
                home["Lot Square Footage"] = None

            # Attempt to pull address
            try:
                home["Address"] = prop.find("div", class_="address", attrs={"data-label":"pc-address"}).text
            except:
                home["Address"] = None

            # Add Date Created
            home["Created"] = datetime.datetime.now().strftime("%b-%d-%Y %I:%M:%S")
            results_list.append(home)

def requestNewURL(url):
    """
    Takes in base url to crawl through and converts into BeautifulSoup
    """
    print("Looking at webpage: %s" % url)
    
    payload = { "api_key": scraperapi_Key, "url": url }
    req = requests.get("http://api.scraperapi.com",params=payload,headers=header)
    contents = req.text.strip()
    soup = BeautifulSoup(contents, "html.parser")
    parseContent(soup)


# Start off parsing 1st page which will have some results
payload = { "api_key": scraperapi_Key, "url": realtor_base_url }
req = requests.get("http://api.scraperapi.com",params=payload,headers=header)
contents = req.text.strip()
soup = BeautifulSoup(contents, "html.parser")

# To see web content results, uncomment the following line
# print(soup.prettify())


# Parse through first page
parseContent(soup)

# Determine number of pages
try:
    max_pages = soup.find_all("li", {"class":"pagination-number"})[-1].text
    
    # if more than 1 pages loop through all
    if int(max_pages) >= 2:
        # Since range is exclusive, we need to add one to the end
        for page in range(2,int(max_pages)+1):
            if page > 1:
                # Add sleep timer to avoid clogging up requests per second
                time.sleep(2)
                requestNewURL(realtor_base_url + "/pg-" +str(page))
except IndexError:
    pass

# Create csv file with all results
dataFrame = pandas.DataFrame(results_list)
dataFrame.to_csv("%s_PropertyResults.csv" % city)