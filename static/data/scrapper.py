from io import BytesIO
from bs4 import BeautifulSoup
import requests
import pickle
import json
import datetime
import pandas as pd
from typing import Dict
from colorthief import ColorThief
import logging
logging.basicConfig(level=logging.INFO)

char_list_url = "https://grayravens.com/wiki/Main_Page"
char_page_base_url = "https://grayravens.com"


def get_num_characters() -> int:
    """Get the number of operators available on Gamepress.
    """
    req = requests.get(char_list_url)
    soup = BeautifulSoup(req.content, "lxml")

    # There is a div with individual divs per character
    char_list = soup.find("div", class_="desktop-hide").find_all("div", class_="character_icon_div")
    # Get the number of characters available
    num_characters = len(char_list)

    return num_characters


def scrape_pages() -> None:
    """Given the page with the list of operators, scrape their names and individual pages' URL.
    This data is exported in a pickle file.
    """
    # Scrape the operator's names and page URLs
    req = requests.get(char_list_url)
    soup = BeautifulSoup(req.content, "lxml")

    # Get all the divs of character portraits with links to their pages
    char_list = soup.find("div", class_="desktop-hide").find_all("div", class_="character_icon_div")
    char_dict = {}
    for character in char_list:
        # Get the name and their personal page from these HTML elements
        name = character.find("a")["title"]
        page = char_page_base_url + character.find("a")["href"] + "/Gallery"
        # Add the new information to the dictionary
        char_dict[name] = page
        # logging.info(f"{datetime.datetime.now()}: Found {name}")
    logging.info(f"{datetime.datetime.now()}: Found {len(char_list)} characters")

    # Write this dictionary to a pickle file
    with open("character_pages.pickle", "wb") as f:
        pickle.dump(char_dict, f)
        logging.info(f"{datetime.datetime.now()}: Created pickle file with character pages")


def gen_operator_colour(art_url: str) -> str:
    """Generate a colour for an operator by detecting the most dominant colour on their E0 art.
    """
    # Request the image
    img_req = requests.get(art_url)
    # Read the response content
    img_bytes = BytesIO(img_req.content)
    # Create a ColorThief object for the image (in bytes)
    colour_thief = ColorThief(img_bytes)
    # Build a colour palette
    palette = colour_thief.get_palette(color_count=2)
    # Convert the generated colour to hex
    colour_chosen = palette[0]
    colour_chosen = f"#{colour_chosen[0]:02x}{colour_chosen[1]:02x}{colour_chosen[2]:02x}"
    # Return only the most dominant colour
    return colour_chosen


def scrape_op_art(char_pages: Dict[str, str]) -> None:
    """Given a dictionary of characters and the URLs to their pages, scrape all their promotion and skins artwork.
    """

    # Dict to contains an entry per character of coating-imageUrl pairs
    char_info = dict()

    # Loop through available operators
    for character in char_pages:
        logging.info(f"{datetime.datetime.now()}: Scraping {character}")
        page = char_pages[character]

        # Get the operator's page
        req = requests.get(page)
        soup = BeautifulSoup(req.content, "lxml")
        
        # Get img elements
        coatings_imgs = [coating_elem.find_all("img") for coating_elem in soup.find_all("div", class_="tabbertab") if coating_elem.find_all("img")]
        # print(coatings_imgs)
        
        # Now get the URL to each image
        coatings_imgs = [img[0]["srcset"].split(" ")[2] for img in coatings_imgs if ".png" in img[0]["srcset"]]
        # Now clean the URL to get the high resolution
        coatings_imgs = [f"{img.split('.png')[0]}.png".replace("/thumb", "") for img in coatings_imgs]
        coatings_imgs = [img for img in coatings_imgs if "screenshot" not in img.lower()]
        
        # Derive the coating name from the image URL
        coatings_names = [img.split("/")[-1].replace(".png", "").replace("-", " ").replace("Coating ", "") for img in coatings_imgs]
        # print(coatings_imgs)
        # print(coatings_names)

        # Generate the operator colour
        # operator_colour = gen_operator_colour(e2_img) if e2_img != "" else gen_operator_colour(e0_img)

        # Create a mapping of coating names to image url
        coating_dict = {coatings_names[i]: coatings_imgs[i] for i in range(len(coatings_imgs))}
        # And store it under the character key in the main dict
        char_info[character] = coating_dict
        # char_info.append({character: coating_dict})

    
    # Export the list of skins dictionaries as a JSON
    with open("char_info.json", "w") as f:
        json.dump(char_info, f, indent=4)


def main() -> None:
    # Load the pickle file with the operator pages
    with open("character_pages.pickle", "rb") as f:
        char_pages = pickle.load(f)
    
    # Get the number of operators in the pickle and on Gamepress
    num_char_pickle = len(char_pages.keys())
    num_char_live = get_num_characters()

    # If the pickle has as many characters as the website, use this pickle and get the character art
    if num_char_pickle == num_char_live:
        logging.info(f"{datetime.datetime.now()}: Pickle up to date. Scraping character art")
        scrape_op_art(char_pages)
    
    # Otherwise, we need to scrape all characters again, load the new pickle
    # and finally get the character art
    else:
        logging.info(f"{datetime.datetime.now()}: Pickle outdated. Scraping characters from scratch")
        scrape_pages()
        with open("character_pages.pickle", "rb") as f:
            char_pages = pickle.load(f)
        scrape_op_art(char_pages)


if __name__ == "__main__":
    main()
    
    # get_num_characters()
    # scrape_pages()
    
    # scrape_pages()
    # with open("character_pages.pickle", "rb") as f:
    #     char_pages = pickle.load(f)
    # char_pages = {
    #     "Lucia": "https://grayravens.com/wiki/Liv:_Eclipse/Gallery#Gray%20Feathers:%20Eclipse",
    # }
    # scrape_op_art(char_pages)