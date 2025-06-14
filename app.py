import streamlit as st
from PIL import Image
from io import BytesIO

# Import your custom components and utility functions
from components.image_cropper import image_cropper_component
from components.color_selector import color_selector_component
from components.hsv_filter_ui import hsv_filter_component
from components.hold_segmentation_viewer import hold_segmentation_viewer_component
from utils.image_processing import apply_hsv_filter, find_fastest_route, visualize_route # Adicionado find_fastest_route, visualize_route
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(layout="wide")
st.title("Image Processing App (Modular)")

# --- Initialize session state variables ---
if 'clicks' not in st.session_state:
    st.session_state.clicks = []
if 'uploaded_image_info' not in st.session_state:
    st.session_state.uploaded_image_info = {"name": None, "data": None}
if 'crop_points' not in st.session_state:
    st.session_state.crop_points = []
if 'cropped_image_data' not in st.session_state:
    st.session_state.cropped_image_data = None
if 'selected_color_rgb' not in st.session_state:
    st.session_state.selected_color_rgb = None
if 'selected_color_hsv' not in st.session_state:
    st.session_state.selected_color_hsv = None
if 'hsv_tolerances' not in st.session_state:
    st.session_state.hsv_tolerances = {'H': 4, 'S': 100, 'V': 100}
if 'erosion_iterations' not in st.session_state:
    st.session_state.erosion_iterations = 0
if 'dilation_iterations' not in st.session_state:
    st.session_state.dilation_iterations = 0
if 'detected_holds_components' not in st.session_state:
    st.session_state.detected_holds_components = None
if 'initial_holds' not in st.session_state:
    st.session_state.initial_holds = []
if 'final_hold' not in st.session_state:
    st.session_state.final_hold = None

# --- Configuration ---
MAX_IMAGE_WIDTH = 500 # pixels - adjust as needed
st.session_state.max_image_width = MAX_IMAGE_WIDTH # Always ensure this is set


# --- File Uploader ---
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "gif"])

