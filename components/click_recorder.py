import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image # For type hinting

def click_recorder_component(image_to_click_on: Image.Image, section_title: str = "General Clicks", key_suffix: str = ""):
    """
    Allows recording general clicks on a given image.
    Args:
        image_to_click_on (PIL.Image.Image): The image on which to record clicks.
        section_title (str): Title for this section.
        key_suffix (str): A unique suffix for the streamlit_image_coordinates key
                          if multiple instances are used on the same page.
    Returns:
        list: A list of (x, y) tuples of recorded clicks.
    """
    if 'clicks' not in st.session_state:
        st.session_state.clicks = []

    if image_to_click_on is None:
        st.info("No image available to record clicks.")
        return []

    st.subheader(section_title)
    st.write("Click on the image to record additional coordinates.")

    general_click_coords = streamlit_image_coordinates(
        image_to_click_on,
        key=f"image_for_general_clicks_{key_suffix}"
    )

    if general_click_coords:
        clicked_x = general_click_coords['x']
        clicked_y = general_click_coords['y']
        
        if not st.session_state.clicks or \
           (st.session_state.clicks[-1][0] != clicked_x or st.session_state.clicks[-1][1] != clicked_y):
            st.session_state.clicks.append((clicked_x, clicked_y))
            st.toast(f"Recorded click on image: ({clicked_x}, {clicked_y})")

    # Display recorded clicks
    if st.session_state.clicks:
        st.write("Recorded Clicks:")
        for i, (x, y) in enumerate(st.session_state.clicks):
            st.write(f"{i+1}. X: {x}, Y: {y}")
    else:
        st.write("No clicks recorded yet.")
    
    return st.session_state.clicks