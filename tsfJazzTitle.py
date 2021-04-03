"""
This script to grab info from https://www.tsfjazz.com/

note:
install beautiful soup using the following command

>>> pip install beautifulsoup4

"""

from bs4 import BeautifulSoup
import requests


class TSJAZZ_TITLE:
    """
    Grab title and artist from main page
    of tsfjazz website
    """

    def cls_get_title_name():
        """
        returns
        : title, str, the song title 
        : artist, str, artist name

        """
        
        url = "https://www.tsfjazz.com/"

        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        one_soup = soup.prettify().split("\n")
        nbline = 0
        pay_attention = False
        # print(soup.prettify())
        for one_line in one_soup:
            nbline = nbline + 1
            if "<body>" in one_line:
                pay_attention = True
            if pay_attention is True:
                if '<div class="track">' in one_line:
                    position = nbline
                    break

        # for pos in range(position, position + 5):
        # print(one_soup[position + 1].lstrip())
        # print(one_soup[position + 4].lstrip())
        return one_soup[position + 1].lstrip(), one_soup[position + 4].lstrip()


if __name__ == "__main__":
    TSF = TSJAZZ_TITLE
    title, artist = TSF.cls_get_title_name()
    print("tit: " + title)
    print("art: " + artist)