if uploaded_file is not None:
    # Check if a new file is uploaded or if the file has changed
    if st.session_state.uploaded_image_info["name"] != uploaded_file.name:
        st.session_state.uploaded_image_info["name"] = uploaded_file.name
        st.session_state.uploaded_image_info["data"] = uploaded_file.getvalue()
        # Reset all relevant states for a new image
        st.session_state.clicks = []
        st.session_state.crop_points = []
        st.session_state.cropped_image_data = None
        st.session_state.selected_color_rgb = None
        st.session_state.selected_color_hsv = None
        st.session_state.hsv_tolerances = {'H': 4, 'S': 100, 'V': 100} # Reset tolerances
        st.session_state.erosion_iterations = 0
        st.session_state.dilation_iterations = 0
        st.session_state.detected_holds_components = None # Reset detected holds
        st.session_state.initial_holds = []
        st.session_state.final_hold = None
        st.rerun()

    # Load original image from session state data
    original_image = Image.open(BytesIO(st.session_state.uploaded_image_info["data"]))

    # --- 1. Image Cropping Section ---
    st.subheader("1. Faça o recorte da imagem")
    current_cropped_image_pil = image_cropper_component(original_image)
    
    if current_cropped_image_pil is not None:
        st.image(current_cropped_image_pil, caption="Imagem Cortada", width=st.session_state.max_image_width)

        # --- 2. Select Color from Cropped Image ---
        st.subheader("2. Selecione Uma Agarra")
        color_selector_component(current_cropped_image_pil)

        # Variáveis para armazenar a imagem filtrada e a máscara binária
        filtered_image_np_rgb = None
        binary_mask_np = None

        if st.session_state.selected_color_hsv:
            # --- 3. Filtro HSV ---
            st.subheader("3. Faça os ajustes de Filtro HSV")
            # hsv_filter_component agora retorna a imagem filtrada E a máscara
            filtered_image_np_rgb, binary_mask_np = hsv_filter_component(
                current_cropped_image_pil,
                st.session_state.selected_color_hsv,
                st.session_state.max_image_width
            )
        else:
            st.info("Por favor, selecione uma cor para habilitar o filtro HSV.")
        
        # --- 4. Identificação de Agarras (Chamada ao NOVO componente) ---
        if filtered_image_np_rgb is not None and binary_mask_np is not None:
            # Passamos a imagem cortada (PIL) e a máscara binária (NumPy)
            hold_segmentation_viewer_component(current_cropped_image_pil, binary_mask_np, st.session_state.max_image_width)
        else:
            st.info("Aguardando o filtro HSV para identificar as agarras.")

        # --- 5. Cliques Gerais na Imagem Cortada (Opcional - reindexado de 4 para 5) ---
        st.subheader("5. Seleção de Agarras Iniciais e Final")
        st.write("Clique em duas agarras iniciais e uma agarra final (a mais alta). Limite de 3 cliques.")

        general_click_coords = streamlit_image_coordinates(
            current_cropped_image_pil,
            key="cropped_image_for_general_clicks",
            width=st.session_state.max_image_width
        )
        if general_click_coords:
            clicked_x = general_click_coords['x']
            clicked_y = general_click_coords['y']
            
            if len(st.session_state.clicks) < 3:
                if not st.session_state.clicks or \
                   (st.session_state.clicks[-1][0] != clicked_x or st.session_state.clicks[-1][1] != clicked_y):
                    st.session_state.clicks.append((clicked_x, clicked_y))
                    st.toast(f"Clique registrado: ({clicked_x}, {clicked_y}). Total: {len(st.session_state.clicks)}/3")
                    if len(st.session_state.clicks) == 3:
                        # Sort clicks by y-coordinate to identify final hold
                        sorted_clicks = sorted(st.session_state.clicks, key=lambda p: p[1])
                        st.session_state.final_hold = sorted_clicks[0] # Highest point (smallest y-coordinate)
                        st.session_state.initial_holds = sorted_clicks[1:] # The other two are initial
                        st.success("Três agarras selecionadas! Agarras iniciais e final identificadas.")
            else:
                st.warning("Você já selecionou 3 agarras. Por favor, reinicie o processo para selecionar novamente.")

    # Exibir cliques gerais registrados
    if st.session_state.clicks:
        st.subheader("Cliques Registrados (na imagem cortada):")
        for i, (x, y) in enumerate(st.session_state.clicks):
            st.write(f"{i+1}. X: {x}, Y: {y}")
        
        if st.session_state.final_hold:
            st.write(f"**Agarra Final:** X: {st.session_state.final_hold[0]}, Y: {st.session_state.final_hold[1]}")
            st.write(f"**Agarras Iniciais:**")
            for i, (x, y) in enumerate(st.session_state.initial_holds):
                st.write(f"  {i+1}. X: {x}, Y: {y}")
    else:
        st.write("Nenhum clique geral registrado ainda na imagem cortada.")

    # --- 6. Rota Mais Rápida ---
    st.subheader("6. Rota Mais Rápida")
    if st.session_state.detected_holds_components and st.session_state.initial_holds and st.session_state.final_hold:
        if st.button("Calcular Rota Mais Rápida", key="calculate_route_button"):
            fastest_route = find_fastest_route(
                st.session_state.detected_holds_components,
                st.session_state.initial_holds,
                st.session_state.final_hold
            )

            if fastest_route:
                st.success("Rota mais rápida encontrada!")
                route_image = visualize_route(current_cropped_image_pil, fastest_route)
                st.image(route_image, caption="Rota Mais Rápida", width=st.session_state.max_image_width)
            else:
                st.warning("Não foi possível encontrar uma rota válida com as agarras selecionadas.")
    else:
        st.info("Por favor, complete as etapas 4 e 5 para calcular a rota mais rápida.")


else:
    st.info("Por favor, faça o upload de uma imagem.")
    # Limpar todo o estado da sessão se nenhum arquivo for carregado
    st.session_state.clicks = []
    st.session_state.crop_points = []
    st.session_state.cropped_image_data = None
    st.session_state.uploaded_image_info = {"name": None, "data": None}
    st.session_state.selected_color_rgb = None
    st.session_state.selected_color_hsv = None
    st.session_state.hsv_tolerances = {'H': 4, 'S': 100, 'V': 100}
    st.session_state.erosion_iterations = 0
    st.session_state.dilation_iterations = 0
    st.session_state.detected_holds_components = None
    st.session_state.initial_holds = []
    st.session_state.final_hold = None


st.sidebar.header("Sobre")
st.sidebar.info("Este aplicativo Streamlit demonstra um design modular para etapas de processamento de imagem.")

