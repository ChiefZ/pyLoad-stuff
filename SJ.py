from module.plugins.Hook import Hook 
import feedparser, re, urllib, httplib, codecs
from module.network.RequestFactory import getURL 
from BeautifulSoup import BeautifulSoup
import smtplib
import pycurl

def getSeriesList(file):
    titles = []
    f = codecs.open(file, "rb", "utf-8")
    for title in f.read().splitlines():
        title = title.replace(" ", ".")
        titles.append(title)
    f.close()
    return titles 
    
def notify(title, message, api):
    data = {"token":"aBGPe78hyxBKfRawhuGbzttrEaQ9rW","user":api,"message":message,"title":title}
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json", urllib.urlencode(data), { "Content-type": "application/x-www-form-urlencoded" })
    result = conn.getresponse()
    
def send_mail(text):
    """Tested with googlemail.com and bitmessage.ch. It should work with all mailservices which provide SSL access.""" 
    serveraddr = ''
    serverport = '465'
    username = ''
    password = ''
    fromaddr = ''
    toaddrs  = ''
    
    if toaddrs == "":
        return

    subject = "pyLoad: Package added!"
    msg = "\n".join(text)

    header = "To: %s\nFrom:%s\nSubject:%s\n" %(toaddrs,fromaddr,subject)
    msg = header + "\n" + msg

    server = smtplib.SMTP_SSL(serveraddr,serverport)
    server.ehlo()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
    
def notifyPushbullet(apikey,text):
    if apikey == "0" or apikey == "":
        return
    postData =  '{"type":"note", "title":"pyLoad: Package added!", "body":"%s"}' %" ### ".join(text).encode("utf-8")
    c = pycurl.Curl()
    c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
    c.setopt(pycurl.URL, 'https://api.pushbullet.com/v2/pushes')
    c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(pycurl.USERPWD, apikey.encode('utf-8'))
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, postData)
    c.perform()

