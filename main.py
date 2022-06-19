import pandas
import requests
from bs4 import BeautifulSoup
import time, datetime, os

city = "San-Leandro"
realtor_base_url = "https://www.realtor.com/realestateandhomes-search/%s_CA/radius-10" % city
scraperapi_Key = "01590a15f8f16d6015858b1424fdd3ac"
header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,'referer':'https://www.google.com/'}

# Will be used to store Property results
results_list = []

def parseContent(webSoup, find_Number_of_Properties = False):
    """
    Takes in a BeautifulSoup object that has already been converted to parse webpage and a boolean value to determine if looking for max number of properties to display
    """
    if not isinstance(webSoup, BeautifulSoup):
        raise ValueError("webSoup must be of type 'BeatifulSoup'")
    elif not isinstance(find_Number_of_Properties, bool):
        raise ValueError("find_Number_of_Properties must be of type 'bool'")
    else:
        # If find_Number_of_Properties is True, look for total number of houses
        if find_Number_of_Properties:
            try:
                home_count_Container = webSoup.find("span", class_="result-count")
                print("Total: %s" % home_count_Container.text)
            except Exception as ex:
                print("Error determing property count")
                raise ex

        # Get all property cards and parse through all
        try:
            properties_Container = webSoup.find_all("section", class_="srp-content")[0].find_all("li", attrs={"data-testid":"result-card"}, class_="component_property-card")
            print("Number of properties on this page: %s" % len(properties_Container))
        except Exception as ex:
            print("%s Error occured initializing properties_container: %s" % (type(ex),ex))
             # Return False to retry URL
            return False
        
        for prop in properties_Container:
            home = {}
            # Attempt to pull type
            try:
                home["Type"] = prop.find("div", class_="property-type", attrs={"data-label":"pc-type"}).text
            except AttributeError:
                home["Type"] = None
                pass
            except Exception as ex:
                print("%s Error occured in Type: %s" % (type(ex),ex))
                home["Type"] = None

            # Attempt to pull price and estimated payment
            try:
                priceWrapper = prop.find_all("div", attrs={"data-label":"pc-price-wrapper"}, class_="price")
            except Exception as ex:
                print("%s Error occured initializing priceWrapper: %s" % (type(ex),ex))
                return

            for wrap in priceWrapper:
                # pull price
                try:
                    home["Price"] = wrap.find("span", attrs={"data-label":"pc-price"}).text
                except AttributeError:
                    home["Price"] = None
                    pass
                except Exception as ex:
                    print("%s Error occured in Price: %s" % (type(ex),ex))
                    home["Price"] = None
                # TODO: pull estimated payment
                # try:
                #     home["Estimate Payment"] = wrap.find("button", attrs={"estimate-payment-button"}, class_="estimate-payment-button").text
                # except Exception as ex:
                #     print("Error occured in Estimate Payment: %s" % ex)
                #     home["Estimate Payment"] = None
            
            # Find Home Details
            try:
                detailWrapper = prop.find("div", attrs={"data-testid":"property-meta-container"})
            except: 
                print("%s Error occured initializing detailWrapper: %s" % (type(ex),ex))
                return
            # Attempt to pull Bed
            try:
                home["Beds"] = detailWrapper.find("li", attrs={"data-label":"pc-meta-beds"}).find("span", attrs={"data-label":"meta-value"}).text
            except AttributeError:
                home["Beds"] = None
                pass
            except Exception as ex:
                print("%s Error occured in Bed: %s" % (type(ex),ex))
                home["Beds"] = None

            # Attempt to pull baths
            try:
                home["Baths"] = detailWrapper.find("li", attrs={"data-label":"pc-meta-baths"}).find("span", attrs={"data-label":"meta-value"}).text
            except AttributeError:
                home["Baths"] = None
                pass
            except Exception as ex:
                print("%s Error occured in Baths: %s" % (type(ex), ex))
                home["Baths"] = None

            # Attempt to pull Home SqFt
            try:
                home["Home Square Footage"] = detailWrapper.find("li", attrs={"data-label":"pc-meta-sqft"}).find("span", attrs={"data-label":"meta-value"}).text
            except AttributeError:
                home["Home Square Footage"] = None
                pass
            except Exception as ex:
                print("%s Error occured in Home Square Footage: %s" % (type(ex), ex))
                home["Home Square Footage"] = None

            # Attempt to pull Lot SqFt
            try:
                home["Lot Square Footage"] = detailWrapper.find("li", attrs={"data-label":"pc-meta-sqftlot"}).find("span", attrs={"data-label":"meta-value"}).text
            except AttributeError:
                home["Lot Square Footage"] = None
                pass
            except Exception as ex:
                print("%s Error occured in Lot Square Footage: %s" % (type(ex), ex))
                home["Lot Square Footage"] = None

            # Attempt to pull address
            try:
                home["Address"] = prop.find("div", class_="address", attrs={"data-label":"pc-address"}).text
            except AttributeError:
                home["Address"] = None
                pass
            except Exception as ex:
                print("%s Error occured in Address: %s" % (type(ex),ex))
                home["Address"] = None

            # Add Date Created
            try:
                home["Created"] = datetime.datetime.now().strftime("%b-%d-%Y %I:%M:%S")
            except Exception as ex:
                print("%s Error occured in Created: %s" % (type(ex),ex))
                home["Created"] = "Unavailable"
            
            results_list.append(home)

        return True

