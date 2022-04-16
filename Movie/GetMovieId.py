import requests

from bs4 import BeautifulSoup


web = 'http://www.vscinemas.com.tw/vsweb/theater/detail.aspx?id=22'
url = requests.get(web)
soup = BeautifulSoup(url.text, "html.parser")

t = soup.select("div.theaterStory option")
id_temp = ""

for s in t:
    if s["value"] != "" :
        id_temp += s.text + "," + s["value"] + "\n"
        
with open("D:/LineBot/Movie/movie_id.csv", "w") as file:
    file.write(id_temp )
  