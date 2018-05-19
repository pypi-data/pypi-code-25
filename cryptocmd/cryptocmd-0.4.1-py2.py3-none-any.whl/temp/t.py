# from cryptocmd import CmcScraper

# x = CmcScraper('xrp')

# import sys
# sys.path.append("..")

from cryptocmd import CmcScraper

# initialise scraper without passing time interval
# scraper = CmcScraper('XRP')
#
# # data as list of list in a variable
# headers, data = scraper.get_data()
# print(headers)
#
# # export the data as csv file, you can also pass optional name parameter
# scraper.export_csv()
#
# # Pandas dataFrame for the same data
# df = scraper.get_dataframe()
#
# print(df.head())

scraper = CmcScraper('XRP', '01-01-2015', '10-03-2015')
df = scraper.get_dataframe()
print(df)
#
# print(df.head())
#
#
# # 1 scraper
# scraper = CmcScraper('sc', '15-10-2017', '25-10-2017')
#
# # get data as list of list
# headers, data = scraper.get_data()
#
# # export the data to csv
# scraper.export_csv()
#
# # get dataframe for the data
# df = scraper.get_dataframe()
#
#
# print(df.tail())
#
# print(df.head())
#
#
# scraper = CmcScraper('sc')
# scraper.export_csv()