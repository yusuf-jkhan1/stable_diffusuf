import streamlit as st
from hf_api import HF_API
from dotenv import load_dotenv
import os
import time
import yaml
from PIL import Image

load_dotenv()
hf_api = HF_API(os.getenv('hf_repo'))

st.set_page_config(page_title="Stable Diffusuf",layout="wide")

st.header('Stable Diff-usuf v0.1')
st.subheader('Use prompts to generate Yusuf avatars')
st.empty()

with st.expander("About"):
    st.markdown("""
    > NOTES: 
    - This is all running on inexepensive endpoints/free tier services, so it may take a while to generate an image. Please be patient. 
    - For the same reason it will occasionly get confused and generate a blank image. If this happens, just try again with a different input.
    - The endpoint initializes a seed when it is first loaded. Within the same session the outputs are deterministic.
    - The endpoint offboards the model aggresively (within 60-120 seconds), so it may take a while to load the first time you use it. Or if you pause between generating images.
    """)
    st.write("If I find time, and some free credits, I'll try to host this on a more robust service. That includes a fine-tuning pipeline so you can upload your own images and create avatars of yourself")
    st.write("Also it's entirely possible my free credits expire without me noticing =)")

with st.expander("Prompt Builder"):

    st.write("Prompt Engineering is the difference between great and garbage generations. I've tried to templatize it as much as makes sense, but this is far from a perfect formula.")
    
    medium_tab, style_tab, background_tab, modifier_tab = st.tabs(["Medium", "Style", "Background", "Modifiers"])

    #Medium
    with medium_tab:
        if st.checkbox("Select from presets", key="medium"):
            with open("options.yaml") as f:
                options = yaml.load(f, Loader=yaml.FullLoader)
                medium_presets = options["medium_presets"]
            medium = st.selectbox(
                'Medium',
                medium_presets
                )
        else:
            medium = st.text_input("Describe a medium:")

    #Style
    with style_tab:
        if st.checkbox("Select from presets", key="style"):
            with open("options.yaml") as f:
                    options = yaml.load(f, Loader=yaml.FullLoader)
                    style_presets = options["style_presets"]
            style = st.selectbox(
                    'Style',
                    style_presets
                    )
        else:
            style = st.text_input("Describe a style:")

    #Background
    with background_tab:
        if st.checkbox("Select from presets", key="background"):
            with open("options.yaml") as f:
                    options = yaml.load(f, Loader=yaml.FullLoader)
                    background_presets = options["background_presets"]
            background = st.selectbox(
                    'Background',
                    background_presets
                    )
        else:
            background = st.text_input("Describe a background:")

    #Modifiers
    with modifier_tab:
        if st.checkbox("Select from presets", key="modifiers"):
            with open("options.yaml") as f:
                    options = yaml.load(f, Loader=yaml.FullLoader)
                    modifier_presets = options["modifier_presets"]
            modifiers = st.multiselect(
                    'Modifiers',
                    modifier_presets,
                    default=modifier_presets[0:10]
                    )
        else:
            modifiers = st.text_input("Add a comma-separated list of modifiers:")

#Weighting
with st.expander("Weighting"):
    subject_weight = st.slider("Subject Weighting", -10.0, 10.0, 0.0, 0.5)
    background_weight = st.slider("Background Weighting", -10.0, 10.0, 0.0, 0.5)
    modifier_weight = st.slider("Modifier Weighting", -10.0, 10.0, 0.0, 0.5)

input_prompt = f"""
{medium} of yusufjkhan1 as
{style} : {subject_weight} |
{background} : {background_weight} |
{modifiers} : {modifier_weight}
"""

display_prompt = input_prompt.replace("yusufjkhan1", "Yusuf")
st.write("Prompt: ", display_prompt)


if st.button("Generate Image"):
    hf_api.generate(input_prompt)
    while hf_api.status != "Success":
        st.write(hf_api.status)
        time.sleep(30)
    st.write("Success!")
    image = Image.open(hf_api._fpath)
    st.image(image, use_column_width=True)