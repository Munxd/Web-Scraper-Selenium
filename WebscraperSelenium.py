import csv
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
import time
import logging



LOG_FILE="trakel.log"
logger = logging.getLogger(__name__)
logging.basicConfig(filename=LOG_FILE, 
                    encoding='utf-8', 
                    level=logging.INFO,  
                    filemode="w", 
                    format='%(asctime)s %(levelname)-4s %(message)s')



homePage = "https://www.trakel.org/kelebekler/?fsx=2fsdl5@d"


userAgents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/135.0.3179.98"
]
chromeOptions = Options()


randomUserAgent = random.choice(userAgents)
chromeOptions.add_argument(f"--user-agent={randomUserAgent}")


driver = webdriver.Chrome(options=chromeOptions)

def visit(path, interval=0):
    driver.get(path)
    if(interval > 0 ):
        time.sleep(5)

def navigateHome():
   
    visit(homePage)
    
def getCategories():
    
    categories = []
    
  
    selectList = driver.find_element(By.NAME,"sc")
    
    
    button =driver.find_element(By.XPATH,"//input[@type='submit']")   
    
    
    index = 0
        
   
    for option in selectList.find_elements(By.TAG_NAME,"option"):
        index = index + 1
        
        if (index < 3 ):
            continue
        
        
        category = {
            "CatId": index,
            "Name": option.text,
            "URL": "https://www.trakel.org/kelebekler/?fsx=2fsdl5%40d&sc="+ urlEncode(option.text) +"&sc_1=0&sc_2=4&sc_3=&Submit=Listele"
        }

        categories.append(category)
        
    dictToCSV("categories.csv", categories, ["CatId", "Name", "URL"])
    
    return categories
    

def dictToCSV(fileName, dict, fieldNames):
    with open(fileName, mode="w", newline="", encoding="utf-8") as file:
        
        writer = csv.DictWriter(file, fieldnames=fieldNames)
        writer.writeheader()
        
        writer.writerows(dict)    
        
def urlEncode(query):
    return urllib.parse.quote(query)        


def getPages(category):
    tempPages=[]

   
    pageList = driver.find_elements(By.XPATH,"//a[contains(@href,'sc_1=0') and not(contains(text(),'sonraki'))]")
    if ( len(pageList) == 0 ):
        return tempPages
    
    
    pindex = 1
    for p in pageList:
        purl = p.get_attribute('href')
        page = {
                "PageId": pindex,
                "CatId": category['CatId'],
                "CatName" : category['Name'],
                "URL": purl,
                "Count": len(pageList)
        }
        
        
        tempPages.append(page)
        
        pindex = pindex + 1    

    return tempPages


def getLinks(page):
    tempButterflyLinks=[]

    
    butterflyLinks = driver.find_elements(By.XPATH,"//a[contains(@href,'idx=')]")
    if ( len(butterflyLinks) == 0 ):
        return tempButterflyLinks
    
    
    for b in butterflyLinks:
        burl = b.get_attribute('href')
        
        
        smallImg =  b.find_element(By.XPATH,"./img")
        smallImgURL = smallImg.get_attribute("src")
        
        butterflyLink = {
                "LinkId" : getURLParameter(burl,"idx"),
                "PageId": page['PageId'],
                "CatId": page['CatId'], 
                "CatName" : page['CatName'], 
                "URL": burl,
                "SmallImgURL" : smallImgURL
        }
        
       
        tempButterflyLinks.append(butterflyLink)
        
    return tempButterflyLinks


def addLog(msg,printValue: bool=True):
    logger.info(msg)
    if(printValue):
        print(msg)
        

def ordinal(n):
    suffix = ["th", "st", "nd", "rd"]
    num = int(n)
    if num % 10 in [1, 2, 3] and num not in [11, 12, 13]:
        return str(num) + suffix[num % 10]
    else:
        return str(num) + suffix[0]


def getURLParameter(url,key):
    res = urllib.parse.parse_qs(url.split("?")[1])
    value = res.get(key)
    return value[0]
 

navigateHome()


categories = getCategories()
addLog(str(len(categories)) + " categories was found")
addLog("--------------------------------------")



pages=[]
for category in categories:
  addLog(category['Name'] + " is exploring...")
  visit(category['URL'], 5)
  

  tempPages = getPages( category )
  pageCount = len(tempPages)
  if( pageCount > 0 ):
      msg = ("One page was found" if pageCount == 1 else str(pageCount) + " pages were found")
      addLog(msg)
      pages.extend(tempPages)
  else:
      addLog("No pages were found")
  
  addLog("Operation was completed")
  addLog("--------------------------------------")
 

dictToCSV("pages.csv", pages, ["PageId", "CatId", "CatName", "URL", "Count"])



current = -1
links=[]
for page in pages:

    if ( current != page['CatId']):
        addLog("Butterfly links of " + page['CatName'] + " are exploring...")
        current = page['CatId']
    
    addLog(ordinal(page['PageId']) + " page is visiting")
    visit(page['URL'], 5)
    
    tempLinks = getLinks(page)
    linkCount = len(tempLinks)
    if( linkCount > 0 ):
        msg = ("One link was found" if linkCount == 1 else str(linkCount) + " links were found")
        addLog(msg)
        links.extend(tempLinks)
    else:
        addLog("No links were found")
    
  
    if(page['Count'] == page['PageId']):
        addLog("--------------------------------------")
      

dictToCSV("links.csv", links, ["LinkId", "PageId", "CatId", "CatName", "URL", "SmallImgURL"])



details = []

for link in links:
    addLog(ordinal(link['LinkId']) + " link is visiting")
    visit(link['URL'], 10)


    try:
        table = driver.find_element(By.XPATH, "//table[@width='100%']")
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        detaylar_list = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                label = cols[0].text.strip()
                value = cols[2].text.strip() 
                detaylar_list.append(f"{label}: {value}")


        
        detay_str = " | ".join(detaylar_list)
        
        detail = {
            "PageId": link['PageId'],
            "CatId": link['CatId'],
            "CatName": link['CatName'],
            "URL": link['URL'],
            "Detaylar": detay_str
        }

        details.append(detail)
    
    except Exception as e:
        logger.error(f"Error while parsing detail for {link['URL']}: {str(e)}")
        continue



dictToCSV("details.csv", details, ["PageId", "CatId", "CatName", "URL", "Detaylar"])



with open("details.csv", mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["PageId", "CatId", "CatName", "URL", "Detaylar"])

    for detail in details:
        detaylar_raw = detail["Detaylar"]
        key_value_pairs = []
        
        for pair in detaylar_raw.split(" | "):
            if ":" in pair:
                key, value = pair.split(":", 1)
                key_value_pairs.append(f"{key.strip()}: {value.strip()}")
        
        detaylar_clean = " | ".join(key_value_pairs)

        writer.writerow([
            detail["PageId"],
            detail["CatId"],
            detail["CatName"],
            detail["URL"],
            detaylar_clean
        ])


time.sleep(5)
driver.quit()
