"""

SCRAPE AFLTABLES.COM for the Rugby Leagu results

--- igor k. 07DEC2016 ---

"""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from collections import defaultdict

# choose the range of years you are interested in; the earliest available year is 1897
y_from = 1981
y_to = 2016

"""
choose what format to save data in:
	0 : don't save at all, just show first 10 rdata ows on screen
	1 : save as a table in .CSV 
	2 : save as a JSON file
"""
save_flag = 1

# want to see yearly counts for the retrieved records? 1 for yes

show_yrecs = 1

# sanity check

assert y_from > 1907, ("sorry, there\'s no data for earliest year {} that you\'ve picked." 
						"you may want to choose another year from 1908 and on..".format(y_from))
assert y_to < 2017, ("sorry, there\'s no data for last year {} that you\'ve picked." 
						"you may want to choose another year before 2017..".format(y_to))
assert y_from <= y_to, ("no, this won\'t work. make sure that the earliest year you pick is before or equal to the last year...")

# show this 
print("""-------> scraping afltables.com""")
# lists to store the scraped data
list_rounds = []
list_round_att = []
list_total_att = []
list_team_1 = []
list_team_2 = []
list_score_1 = []
list_score_2 = []
list_dates = []
list_att = []
list_venues = []

# lists to keep quarterly scores
list_hscore_1 = []
list_hscore_2 = []

# stats per year
statsy = defaultdict(lambda: defaultdict(int))

for year in range(y_from, y_to + 1):
	
	print("downloading data for", year, "...", end="")

	season_line = "http://afltables.com/rl/seas/" + str(year) +".html"
	
	page = requests.get(season_line)
	
	if page.status_code == 200:
		print("ok")
	else:
		print("error {}!".format(year))

	# create a soup object
	soup = BeautifulSoup(page.content, 'html.parser')

	def is_match(tb):

		if ((len(tb.find_all("tr")) == 2) and (len(tb.find_all("td")) == 8) and 
				tb.has_attr("border") and
					 (tb["border"] == "2")):
			return True
		else:
			return False

	#
	# is this tag a table that sits right on top of the match result tables
	# 
	def is_round(tb):

		if (tb.has_attr("border") and 
				tb["border"] == "2" and
			 		len(tb.find_all("th")) == 1):
			return True
		else:
			return False

	mtb = 0

	for i, this_header_tbl in enumerate(soup.find_all("table")):

		if is_round(this_header_tbl):

			statsy[year]["number_rounds"] += 1

			this_round = this_header_tbl.find_all("th")[0].text.strip().lower()

		if is_match(this_header_tbl):

			
			statsy[year]["number_games"] += 1

			list_rounds.append(this_round)

			team1_tr, team2_tr = this_header_tbl.find_all("tr")

			# now find all cells for each row
			team1_tds = team1_tr.find_all("td")
			team2_tds = team2_tr.find_all("td")
			
			for i in range(len(team1_tds)):
				if i == 0:
					list_team_1.append(team1_tds[i].text.strip())
					list_team_2.append(team2_tds[i].text.strip())
				if i == 1:
					list_hscore_1.append(team1_tds[i].text.strip())
					list_hscore_2.append(team2_tds[i].text.strip())
				if i == 2:
					list_score_1.append(team1_tds[i].text.strip())
					list_score_2.append(team2_tds[i].text.strip())
				if i == 3:
					all_bs1 = team1_tds[i].find_all("b")  # expect to have 3: date, venue and crowd
					list_dates.append(all_bs1[0].next_sibling.strip())
					list_venues.append(all_bs1[1].next_sibling.text.strip())
					list_att.append(all_bs1[2].next_sibling.strip())


# now combine eerything into a zip
data = zip(list_rounds, list_dates, list_team_1, 
				list_hscore_1, list_score_1,
				 list_team_2, list_hscore_2, list_score_2, list_venues, list_att)


# put the data into a pandas data frame
df = pd.DataFrame(columns="round date team1 t1h t1score team2 t2h t2score venue attendance".split())

for i, row in enumerate(data):
	df.loc[i] = row

print("successfully retrieved {} results..".format(len(df.index)))

if show_yrecs:
	df_statsy = pd.DataFrame.from_dict(statsy)
	print(df_statsy)

if save_flag == 0:

	print(df.head(10))

elif save_flag == 1:

	if y_from != y_to:
		csv_fl = "scraped_data_from_afltables_rugby_yrs_" + str(y_from) + "_to_" + str(y_to) + ".csv"
	else:
		csv_fl = "scraped_data_from_afltables_rugby_" + str(y_from) + ".csv"

	df.to_csv(csv_fl, index=False)
elif save_flag == 2:

	if y_from != y_to:
		csv_fl = "scraped_data_from_afltables_rugby_yrs_" + str(y_from) + "_to_" + str(y_to) + ".json"
	else:
		csv_fl = "scraped_data_from_afltables_rugby_" + str(y_from) + ".json"
	df.to_json(csv_fl, orient='records')


print("done. saved the scraped data to file {} in your current directory..".format(csv_fl))






