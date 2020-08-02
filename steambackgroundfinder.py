from selenium import webdriver
from bs4 import BeautifulSoup
import time
from datetime import datetime

start=datetime.now()
class background:
    name = ""
    link = ""
    quantity = ""
    price = ""
    saleList = list()
    appId = ""
    titleList = list()
    rarity = ""
    averageSalePrice = 0
    chance = 0
    commonCount = 0
    uncommonCount = 0
    rareCount = 0
    score = 0
    def __init__(self,name,link,quantity,price,appId):
        self.name = name
        self.link = link
        self.quantity = quantity
        self.price = price
        self.appId = appId
        
browser = webdriver.Chrome()

loginLink = "https://store.steampowered.com/login/"
browser.get(loginLink)

print("Lütfen Steam'e Giriş Yapınız. (Steam'e giriş yapmanızın nedeni, steam pazar fiyatları araştırılır iken arkaplan fiyatlarının TL cinsinden gözükmesi için steam cüzdanı oluşturulmuş bir hesap gerekmesidir. Aksi takdirde fiyatlar USD cinsinden gözükecek ve USD->TL çevirmesi esnasında hatalar olacaktır. Bu hatalar sonucu da istenen kar düzgün hesaplanamayacaktır.")
print("Steam'e giriş yaptıktan sonra lütfen konsola \"devam\" yazınız.")


cont = ""
while True:
    cont = input()
    if(cont == "devam"):
        break
    else:
        time.sleep(1)

print("\nHangi sayfadan başlamak istersiniz ?")
pageStart = int(input())
print("\nKaçıncı sayfaya kadar taramak istersiniz ?")
pageEnd = int(input())
print("\nPazarda en az kaç tane bulunan arkaplanları taramak istersiniz ?")
quantityLimit = int(input())


backgrounds = list()




print("\nArkaplanlar Taranmaya Başlıyor...")
print("\nTaratılacak sayfa sayısı " + str(pageEnd-pageStart)+"\n")

for k in range(pageStart,pageEnd+1):
    print("Çekilen arkaplan sayısı " + str(len(backgrounds)) + "\t" + str(k-pageStart) + "/" + str(pageEnd-pageStart) +" Sayfa taratıldı")
    backgroundURL  = "https://steamcommunity.com/market/search?q=&category_753_Game%5B%5D=any&category_753_item_class%5B%5D=tag_item_class_3&appid=753#p" +  str(k) +  "_price_desc"
    browser.get(backgroundURL)
    time.sleep(5)
    html_source = browser.page_source
    soup = BeautifulSoup(html_source,'html.parser')
    
    names =  soup.find_all("span", attrs={"class":"market_listing_item_name"}) # name in names : name.getText()
    links = soup.find_all("a",attrs={"class":"market_listing_row_link"}) # link in links : link.get("href")
    quantities = soup.find_all("span",attrs={"class":"market_listing_num_listings_qty"}) #quantity in quantities: quantity.getText()
    prices = soup.find_all("span",attrs={"class":"normal_price"}) # price in prices: price.get("data-price") none'lar içeriyor
    
    for price in prices:
        if str(price.get("data-price")) == "None":
            prices.remove(price)
    
    
    
    for i in range(0,len(names)):
        if int(quantities[i].getText()) >= quantityLimit:
            link = links[i].get("href")
            appId = link[link.index("753")+4:link.index("-")]
            bg = background(names[i].getText(),links[i].get("href"),quantities[i].getText(),int(prices[i].get("data-price"))/100,appId) 
            backgrounds.append(bg)
    
    
