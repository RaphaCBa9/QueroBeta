import streamlit as st
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

# Importa as funções de processamento de imagem
from utils.image_processing import bfs_segmentation, visualize_components_colored

def hold_segmentation_viewer_component(cropped_image_pil, binary_mask_np, max_display_width):
    """
    Componente Streamlit para segmentação de agarras (holds) e visualização.
    Args:
        cropped_image_pil (PIL.Image.Image): A imagem cortada (original para dimensão).
        binary_mask_np (numpy.ndarray): A máscara binária da imagem (255 para agarras, 0 para fundo).
        max_display_width (int): A largura máxima para exibir a imagem.
    Updates:
        st.session_state.detected_holds_components (list): Lista de componentes BFS encontrados.
    """
    st.subheader("4. Identificação de Agarras")

    # Botão para iniciar a segmentação. Colocado em uma coluna para melhor layout.
    if st.button("Identificar Agarras", key="identify_holds_button"):
        # A máscara binária já é o que precisamos para o BFS
        st.session_state.detected_holds_components = bfs_segmentation(binary_mask_np)
        st.toast("Agarras identificadas!")
        st.rerun() # Força um rerun para exibir os resultados após a detecção

    # Exibir os resultados da segmentação se houver agarras detectadas
    if st.session_state.get('detected_holds_components'):
        st.write("Agarras segmentadas (cada agarrara com uma cor diferente):")
        
        # Gerar a imagem colorida
        colored_components_image = visualize_components_colored(
            st.session_state.detected_holds_components,
            cropped_image_pil.size[::-1] # .size retorna (width, height), precisamos (height, width)
        )
        st.image(colored_components_image, caption="Agarras Identificadas", width=max_display_width)

        # Opcional: Exibir número de agarras e talvez um botão para "Reiniciar Identificação"
        if st.button("Reiniciar Identificação de Agarras", key="reset_holds_button"):
            st.session_state.detected_holds_components = None
            st.rerun()