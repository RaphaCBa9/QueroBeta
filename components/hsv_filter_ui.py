import streamlit as st
import numpy as np
import cv2
from PIL import Image # For converting back to PIL Image for display

def hsv_filter_component(input_image_pil, selected_color_hsv, max_display_width):
    """
    Displays HSV sliders and applies filtering to the image.
    Args:
        input_image_pil (PIL.Image.Image): The image to filter.
        selected_color_hsv (tuple): The (H, S, V) tuple of the selected base color.
        max_display_width (int): The maximum width to display the image.
    Returns:
        numpy.ndarray: The filtered image as a NumPy array if successful, otherwise None.
    """
    from utils.image_processing import apply_hsv_filter

    if 'hsv_tolerances' not in st.session_state:
        st.session_state.hsv_tolerances = {'H': 4, 'S': 100, 'V': 100}
    if 'erosion_iterations' not in st.session_state:
        st.session_state.erosion_iterations = 0
    if 'dilation_iterations' not in st.session_state:
        st.session_state.dilation_iterations = 0

    if selected_color_hsv is None or input_image_pil is None:
        st.info("Por favor, selecione uma cor e certifique-se de que a imagem esteja cortada para habilitar o filtro")
        return None, None

    st.write("Use os sliders para ajustar a tolerância da cor e filtar a imagem.")

    current_h_tol = st.session_state.hsv_tolerances['H']
    current_s_tol = st.session_state.hsv_tolerances['S']
    current_v_tol = st.session_state.hsv_tolerances['V']
    current_erosion = st.session_state.erosion_iterations
    current_dilation = st.session_state.dilation_iterations

    col_image, col_sliders = st.columns([2, 1])

    with col_sliders:
        st.subheader("Controles de Filtro HSV")
        new_h_tol = st.slider('Tolerância Hue (0-179)', 0, 50, value=current_h_tol, step=1, key='h_tolerance_slider')
        new_s_tol = st.slider('Tolerância Saturation (0-255)', 0, 100, value=current_s_tol, step=1, key='s_tolerance_slider')
        new_v_tol = st.slider('Tolerância Value (0-255)', 0, 100, value=current_v_tol, step=1, key='v_tolerance_slider')

        st.subheader("Controles de Operações Morfológicas")
        new_erosion = st.slider('Iterações de Erosão', 0, 10, value=current_erosion, step=1, key='erosion_slider')
        new_dilation = st.slider('Irerações de Dilatação', 0, 10, value=current_dilation, step=1, key='dilation_slider')

        if (new_h_tol != current_h_tol or
            new_s_tol != current_s_tol or
            new_v_tol != current_v_tol):
            st.session_state.hsv_tolerances['H'] = new_h_tol
            st.session_state.hsv_tolerances['S'] = new_s_tol
            st.session_state.hsv_tolerances['V'] = new_v_tol
        
        if new_erosion != current_erosion:
            st.session_state.erosion_iterations = new_erosion
        if new_dilation != current_dilation:
            st.session_state.dilation_iterations = new_dilation

    cropped_image_np_rgb = np.array(input_image_pil.convert('RGB'))

    filtered_image_np_rgb, binary_mask = apply_hsv_filter(
        cropped_image_np_rgb,
        selected_color_hsv,
        st.session_state.hsv_tolerances['H'],
        st.session_state.hsv_tolerances['S'],
        st.session_state.hsv_tolerances['V']
    )

    # Apply erosion and dilation
    if binary_mask is not None:
        kernel = np.ones((3,3), np.uint8)
        if st.session_state.erosion_iterations > 0:
            binary_mask = cv2.erode(binary_mask, kernel, iterations=st.session_state.erosion_iterations)
        if st.session_state.dilation_iterations > 0:
            binary_mask = cv2.dilate(binary_mask, kernel, iterations=st.session_state.dilation_iterations)
        
        # Re-apply the mask to the original image to show the effect of erosion/dilation
        # Create a blank image with the same dimensions as the original
        processed_image_rgb = np.zeros_like(cropped_image_np_rgb)
        # Apply the binary mask to each channel of the original image
        processed_image_rgb[binary_mask == 255] = cropped_image_np_rgb[binary_mask == 255]
        filtered_image_np_rgb = processed_image_rgb

    with col_image:
        st.subheader("Imagem Filtrada")
        st.image(filtered_image_np_rgb, caption="Imagem Filtrada", width=max_display_width)
    
    return filtered_image_np_rgb, binary_mask