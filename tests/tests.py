import requests

from  bs4 import BeautifulSoup
from  markdownify import markdownify

print("Sending Request")

response = requests.get(
    'https://discordpy.readthedocs.io/en/latest/api.html'
    ).text

print("Parsing HTML")
soup = BeautifulSoup(response, "lxml")

id_ = "discord.Member"

all_data = [i for i in soup.findAll(
    "dl", attrs={"class": "class"}
    ) if i.find(
        "dt", attrs={"id": id_}
        )][0]


class_name = all_data.find("dt").contents
class_name_formatted = ""
for i in class_name: 
    class_name_formatted += str(i)
class_name = markdownify(class_name_formatted)

print(class_name)