# WebScraper
Purely for education and portfolio purposes - pulls home data from realtor website.

Using ScraperAPI, I built this Python program to pull data from a realtor website to view what houses are for sale without going to the webpage itself.
The data gets converted into a CSV file using Pandas for better visualization and manipulation.

To run, first run 'pip install -r requirements.txt'

(Optional) To change city location, on 'main.py' line 6 change 'city' property to whatever city you'd like, just be sure to capitalize and add a hypen between words

then run 'python main.py'

To view data, just open the file ending in '_PropertyResults.csv'

# Weekly Sold
The program is now able to pull recent sold properties in any given city in California.

Default date range is all properties sold in the past 7 days.

Run 'python WeeklySold.py' and the generated excel file is located in 'Results' Folder.

(Optional) To change city location, in 'WeeklySold.py' change 'city' property to whatever city you'd like, just be sure to capitalize and add a hypen between words
(Optional) To change how far back to pull sold properties, in 'ScraperBrain.py' change 'withinDaysSold' to how every many days you would like.

# Note:
Sometimes program may crash or unexpected error may appear. Just run again, usually does the trick.
