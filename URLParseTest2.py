import urllib.request
import urllib
import ssl
import json

from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

#https://en.wikipedia.org/w/api.php?action=help&modules=parse
#https://www.mediawiki.org/wiki/API:Query
ssl._create_default_https_context = ssl._create_unverified_context #SSL certificate for https
with urllib.request.urlopen('https://en.wikipedia.org/w/api.php?action=query&format=json&titles=wolf&prop=extracts&exintro&explaintext') as f:
    pageObj = json.loads(f.read())
    for key, value in pageObj['query']['pages'].items():
        print("\n")
        print(pageObj['query']['pages'][key]['title'])
        #print(pageObj['query']['pages'][key]['extract'])

#with user agent defined as mozilla to avoid simple bot detection
req = urllib.request.Request('https://wiki.ss13.co/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Cluwne')
# Customize the default User-Agent header value:
req.add_header('User-Agent', 'Mozilla/5.0')
with urllib.request.urlopen(req) as r:
    pageObj2 = json.loads(r.read())
    for key, value in pageObj2['query']['pages'].items():
        print("\n")
        print(pageObj2['query']['pages'][key]['title'])
        print(pageObj2['query']['pages'][key]['revisions'])

req2 = urllib.request.Request("https://wiki.warthunder.com/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Wyvern_S4")
# Customize the default User-Agent header value:
req2.add_header('User-Agent', 'Mozilla/5.0')
with urllib.request.urlopen(req2) as r2:
    pageObj3 = json.loads(r2.read())
    for key, value in pageObj3['query']['pages'].items():
        print("\n")
        print(pageObj3['query']['pages'][key]['title'])
        wikiText = pageObj3['query']['pages'][key]['revisions'][0]['*']
        wikiText = wikiText.replace('&','%26')
        #todo replace [[A|B]] -> B and [[X]] -> X
        print(wikiText)
        print('\n')
        
        print("https://wiki.warthunder.com/api.php?action=expandtemplates&format=json&prop=wikitext&title=Wyvern_S4&text={}".format(urllib.parse.quote_plus(wikiText)[:3000]))
        print('\n')
        req3 = urllib.request.Request("https://wiki.warthunder.com/api.php?action=expandtemplates&format=json&prop=wikitext&title=Wyvern_S4&text={}".format(urllib.parse.quote_plus(wikiText)[:3000]))
        req3.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req3) as r3:
            pageObj4 = json.loads(r3.read())
            for key, value in pageObj4.items():
                print(strip_tags(pageObj4['expandtemplates']['wikitext']))
                #todo Removed all [[]]
    
