import streamlit as st
from PIL import Image
from io import BytesIO
from streamlit_image_coordinates import streamlit_image_coordinates

MAX_IMAGE_WIDTH = 500

def image_cropper_component(original_image_pil):
    """
    Streamlit component to handle image cropping based on two user clicks.
    Updates st.session_state.crop_points and st.session_state.cropped_image_data.
    Displays the original image for cropping and the cropped image if available.

    Args:
        original_image_pil (PIL.Image.Image): The original PIL Image object to be cropped.

    Returns:
        PIL.Image.Image or None: The cropped PIL Image object if available, otherwise None.
    """

    # If already cropped, just load and display the cropped image
    if st.session_state.cropped_image_data is not None:
        cropped_pil_image = Image.open(BytesIO(st.session_state.cropped_image_data))
        return cropped_pil_image
    
    # If not yet cropped, show the original image for cropping interface
    else:
        st.write("Clique em dois pontos na imagem para definir os cantos superior esquerdo e inferior direito do retângulo de recorte.")
        current_coordinates = streamlit_image_coordinates(
            original_image_pil,
            key="original_image_for_cropping",
        )

        if current_coordinates:
            clicked_x = current_coordinates['x']
            clicked_y = current_coordinates['y']

            # Only append if it's a new, distinct click
            if not st.session_state.crop_points or \
               (st.session_state.crop_points[-1][0] != clicked_x or st.session_state.crop_points[-1][1] != clicked_y):
                
                if len(st.session_state.crop_points) < 2:
                    st.session_state.crop_points.append((clicked_x, clicked_y))
                    st.toast(f"Ponto de corte {len(st.session_state.crop_points)} selecionado: ({clicked_x}, {clicked_y})")
                    
                    if len(st.session_state.crop_points) == 2:
                        st.write("Cortando imagem com os pontos selecionados...")
                        p1 = st.session_state.crop_points[0]
                        p2 = st.session_state.crop_points[1]

                        x1, y1 = min(p1[0], p2[0]), min(p1[1], p2[1])
                        x2, y2 = max(p1[0], p2[0]), max(p1[1], p2[1])

                        # Ensure coordinates are within image bounds
                        x1 = max(0, x1)
                        y1 = max(0, y1)
                        x2 = min(original_image_pil.width, x2)
                        y2 = min(original_image_pil.height, y2)

                        cropped_image = original_image_pil.crop((x1, y1, x2, y2))
                        
                        buf = BytesIO()
                        # Save the cropped image as a standard format (e.g., PNG)
                        # This conversion is important for PIL to later identify it.
                        cropped_image.save(buf, format="PNG")
                        st.session_state.cropped_image_data = buf.getvalue()
                        
                        st.success("Imagem cortada com sucesso! Exibindo imagem cortada abaixo.")
                        st.rerun() # Rerun to display the cropped image by the next pass
        
        if len(st.session_state.crop_points) < 2:
            st.info(f"Selecione {2 - len(st.session_state.crop_points)} mais pontos para selecionar a área cortada.")
        
        return None # No cropped image yet