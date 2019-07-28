import bs4 as bs
import urllib.request
import pandas as pd
import pickle
import csv

source = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_One_Day_International_cricketers').read()

soup=bs.BeautifulSoup(source,'lxml')
# print(soup.prettify())
countries=[]
spans = soup.find_all('span', {'class': 'mw-headline'})

for span in spans:
    countries.append(span.string)
	
body=soup.body
dict={}
players=['ODI Players']
count=-2

# Extracting Players Name
 
for paragraph in body.find_all('p'):
    count+=1
    if count<0:
        continue
    dict[countries[count]]=[]
    # print(count)

    for x in paragraph.text.split('\n')[:-1]:
        text1=x.split('·')[0].lstrip().rstrip()
        players.append(text1)
        dict[countries[count]].append(text1)			#dict contains Players Name country-wise
players=pd.DataFrame(players)
# players.to_csv('Players_sno.csv',header=False)		# For Serial Number
players.to_csv('Players.csv',header=False,index=False)		

# Extracting runs
# Year Range 1970:2019
years=[]
start=1970
players2={}
players2['country']={}
while start<=2019:
	years.append(start)
	players2[start]={}
	start+=1
for year in years:
	print(year)
	page=0
	while(page<1000):
		page+=1
		link='http://stats.espncricinfo.com/ci/engine/stats/index.html?class=2;page={};spanmax1=31+Dec+{};spanmin1=01+Jan+{};spanval1=span;template=results;type=batting'.format(page,year,year)
		dfs=pd.read_html(link,header=0)
		data_present=0
		for df in dfs:
			if 'Player' in df:
				# print(df[['Player','Runs']])
				for y in df['Player']:
					y1=y.split('(')[0].strip()
					y2=y.split('(')[1].split(')')[0].strip()
					a=df[df['Player']==y]['Runs']
					players2['country'][y1]=y2		# Country name for player
					try:
						players2[year][y1]=int(a)	# Runs for Player
					except:
						pass
				data_present=1
		# print(page,data_present)
		if(data_present==0):			# Checking if Data is there in last extraction, if not the jump to next year
			break

file=open("Runs.pickle","wb")
pickle.dump(players2,file)

csv_file = "temp.csv"	
csv_columns=players2['country'].keys()

# Writing Data to csv

try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for scores in players2:
            writer.writerow(players2[scores])
except IOError:
    print("I/O error") 

data=pd.read_csv('temp.csv')

# Adding the headings and rearranging the Data

data['Players']='Country'
count=0	
for year in years:
    count+=1
    data['Players'][count]=year
cols = data.columns.tolist()
cols = cols[-1:] + cols[:-1]
data=data[cols]
d={}
runs=0
data.to_csv('Runs_yearwise.csv',index=False)	
data_new=(data.transpose())
data_new.to_csv('Runs_Playerwise.csv', header=False)

# Cumulating runs

for x in data:
	runs=0
	d[x]={}
	for year in years:
		if(x=='Players'):
			runs=0
		try:
			runs+=int(data[data['Players']==year][x])
		except:
			pass
		d[x][year]=runs
	# print(runs)

data_new=pd.read_csv('Runs_Playerwise.csv')
cumulative_data=pd.DataFrame(d)
cumulative_data.transpose().to_csv('Cumulative_Runs.csv',header=False)