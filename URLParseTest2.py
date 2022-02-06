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
    #print('split list')
    for index, substring in enumerate(temp):
        x = substring.find('|')
        y = substring.find('@inside@')
        if (x != -1 and y != -1):
            #print(temp[index])
            if(substring.find('@inside@File:') != -1):
                temp[index] = '' #if link is a file remove link
            else:
                temp[index] = substring[x+1:] #replace [[A|B]] -> B
            #print(temp[index])
            
        if(temp[index].find(':')!= -1 and temp[index].find('@inside@')!= -1):
            temp[index] = '' #remove [[X]]'s that contain a : EX: [[Catagory:verb]]->Verb
        #TODO ignore <code> tags (modifiy html stripper or pre htlm stripper)
        #TODO remove links
    #   #TODO [[Wiktionary:hello|]] -> hello Currently deletes link (rare and a pain to parse)
    newStr = ''.join(temp).replace('@inside@','').replace('=','').replace('\'\'\'','')#remove fromating like == and ''' 
    return re.sub('( \s*)\n','\n',re.sub('(\n(!|\|).*?(\n|\Z)((!|\|).*?(\n|\Z))*)|({\| class).*','\n',re.sub('__.*?__','',newStr))) #Remove extra whitespace(remove lines for wikitables including any line starting with ! or | (remove __X__ ex: __TOC__))
     
#https://en.wikipedia.org/w/api.php?action=help&modules=parse
#https://www.mediawiki.org/wiki/API:Query
ssl._create_default_https_context = ssl._create_unverified_context #SSL certificate for https
with urllib.request.urlopen('https://en.wikipedia.org/w/api.php?action=query&format=json&titles=wolf&prop=extracts&exintro&explaintext') as f:
    pageObj = json.loads(f.read())
    for key, value in pageObj['query']['pages'].items():
        print("\n")
        #print(pageObj['query']['pages'][key]['title'])
        #print(pageObj['query']['pages'][key]['extract'])

#with user agent defined as mozilla to avoid simple bot detection
req = urllib.request.Request('https://wiki.ss13.co/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Cluwne')
#Customize the default User-Agent header value:
req.add_header('User-Agent', 'Mozilla/5.0')
with urllib.request.urlopen(req) as r:
    pageObj2 = json.loads(r.read())
    for key, value in pageObj2['query']['pages'].items():
        print("\n")
        #print(pageObj2['query']['pages'][key]['title'])
        #print(wikitextClean(pageObj2['query']['pages'][key]['revisions'][0]['*']))

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
            for key, value in pageObj4['expandtemplates'].items():
               print('pre wikitext func')
               print((pageObj4['expandtemplates']['wikitext']))
               print('post')
               print(wikitextClean(strip_tags(pageObj4['expandtemplates']['wikitext'])))

               
#tts = gtts.gTTS(wikitextClean(strip_tags(pageObj4['expandtemplates']['wikitext'])))
#tts.save("test.mp3")
