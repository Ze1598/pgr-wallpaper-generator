from PIL import Image, ImageFile
import streamlit as st
from streamlit import caching
import json
import os
import wallpaper_gen
import utils
st.set_option("deprecation.showfileUploaderEncoding", False)
ImageFile.LOAD_TRUNCATED_IMAGES = True

st.markdown("""
# Punishing Gray Raven Phone Wallpaper Generator

Create phone wallpapers for your favourite characters!

If you're interested in the code, you can find it on my GitHub repository [here](https://github.com/Ze1598/pgr-wallpaper-generator).

For feedback, feel free to reach out to me on Twitter [@ze1598](https://twitter.com/ze1598).

P.S. as the images are high resolution, you might come across partial loads in the image art. Please try different art options until the art you want fully loads.
""")


@st.cache
def load_data_file():
    """Load the main CSV of operator names, promotion images' URLs and theme colors.
    This function exists so the data can be cached.
    """
    data_path = os.path.join("static", "data", "char_info.json")
    with open(data_path, "r") as f:
        data = json.load((f))
    return data


# Load the necessary data and sort it by alphabetical order of names
main_data = load_data_file()

# Dropdown to filter by operator rank
character_choice = st.selectbox(
    "Choose the character",
    sorted(tuple(main_data.keys()))
)

character_coatings = main_data[character_choice]
# coating_choice = st.selectbox(
#     "Choose the coating",
#     sorted(tuple(character_coatings.keys()))
# )

# Choose the fore and background art individually
foreground_art = st.selectbox(
    "Choose the coating",
    sorted(tuple(character_coatings.keys()))
)
# background_art = st.selectbox(
#     "Choose a coating for the background (optionally None):",
#     ["None"] + sorted(tuple(character_coatings.keys()))
# )
background_art = "None"

# Upload a custom background image for the wallpaper
custom_bg_img = st.file_uploader(
    "You can upload a custom background image to replace the default black one with 640x1280 dimensions (otherwise it is resized)", 
    type=["png", "jpg"]
)
# Save the uploaded image (deleted from the server at the end of the script)
if custom_bg_img != None:
    custom_bg_name = "custom_bg_img.png"
    custom_bg_path = os.path.join("static", "resources", custom_bg_name)
    pil_custom_bg_img = Image.open(custom_bg_img).resize((640, 1280)).save(custom_bg_path)

# Change the operator theme color
# Using the beta version until the generally available version is fixed in Streamlit 
# theme_colour = st.beta_color_picker("Feel free to change the operator theme color", "#B7011D")
theme_colour = st.color_picker("Feel free to change the operator theme color", "#B7011D")
# theme_colour ="#B7011D"

fg_art_url = character_coatings.get(foreground_art, None)
bg_art_url = character_coatings.get(background_art, None)
# main_img_url = character_coatings.get(coating_choice, None)

# Create the image name string
wallpaper_name = character_choice.replace(":", "_") + ".png"
wallpaper_bg_path = custom_bg_path if custom_bg_img != None else ""

# DEBUG
# st.write("foreground", fg_art_url)
# st.write("background", bg_art_url)
# st.write(wallpaper_name, fg_art_url, bg_art_url, wallpaper_bg_path, theme_colour)

# Generate the wallpaper
wallpaper_gen.main(
    wallpaper_name,
    fg_art_url,
    bg_art_url,
    wallpaper_bg_path,
    theme_colour
)
# Display the wallpaper
st.image(wallpaper_name, use_column_width=True)

# Encode the image to bytes so a download link can be created
encoded_img = utils.encode_img_to_b64(wallpaper_name)
href = f'<a href="data:image/png;base64,{encoded_img}" download="{wallpaper_name}">Download the graphic</a>'
# Create the download link
st.markdown(href, unsafe_allow_html=True)

# Delete the graphic from the server
os.remove(wallpaper_name)
try:
    os.remove(custom_bg_path)
except:
    pass