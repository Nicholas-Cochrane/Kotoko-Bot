from lxml import html
from lxml.etree import Comment
import requests
import html2text
import pwb
import pywikibot

page = requests.get('https://en.wikipedia.org/wiki/Wolf')

tree = html.fromstring(page.content)
body = tree.xpath('//div[@id="content"]')[0]
print(html2text.html2text(str(html.tostring(body))))

""""TRY THIS NEXT TIME
https://en.wikipedia.org/w/api.php?action=query&format=json&titles=wolf&prop=extracts&exintro&explaintext
"""
"""https://wiki.ss13.co/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Cluwne"""
https://wiki.ss13.co/Special:Version
https://www.mediawiki.org/wiki/Special:Version
https://www.mediawiki.org/wiki/Extension:TextExtracts
"""text = ""

text = text + (tree.xpath('//h1[@id="firstHeading"]')[0].text) + ". "
text = text + ((tree.xpath('//div[@id="bodyContent"]')[0]).xpath('//div[@id="siteSub"]')[0].text)
plist = ((tree.xpath('//div[@class="mw-parser-output"]')[0]).xpath('//p'))
         
print(text)
print("___")
def recrusiveRead(tag):
    if tag.text and not tag.tag == Comment:
        print(tag.tag)
        print(tag.text)
    for subtag in tag:
        recrusiveRead(subtag)
        
for tag in plist[2]:
    recrusiveRead(tag)"""
