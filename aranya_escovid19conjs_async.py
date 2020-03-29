# Código para ejecución asíncrona
# https://stackoverflow.com/questions/54768871/how-to-render-asynchronous-page-with-requests-html-in-a-multithreaded-environmen
# Doc sobre requests-html
# https://requests-html.kennethreitz.org/
# Tutorial en video
# https://www.youtube.com/watch?v=a6fIbtFB46g
from pprint import pprint
import asyncio
from concurrent.futures import ThreadPoolExecutor

from requests_html import AsyncHTMLSession


async def fetch(session, url):
    r = await session.get(url)
    await r.html.arender()
    return r.html.raw_html


def parseWebpage(page):
    pprint(page.decode('utf8'))


async def get_data_asynchronous():
    urls = [
        'https://covid19.isciii.es/'
    ]

    with ThreadPoolExecutor(max_workers=20) as executor:
        with AsyncHTMLSession() as session:
            # Set any session parameters here before calling `fetch`

            # Initialize the event loop
            loop = asyncio.get_event_loop()

            # Use list comprehension to create a list of
            # tasks to complete. The executor will run the `fetch`
            # function for each url in the urlslist
            tasks = [
                await loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, url)  # Allows us to pass in multiple arguments
                                     # to `fetch`
                )
                for url in urls
            ]

            # Initializes the tasks to run and awaits their results
            for response in await asyncio.gather(*tasks):
                parseWebpage(response)


def main():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)


main()
