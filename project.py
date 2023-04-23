from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import time
import warnings
from pymongo import MongoClient
import requests
import re
import json

warnings.simplefilter('ignore')

cu_path = os.getcwd()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56'}

client = MongoClient('localhost', 27017)

def q4():
  try:
    SEARCH = "Pizzeria"
    PLACE = "San+Francisco%2C+CA"
    URL = f"https://www.yellowpages.com/search?search_terms={SEARCH}&geo_location_terms={PLACE}"
    session_requests = requests.session()
    page1 = session_requests.get(URL , headers = headers)
    doc2 = BeautifulSoup(page1.content, 'lxml')
    with open(f"sf_pizzeria_search_page.htm", "w", encoding = 'utf-8') as file:
      file.write(str(doc2.prettify()))
  except:
    print("error")


def q5_q6():
  mydatabase = client['sf_pizzerias']
  mycollection = mydatabase['sf_pizzerias']
  mycollection.drop()
  #q5
  with open("sf_pizzeria_search_page.htm" , "r" , encoding = 'utf-8') as f:
    contents = f.read()
    soup = BeautifulSoup(contents, 'lxml')
    data = soup.select("div.scrollable-pane > div.search-results.organic")[0]
    data = data.select("div.result")
    for each in data:
      search_rank = re.sub(r"(\s{1,}|\n)([0-9]+)(\s|\n|.)*" , r"\2",each.find("h2",{"class" : "n"}).text)
      name = re.sub(r"([\n\t\s]+?)([.]*)([\n\t\s]+?)" , r"\2",each.find("span").text)
      url = "https://www.yellowpages.com" + each.find("a",{"class" : "business-name"}).get('href')
      try:
        star_rating = each.find("a",{"class" : "rating hasExtraRating"}).div["class"][1:]
        star_rating = " ".join(star_rating)
      except:
        star_rating = ""
      try:
        num_reviews = each.find("span",{"class" : "count"}).text
        num_reviews = re.sub(r"(\s{1,}|\n|\()*([0-9]+)*(\s|\n|.|\))*" , r"\2",num_reviews)
      except:
        num_reviews = ""
      try:
        trip_advisor_rating = json.loads(each.find("div",{"class" : "ratings"}).get("data-tripadvisor"))["rating"]
      except:
        trip_advisor_rating = ""
      try:
        num_TA_reviews = json.loads(each.find("div",{"class" : "ratings"}).get("data-tripadvisor"))["count"]
      except:
        num_TA_reviews = ""
      try:
        dollar_m = each.find("div",{"class" : "price-range"}).text
        dollar_m = re.sub(r"(\s{1,}|\n|\()*([\$]+)*(\s|\n|.|\))*" , r"\2",dollar_m)
      except:
        dollar_m = ""
      try:
        business_years = each.find("div",{"class" : "number"}).text
        business_years= re.sub(r"(\s{1,}|\n|\()*([0-9]+)*(\s|\n|.|\))*" , r"\2",business_years)
      except:
        business_years = ""
      try:
        reviews = each.find("p",{"class" : "body with-avatar"}).text
        reviews = re.sub(r"([\n\t\s]+?)([.]*)([\n\t\s]+?)" , r"\2",reviews)
      except:
        reviews = ""
      try:
        amenities_list = []
        amenities = each.find("span",{"class" : "amenities-icons"}).find_all("use")
        for ame in amenities:
          ame = ame.get("xlink:href")
          ame = ame.replace("#icon-amenity-","")
          amenities_list.append(ame)
      except:
        amenities = []
      #q6
      q6_json = {}
      q6_json["search_rank"] = search_rank
      q6_json["name"] = name
      q6_json["url"] = url
      q6_json["star_rating"] = star_rating
      q6_json["num_reviews"] = num_reviews
      q6_json["trip_advisor_rating"] = trip_advisor_rating
      q6_json["num_TA_reviews"] = num_TA_reviews
      q6_json["dollar_m"] = dollar_m
      q6_json["business_years"] = business_years
      q6_json["reviews"] = reviews
      q6_json["amenities"] = amenities_list
      mycollection.insert_one(q6_json)


def q7():
  mydatabase = client['sf_pizzerias']
  mycollection = mydatabase['sf_pizzerias']
  df = mycollection.find()
  for each in df:
    time.sleep(3)
    each_url = each["url"]
    rank = each["search_rank"]
    page = requests.get(each_url , headers = headers)
    soup = BeautifulSoup(page.text, 'lxml')
    with open(f"sf_pizzerias_{rank}.htm", "w", encoding = 'utf-8') as file:
      file.write(str(soup.prettify()))


def q8_q9():
  #q8
  for i in range(1,31):
    file_name = f"sf_pizzerias_{i}.htm"
    with open(file_name , "r" , encoding = 'utf-8') as f:
      contents = f.read()
      soup = BeautifulSoup(contents, 'lxml')
      data = soup.find("section",{"id" : "details-card"})
      try:
        phone = data.find("p",{"class" : "phone"}).text
        phone = re.sub(r"([\n\t\s]*)(Phone:)([\n\t\s]*)([-\(\)0-9]*?)([\n\t\s]*)" , r"\4",phone)
        phone = re.sub("\n","",phone)
        phone = re.sub("\s","",phone)
      except:
        phone = ""
      try:
        address = data.find_all("p")[1]
        address = address.text
        address = re.sub(r"(\s{1,}|\n)*(Address:)(\s{1,}|\n)*([-\(\)0-9\s]+)*?(\s{1,}|\n)*" , r"\4",address)
      except:
        address = ""
      try:
        website = data.find("p",{"class" : "website"}).find("a").get("href")
      except:
        website = ""
      print("Phone number : " , phone)
      print("address : " , address)
      print("website : " , website)
      # q9
      time.sleep(3)
      try:
        api_key = "1b50f6423a5a497abf8669f16dcb0aaf"
        request_url = f"http://api.positionstack.com/v1/forward?access_key={api_key}&query={address}"
        response_page = requests.get(request_url, headers=headers)
        doc = BeautifulSoup(response_page.content, 'html.parser')
        json_data = json.loads(str(doc))
        latitude = json_data["data"][0]["latitude"]
        longitude = json_data["data"][0]["longitude"]
      except:
        latitude = ""
        longitude = ""
      mydatabase = client['sf_pizzerias']
      mycollection = mydatabase['sf_pizzerias']
      mycollection.update_one(
        {"search_rank" : str(i)},
         {"$set" : {"shop's address" : address,
                    "phone_number" : phone,
                    "website" : website,
                    "latitude" : latitude,
                    "longitude" : longitude}}
      )

if __name__ == '__main__':
  q4()
  q5_q6()
  q7()
  q8_q9()