class SJ(Hook):
    __name__ = "SJ"
    __version__ = "1.08"
    __description__ = "Findet und fuegt neue Episoden von SJ.org pyLoad hinzu"
    __config__ = [("activated", "bool", "Aktiviert", "False"),
                  ("regex","bool","Eintraege aus der Suchdatei als regulaere Ausdruecke behandeln", "False"),
                  ("quality", """480p;720p;1080p""", "480p, 720p oder 1080p", "720p"),
                  ("file", "file", "Datei mit Seriennamen", "SJ.txt"),
                  ("rejectlist", "str", "Titel ablehnen mit (; getrennt)", "dd51;itunes"),
                  ("language", """DEUTSCH;ENGLISCH""", "Sprache", "DEUTSCH"),
                  ("interval", "int", "Interval", "60"),
                  ("hoster", """ul;so;fm;cz;alle""", "ul.to, filemonkey, cloudzer, share-online oder alle", "ul"),
                  ("pushover", "str", "deine pushover api", ""),
                  ("queue", "bool", "Direkt in die Warteschlange?", "False"),
                  ("pushbulletapi","str","Your Pushbullet-API key","0")]
    __author_name__ = ("gutz-pilz","zapp-brannigan")
    __author_mail__ = ("unwichtig@gmail.com","")

    def setup(self):
        self.interval = self.getConfig("interval") * 60

    def periodical(self):
        feed = feedparser.parse('http://serienjunkies.org/xml/feeds/episoden.xml')
        
        self.pattern = "|".join(getSeriesList(self.getConfig("file"))).lower()
        reject = self.getConfig("rejectlist").replace(";","|").lower() if len(self.getConfig("rejectlist")) > 0 else "^unmatchable$"
        self.quality = self.getConfig("quality")
        self.hoster = self.getConfig("hoster")
        if self.hoster == "alle":
            self.hoster = "."
        self.added_items = []
        
        for post in feed.entries:
            link = post.link
            title = post.title
            
            if self.getConfig("regex"):
                m = re.search(self.pattern,title.lower())
                if not m and not "720p" in title and not "1080p" in title:
                    m = re.search(self.pattern.replace("480p","."),title.lower())
                    self.quality = "480p"
                if m:
                    if "720p" in title.lower(): self.quality = "720p"
                    if "1080p" in title.lower(): self.quality = "1080p"
                    m = re.search(reject,title.lower())
                    if m:
                        self.core.log.debug("SJFetcher - Abgelehnt: " + title)
                        continue
                    title = re.sub('\[.*\] ', '', post.title)
                    self.range_checkr(link,title)
                                
            else:
                if self.getConfig("quality") != '480p':
                    m = re.search(self.pattern,title.lower())
                    if m:
                        if self.getConfig("language") in title:
                            mm = re.search(self.quality,title.lower())
                            if mm:
                                mmm = re.search(reject,title.lower())
                                if mmm:
                                    self.core.log.debug("SJFetcher - Abgelehnt: " + title)
                                    continue
                                title = re.sub('\[.*\] ', '', post.title)
                                self.range_checkr(link,title)
        
                else:
                    m = re.search(self.pattern,title.lower())
                    if m:
                        if self.getConfig("language") in title:
                            if "720p" in title.lower() or "1080p" in title.lower():
                                continue
                            mm = re.search(reject,title.lower())
                            if mm:
                                self.core.log.debug("SJFetcher - Abgelehnt: " + title)
                                continue
                            title = re.sub('\[.*\] ', '', post.title)
                            self.range_checkr(link,title)
                        
        send_mail(self.added_items) if len(self.added_items) > 0 else True
        notifyPushbullet(self.getConfig("pushbulletapi"),self.added_items) if len(self.added_items) > 0 else True
            
                    
    def range_checkr(self, link, title):
        pattern = re.match(".*S\d{2}E\d{2}-\d{2}.*", title)
        if pattern is not None:
            range0 = re.sub(r".*S\d{2}E(\d{2}-\d{2}).*",r"\1", title)
            number1 = re.sub(r"(\d{2})-\d{2}",r"\1", range0)
            number2 = re.sub(r"\d{2}-(\d{2})",r"\1", range0)
            title_cut = re.sub(r"(.*S\d{2}E).*",r"\1",title)
            for count in range(int(number1),(int(number2)+1)):
                NR = re.match("d\{2}", str(count))
                if NR is not None:
                    title1 = title_cut + str(count)
                    self.range_parse(link, title1)
                else:
                    title1 = title_cut +"0"+ str(count)
                    self.range_parse(link, title1)
        else:
            self.parse_download(link, title)


    def range_parse(self,series_url, search_title):
        req_page = getURL(series_url)
        soup = BeautifulSoup(req_page)
        titles = soup.findAll(text=re.compile(search_title))
        for title in titles:
           if self.quality !='480p' and self.quality in title: 
               self.parse_download(series_url, title)
           if self.quality =='480p' and not (('.720p.' in title) or ('.1080p.' in title)):               
               self.parse_download(series_url, title)


    def parse_download(self,series_url, search_title):
        req_page = getURL(series_url)
        soup = BeautifulSoup(req_page)
        title = soup.find(text=re.compile(search_title))
        if title:
            items = []
            links = title.parent.parent.findAll('a')
            for link in links:
                url = link['href']
                pattern = '.*%s_.*' % self.hoster
                if re.match(pattern, url):
                    items.append(url)
            self.send_package(title,items) if len(items) > 0 else True
                 
    def send_package(self, title, link):
        storage = self.getStorage(title)
        if storage == 'downloaded':
            self.core.log.debug("SJFetcher - " + title + " already downloaded")
        else:
            self.core.log.info("SJFetcher - NEW EPISODE: " + title)
            self.setStorage(title, 'downloaded')
            if self.getConfig('pushover'):
                notify("SJ: Added package",title.encode("utf-8"),self.getConfig("pushover"))
            self.core.api.addPackage(title.encode("utf-8"), link, 1 if self.getConfig("queue") else 0)
            self.added_items.append(title.encode("utf-8"))
