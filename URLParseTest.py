import urllib.request
import urllib
from urllib.parse import urlparse
import re
import ssl
import json
from playsound import playsound
import aiohttp
import asyncio

from io import StringIO
from html.parser import HTMLParser
""""TRY THIS NEXT TIME
https://en.wikipedia.org/w/api.php?action=query&format=json&titles=wolf&prop=extracts&exintro&explaintext
"""
"""https://wiki.ss13.co/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Cluwne"""
"""https://wiki.ss13.co/Special:Version
https://www.mediawiki.org/wiki/Special:Version
https://www.mediawiki.org/wiki/Extension:TextExtracts"""
netloc = "en.wikipedia.org"
splitPath = ["Toki_Pona"]
async def test():
    finalTexts = []
    requestURL = 'https://{}/w/api.php?action=query&format=json&titles={}&prop=extracts&exintro&explaintext'.format(netloc,splitPath[-1])
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(requestURL) as f:
            pageObj = json.loads(await f.text())
            for key, value in pageObj['query']['pages'].items():
                #TODO add error handling for json return
                #TODO add revisions non extracts verson for wikipedia
                #print("\n")
                #print(pageObj['query']['pages'][key]['title'])
                #print(pageObj['query']['pages'][key]['extract'])
                finalTexts.append(pageObj['query']['pages'][key]['title'] + ' From Wikipedia, the free encyclopedia at ' + netloc + '\n' + pageObj['query']['pages'][key]['extract'])
    return finalTexts[0]


async def main():
    output = await test()
    print(output)
    
if __name__ == "__main__":
    asyncio.run(main())
