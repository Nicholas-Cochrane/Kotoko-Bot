import urllib.request
import urllib
from urllib.parse import urlparse
import re
import ssl
import json
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
    """clean up wikitext (Wikimedia and Wikipedia)byexpanding templates and clean up resulting html, Cleaning up links [[A|B]], removing '=*'(Header notation), TOCs, wikitables and \'\'\'(Bold notation) """
    markedStr = str.replace('[[','[[@inside@') #add marker for inside of link and clean up &'s from link safe to normal
    temp = re.split('\[\[|\]\]',markedStr) #split on links [[X]] -> X
    #print('split list')
    for index, substring in enumerate(temp):
        x = substring.find('|')
        y = substring.find('@inside@')
        if (x != -1 and y != -1):
            if(substring.find('@inside@File:') != -1):
                temp[index] = '' #if link is a file remove link
            else:
                temp[index] = substring[x+1:] #replace [[A|B]] -> B
            
        if(temp[index].find(':')!= -1 and temp[index].find('@inside@')!= -1):
            temp[index] = '' #remove [[X]]'s that contain a : EX: [[Catagory:verb]]->Verb
        #TODO ignore <code> tags (modifiy html stripper or pre htlm stripper)
        #TODO remove links
        #TODO [[Wiktionary:hello|]] -> hello Currently deletes link (rare and a pain to parse)
        #TODO parse tables rather than just removing them
    newStr = ''.join(temp).replace('@inside@','').replace('=','').replace('\'\'\'','')#remove fromating like == and ''' 
    return re.sub('(\s*)\n','\n',re.sub('(\n(!|\|).*?(\n|\Z)((!|\|).*?(\n|\Z))*)|({\|).*','\n',re.sub('__.*?__','',newStr))) #Remove extra whitespace(remove lines for wikitables including any line starting with ! or | (remove __X__ ex: __TOC__))

def wikiURLParse(page):
    """"Returns a tuple of (domain, filename) """
    parsedPage = urlparse(page)
    splitPath = re.split('/',parsedPage.path)
    if(not parsedPage.netloc): #if url does not start with scheme
        if(parsedPage.path):
           netloc = splitPath[0]
        else:
            raise("Not a valid URL")
    else:
        netloc = parsedPage.netloc
    return netloc, splitPath[-1]
    
def wikimediaURLToText(page):
    """Takes in a Wikipedia or Wikimedia Wiki page URL and outputs the first text (extract) for wikipedia and atempts to parse a large part of the page for non wikipedia pages"""
    parsedPage = urlparse(page)
    splitPath = re.split('/',parsedPage.path)
    if(not parsedPage.netloc): #if url does not start with scheme
        if(parsedPage.path):
           netloc = splitPath[0]
        else:
            raise("Not a valid URL")
    else:
        netloc = parsedPage.netloc

    finalTexts = []
    ssl._create_default_https_context = ssl._create_unverified_context #SSL certificate for https
    #TODO add in ability to select sections (EX: Seattle#Media)
    if(netloc[-13:] == 'wikipedia.org'):#wikipedia use a different url to wikimedia and has different capibilities
        requestURL = 'https://{}/w/api.php?action=query&format=json&titles={}&prop=extracts&exintro&explaintext'.format(netloc,splitPath[-1])
        with urllib.request.urlopen(requestURL) as f:
            pageObj = json.loads(f.read())
            for key, value in pageObj['query']['pages'].items():
                #TODO add error handling for json return
                #TODO add revisions non extracts verson for wikipedia
                #print("\n")
                #print(pageObj['query']['pages'][key]['title'])
                #print(pageObj['query']['pages'][key]['extract'])
                finalTexts.append(pageObj['query']['pages'][key]['title'] + ' From Wikipedia, the free encyclopedia at ' + netloc + '\n' + pageObj['query']['pages'][key]['extract']) #id="siteSub" is the "from wikipedia" div if you want to add muli lingual options in the future
    else:
        requestURL = 'https://{}/api.php?action=query&prop=revisions&rvprop=content&format=json&titles={}'.format(netloc,splitPath[-1])
        #with user agent defined as mozilla to avoid simple bot detection
        req = urllib.request.Request(requestURL)
        #Customize the default User-Agent header value:
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req) as r:
            pageObj2 = json.loads(r.read())
            for key, value in pageObj2['query']['pages'].items():
                #print("\n")
                #print(pageObj2['query']['pages'][key]['title'])
                wikiText = pageObj2['query']['pages'][key]['revisions'][0]['*']
                #print(wikitextClean(pageObj2['query']['pages'][key]['revisions'][0]['*']))

                req3 = urllib.request.Request("https://{}/api.php?action=expandtemplates&format=json&prop=wikitext&title={}&text={}".format(netloc,splitPath[-1],urllib.parse.quote_plus(wikiText)[:8000]))
                req3.add_header('User-Agent', 'Mozilla/5.0')
                with urllib.request.urlopen(req3) as r3:
                    pageObj4 = json.loads(r3.read())
                    for key4, value4 in pageObj4['expandtemplates'].items():
                       #print('pre wikitext func')
                       #print((pageObj4['expandtemplates']['wikitext']))
                       #print('post')
                       #print(wikitextClean(strip_tags(pageObj4['expandtemplates']['wikitext'])))
                       finalTexts.append(pageObj2['query']['pages'][key]['title'] + ' at ' + netloc + wikitextClean(strip_tags(pageObj4['expandtemplates']['wikitext'])))
    return finalTexts[0]

test = input("Enter a Wikipedia or Wikimedia Wiki page URL:")
print(wikimediaURLToText(test))
#tts = gtts.gTTS(wikitextClean(strip_tags(pageObj4['expandtemplates']['wikitext'])))
#tts.save("sounds/test.mp3")
