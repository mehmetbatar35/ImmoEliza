import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import csv


class Property:
    def __init__(self):

        property_list: list[str] = []


        self.cheat_immo = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)            Chrome/91.0.4472.124 Safari/537.36"
        }

        self.url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page=1&orderBy=relevance"



        self.soup = self.get_soup(self.url)
        self.property_links : list[str] = self.get_links()
        
        with open('output.json', 'w', encoding='utf-8') as f:
            f.write("[\n")
            for link in self.property_links:
                if "new-real-estate-project" in link:
                    continue
                soup  = self.get_soup(link)
                property_json = self.get_property_json(soup)
                json_formatted_str = json.dumps(property_json, indent=2)
                if link == self.property_links[-1]:
                    f.write( json_formatted_str + "\n" )
                else:
                    f.write( json_formatted_str+",\n" )

                prop_dict = {}  
                prop_dict ["Type of property"] = property_json["property"]["type"]  
                prop_dict ["Subtype of property"] = property_json["property"]["subtype"]
                prop_dict ["Locality"] = property_json["property"]["location"]["postalCode"]
                prop_dict ["Living Area"] = property_json["property"]["netHabitableSurface"]
                prop_dict ["Price"] = property_json['price']['mainValue']
                prop_dict ["Number of rooms"] = property_json['property']['bedroomCount']
                prop_dict ["Furnished"] = 1 if property_json['transaction']['sale']['isFurnished'] else 0
                prop_dict ["Terrace"] = property_json['property']['terraceSurface'] if property_json['property']['hasTerrace'] else 'No'
                prop_dict ["Garden"] = property_json['property']['gardenSurface'] if property_json['property']['hasGarden'] else 'No'
                prop_dict ["Swimming Pool"] = 1 if property_json['property']['hasSwimmingPool'] else 0
                prop_dict ["State of the building"] = property_json["property"]['building']["condition"] if property_json["property"]['building'] else None
                prop_dict ["Surface Land"] = property_json["property"]['land']["surface"] if property_json["property"]['land'] else "null"
                if property_json["property"]['kitchen'] and property_json["property"]['kitchen']['type'] != None:
                    prop_dict ["Kitchen Fully Equiped"] = 1 if "HYPER" in property_json["property"]['kitchen']['type'] else 0
                else:   
                    prop_dict ["Kitchen Fully Equiped"] = 0
                prop_dict ["Number of facades"] = property_json['property']['building']['facadeCount'] if property_json['property']['building'] else None
                prop_dict ["Open fire"] = 1 if property_json['property']['fireplaceExists'] else 0
                for index, i in enumerate(property_json['flags']):
                    if property_json['flags'][i] == True:
                        type_of_sale = i
                prop_dict ["Type of Sale"] = type_of_sale

                property_list.append(prop_dict)

                print(property_list)

                csv_file = "output.csv"
                fieldnames = property_list[0].keys()
                with open(csv_file, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in property_list:
                        writer.writerow(row)
                

            f.write("]")

    def get_soup(self, url):
        response = requests.get(url, headers=self.cheat_immo)
        soup = bs(response.content, "html.parser")
        return soup 

    def get_links(self):
        list_links = []
        maison_link_soup = self.soup.find_all('a', attrs ={"class": "card__title-link"})

        for link in maison_link_soup:
            list_links.append(link['href'])
        return list_links    
    
    def get_property_json(self, soup):
        json_link = soup.find_all("script", attrs={"type": "text/javascript"})
        for i in json_link:
            if 'window.classified' in i.text:
                i = i.text.replace("window.classified = ", "").replace(";", "")
                i = json.loads(i)
                return i
            
    def get_locality(self, json_link):
        pass

prop = Property()
