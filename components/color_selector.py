import streamlit as st
from PIL import Image
import numpy as np
import cv2
from io import BytesIO
from streamlit_image_coordinates import streamlit_image_coordinates

def color_selector_component(cropped_image_pil):
    """
    Allows user to select a color from the cropped image and displays it.
    Args:
        cropped_image_pil (PIL.Image.Image): The cropped image to select color from.
    Returns:
        tuple: (rgb_color, hsv_color) if a color is selected, otherwise (None, None).
    """
    if 'selected_color_rgb' not in st.session_state:
        st.session_state.selected_color_rgb = None
    if 'selected_color_hsv' not in st.session_state:
        st.session_state.selected_color_hsv = None

    if cropped_image_pil is None:
        return None, None

    st.subheader("2. Select Color")
    st.write("Click on the cropped image to select a pixel's color.")

    if st.session_state.selected_color_rgb is None:
        color_selection_coords = streamlit_image_coordinates(
            cropped_image_pil,
            key="cropped_image_for_color_selection"
        )

        if color_selection_coords:
            pixel_x = color_selection_coords['x']
            pixel_y = color_selection_coords['y']

            rgb_color = cropped_image_pil.getpixel((pixel_x, pixel_y))
            
            # Convert RGB to HSV using OpenCV
            # OpenCV uses BGR by default, so convert RGB to BGR first
            bgr_color = np.array([[[rgb_color[2], rgb_color[1], rgb_color[0]]]], dtype=np.uint8)
            hsv_color = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)[0][0]

            st.session_state.selected_color_rgb = rgb_color
            st.session_state.selected_color_hsv = tuple(hsv_color.tolist())
            
            st.toast(f"Color selected at ({pixel_x}, {pixel_y}): RGB {rgb_color}, HSV {st.session_state.selected_color_hsv}")
            st.rerun()

    if st.session_state.selected_color_rgb:
        st.write("Selected Color:")
        color_hex = f"#{st.session_state.selected_color_rgb[0]:02x}{st.session_state.selected_color_rgb[1]:02x}{st.session_state.selected_color_rgb[2]:02x}"
        st.markdown(
            f'<div style="width: 100px; height: 50px; background-color: {color_hex}; border: 1px solid black;"></div>'
            f'<p>RGB: {st.session_state.selected_color_rgb}</p>'
            f'<p>HSV (OpenCV range H:0-179, S:0-255, V:0-255): {st.session_state.selected_color_hsv}</p>',
            unsafe_allow_html=True
        )
        if st.button("Reset Color Selection"):
            st.session_state.selected_color_rgb = None
            st.session_state.selected_color_hsv = None
            st.rerun()
    
    return st.session_state.selected_color_rgb, st.session_state.selected_color_hsv