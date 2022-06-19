import pandas
import time, os
from ScraperBrain import *
from Network import *

"""
Change City below to any city with hypen in between words
"""
city = "San Leandro"
realtor_base_url = f"https://www.realtor.com/realestateandhomes-search/{city}_CA/show-recently-sold"

# Initialize Network to gather data
soldNetwork = Network(realtor_base_url)

# Start off parsing 1st page which will have some results

# Get Base Home Page Data
soup = soldNetwork.getPageData(soldNetwork.baseUrl)

# Initialize new ScaperBrain
soldScraperBrain = ScraperBrain(soup)

# Parse through first page
soldScraperBrain.parseSoldContent(soldScraperBrain.webSoup)
# print(soldScraperBrain.results_list)

# Determine number of pages
try:
    soldScraperBrain.max_Pages = soup.find("div", {"role":"navigation"}).select("a.item, a.btn")[-2].text
    print(f"Total Number of pages {soldScraperBrain.max_Pages}")
    
    # if more than 1 pages loop through all
    if int(soldScraperBrain.max_Pages) >= 2:
        # Since range is exclusive, we need to add one to the end
        for page in range(2,int(soldScraperBrain.max_Pages)+1):
            if not soldScraperBrain.lastHouseFound:
                time.sleep(1)
                newContent = soldScraperBrain.requestNewURL(soldNetwork, realtor_base_url + "/pg-" +str(page))
                soldScraperBrain.parseSoldContent(newContent)
            else:
                print("Last weekly house found.")
                break
except IndexError:
    print("Index Error occurred, Data may be missing.")
    pass

print(f"Total number of successful pulled Properties: {len(soldScraperBrain.results_list)}")

# Create csv file with all results
dataFrame = pandas.DataFrame(soldScraperBrain.results_list)
results_filename = f"{city}_SoldPropertyResults.csv"

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
print(f"File is located at: {os.path.abspath(results_filename)}")

# Go back to previous directory
if os.path.exists("Results"):
    os.chdir("..")