print("\nÇekilen arkaplan sayısı : "  + str(len(backgrounds)))
print("\nArkaplanların kârları hesaplanıyor...")
stcLink = "https://www.steamcardexchange.net/index.php?gamepage-appid-"
scannedBg = 0
for bg in backgrounds:
    print("\n"+str(scannedBg) + "/" + str(len(backgrounds)) + " adet arkaplanın kârı hesaplandı.")
    try:
        time.sleep(2)
        link = bg.link
        browser.get(link)
        html_source = browser.page_source
        soup = BeautifulSoup(html_source,'html.parser')
        scripts = soup.find_all("script",attrs={"type":"text/javascript"})
        
        scriptsStr = str(scripts)
        scriptsStr = scriptsStr[scriptsStr.index("var line1=")+10:]
        sales = scriptsStr[:scriptsStr.index(";")]
        sales = sales[2:len(sales)-2]
        saleList = sales.split("],[")
        bg.saleList = saleList
        

    except:
        bg.saleList = list()
        continue
  
    browser.get(stcLink+bg.appId)
    html_source = browser.page_source
    soup = BeautifulSoup(html_source,'html.parser')
    element_experience = soup.find_all("a",attrs={"class":"element-image"})
    
    titleList = list()
    for title in element_experience:
        
        titleStr = str(title.get("title")[title.get("title").index("Type:")+6:])
        titleStr = titleStr[:titleStr.index(" ")]
        titleList.append(titleStr)
        
        name = bg.name
        if "(Profil Arka Planı)" in name:
            name = name[:name.index("(Profil Arka Planı)")]
    
        if name in title.get("title"):
            bg.rarity = titleStr
    bg.titleList = titleList
    scannedBg += 1

browser.close()  
    

print("\nKarlar hesaplanıp excel dosyasına aktarılıyor...")
for bg in backgrounds:
    try:
        commonCount = 0
        uncommonCount = 0
        rareCount = 0
        
        for title in bg.titleList:
            if title == "Common":
                commonCount += 1
            elif title == "Uncommon":
                uncommonCount += 1
            elif title == "Rare":
                rareCount += 1
                
        bg.commonCount = commonCount
        bg.uncommonCount = uncommonCount
        bg.rareCount = rareCount
       
        priceCount = 0 
        totalPrice = 0
        for price in bg.saleList:
            if "2020" in price:
                price = price[price.index(",")+1:]
                price = price[:price.index(",")]
                totalPrice += float(price)
                priceCount += 1
        
        averageSalePrice = totalPrice / priceCount
        bg.averageSalePrice = averageSalePrice
    except:
        averageSalePrice = 0;
        bg.averageSalePrice = averageSalePrice
        continue
    
    
for bg in backgrounds:
    chance = 0
    if bg.rarity == "Common":
        chance = 64/bg.commonCount
    elif bg.rarity == "Uncommon":
        chance = 23/bg.uncommonCount
    elif bg.rarity == "Rare":
        chance = 13/bg.rareCount
    
    bg.chance = chance
    bg.score = bg.chance * bg.averageSalePrice
    
import operator
backgrounds = sorted(backgrounds, key=operator.attrgetter('score'))
backgrounds = list(reversed(backgrounds))


from xlwt import Workbook 
wb = Workbook() 

backgroundSheet = wb.add_sheet("Backgrounds")
backgroundSheet.write(0,0,"Name")
backgroundSheet.write(0,1,"Rarity")
backgroundSheet.write(0,2,"Price")
backgroundSheet.write(0,3,"Average Sale Price")
backgroundSheet.write(0,4,"Chance")
backgroundSheet.write(0,5,"Score")
backgroundSheet.write(0,6,"Quantity")
backgroundSheet.write(0,7,"Link")

sayi = 1
for bg in backgrounds:
    backgroundSheet.write(sayi,0,bg.name)
    backgroundSheet.write(sayi,1,bg.rarity)
    backgroundSheet.write(sayi,2,bg.price)
    backgroundSheet.write(sayi,3,bg.averageSalePrice)
    backgroundSheet.write(sayi,4,bg.chance)
    backgroundSheet.write(sayi,5,bg.score)
    backgroundSheet.write(sayi,6,bg.quantity)
    backgroundSheet.write(sayi,7,bg.link)
    sayi += 1


wb.save('ProfitableBackgrounds.xls')

print("\nToplam " + str(len(backgrounds)) + " adet arkaplan tarandı ve excel dosyasına aktarıldı.. Lütfen kontrol ediniz.")
print("\nToplam Geçen Süre : "  + str((datetime.now()-start)))