def requestNewURL(url):
    """
    Takes in base url to scrape through and converts into BeautifulSoup
    """
    print("Looking at webpage: %s" % url)
    
    payload = { "api_key": scraperapi_Key, "url": url }
    req = requests.get("http://api.scraperapi.com",params=payload,headers=header)

    if req.status_code != 200:
        print("STATUS CODE FOR %s : %s" % (url, req.status_code))
    if req.status_code == 500:
        print("Request error 500. Trying again")
        req = requests.get("http://api.scraperapi.com",params=payload,headers=header)
    
    contents = req.text.strip()
    soup = BeautifulSoup(contents, "html.parser")
    if not parseContent(soup, False):
        # something went wrong getting property container. Try URL again.
        print("Trying URL Again")
        requestNewURL(url)


# Start off parsing 1st page which will have some results
payload = { "api_key": scraperapi_Key, "url": realtor_base_url }
req = requests.get("http://api.scraperapi.com",params=payload,headers=header)
contents = req.text.strip()
soup = BeautifulSoup(contents, "html.parser")

# To see web content results, uncomment the following line
# print(soup.prettify())


# Parse through first page
parseContent(soup, True)

# Determine number of pages
try:
    max_pages = soup.find("div", {"role":"navigation"}).select("a.item, a.btn")[-2].text
    print("Total Number of pages %s" % max_pages)
    
    # if more than 1 pages loop through all
    if int(max_pages) >= 2:
        # Since range is exclusive, we need to add one to the end
        for page in range(2,int(max_pages)+1):
            time.sleep(2)
            requestNewURL(realtor_base_url + "/pg-" +str(page))
except IndexError:
    print("Index Error occurred, Data may be missing.")
    pass

# Website has now changed, need to loop while Next button is active
# Increment count manually
# try:
#     navigation = soup.find("div", {"role":"navigation"}).select("a.item, a.btn")[-2].text
#     print(navigation)
# except AttributeError:
#     print("Error finding elements")

print("Total number of successful pulled Properties: %s" % len(results_list))
# Create csv file with all results
dataFrame = pandas.DataFrame(results_list)
results_filename = "%s_PropertyResults.csv" % city

if not os.path.exists("Results"):
    try:
        os.mkdir("Results")
    except OSError:
        # Save results file in current directory
        results_path = os.getcwd()
    else:
        # Save Results to Results directory")
        results_path = os.path.abspath("Results")
        os.chdir("Results")
else: 
    # Results directory already exists
    results_path = os.path.abspath("Results")
    os.chdir("Results")

dataFrame.to_csv(results_path + "/" + results_filename)
print("File is located at: %s" % os.path.abspath(results_filename))

# Go back to previous directory
if os.path.exists("Results"):
    os.chdir("..")
