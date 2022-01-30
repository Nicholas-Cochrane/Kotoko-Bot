import urllib.request
import urllib
import re
import ssl
import json
import gtts
from playsound import playsound

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
    def handle_endtag(self, tag):
        self.text.write(' ')
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def wikitextClean(str):
    '''clean up wikitext remove [[]], =, and \'\'\' '''
    markedStr = str.replace('[[','[[@inside@').replace('%26', '&') #add marker for inside of link and clean up &'s from link safe to normal
    temp = re.split('\[\[|\]\]',markedStr) #split on links [[X]] -> X
    for index, substring in enumerate(temp):
        x = substring.find('|')
        if (x != -1):
            temp[index] = substring[x+1:] #replace [[A|B]] -> B
            
        if(temp[index].find(':')!= -1 and temp[index].find('@inside@')!= -1):
            temp[index] = '' #remove [[X]]'s that contain a : EX: [[Catagory:verb]]->Verb
        #todo ignore <code> tags (modifiy html stripper or pre htlm stripper)
        #todo remove links and clean up or remove tables
    newStr = ''.join(temp).replace('@inside@','').replace('=','').replace('\'\'\'','')#remove fromating like == and ''' 
    return re.sub('( \s*)\n','\n',re.sub('__.*?__','',newStr)) #remove__X__ used for things like table of contents and can be in templates and remove empty lines
     
#https://en.wikipedia.org/w/api.php?action=help&modules=parse
#https://www.mediawiki.org/wiki/API:Query
ssl._create_default_https_context = ssl._create_unverified_context #SSL certificate for https
with urllib.request.urlopen('https://en.wikipedia.org/w/api.php?action=query&format=json&titles=wolf&prop=extracts&exintro&explaintext') as f:
    pageObj = json.loads(f.read())
    for key, value in pageObj['query']['pages'].items():
        print("\n")
        print(pageObj['query']['pages'][key]['title'])
        print(pageObj['query']['pages'][key]['extract'])

#with user agent defined as mozilla to avoid simple bot detection
req = urllib.request.Request('https://wiki.ss13.co/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Cluwne')
# Customize the default User-Agent header value:
req.add_header('User-Agent', 'Mozilla/5.0')
with urllib.request.urlopen(req) as r:
    pageObj2 = json.loads(r.read())
    for key, value in pageObj2['query']['pages'].items():
        print("\n")
        print(pageObj2['query']['pages'][key]['title'])
        print(wikitextClean(pageObj2['query']['pages'][key]['revisions'][0]['*']))

req2 = urllib.request.Request("https://wiki.warthunder.com/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Wyvern_S4")
# Customize the default User-Agent header value:
req2.add_header('User-Agent', 'Mozilla/5.0')
with urllib.request.urlopen(req2) as r2:
    pageObj3 = json.loads(r2.read())
    for key, value in pageObj3['query']['pages'].items():
        #print("\n")
        #print(pageObj3['query']['pages'][key]['title'])
        wikiText = pageObj3['query']['pages'][key]['revisions'][0]['*']
        wikiText = wikiText.replace('&','%26')
        #print(wikiText)
        """print('\n')
        
        print("https://wiki.warthunder.com/api.php?action=expandtemplates&format=json&prop=wikitext&title=Wyvern_S4&text={}".format(urllib.parse.quote_plus(wikiText)[:3000]))
        print('\n')"""
        req3 = urllib.request.Request("https://wiki.warthunder.com/api.php?action=expandtemplates&format=json&prop=wikitext&title=Wyvern_S4&text={}".format(urllib.parse.quote_plus(wikiText)[:5000]))
        req3.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req3) as r3:
            pageObj4 = json.loads(r3.read())
            for key, value in pageObj4.items():
               #print(strip_tags(pageObj4['expandtemplates']['wikitext']))
               print(wikitextClean(strip_tags(pageObj4['expandtemplates']['wikitext'])))
    
#tts = gtts.gTTS(wikitextClean(strip_tags(pageObj4['expandtemplates']['wikitext'])))
#tts.save("test.mp3")
