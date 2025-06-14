# Projeto de Reconhecimento de Rotas de Bouldering

Este projeto utiliza visão computacional para identificar agarras em uma parede de escalada e determinar a rota mais rápida até o topo.

---

## 1. Configuração do Ambiente Virtual

É altamente recomendável criar um ambiente virtual para isolar as dependências do projeto.

1. **Navegue até o diretório do projeto:**
    ```bash
    cd /caminho/para/seu/projeto
    ```
2. **Crie o ambiente virtual:**
    ```bash
    python3 -m venv venv
    ```
3. **Ative o ambiente virtual:**
    - **Linux/macOS:**
      ```bash
      source venv/bin/activate
      ```
    - **Windows (Command Prompt):**
      ```bash
      venv\Scripts\activate.bat
      ```
    - **Windows (PowerShell):**
      ```powershell
      venv\Scripts\Activate.ps1
      ```

## 2. Instalação das Dependências

Com o ambiente virtual ativado, instale as bibliotecas listadas em `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 3. Como Rodar o Aplicativo

Este projeto utiliza o **Streamlit** para interface gráfica.

1. Certifique-se de que o ambiente virtual está ativado.
2. Execute:
    ```bash
    streamlit run app.py
    ```
3. Abra o navegador no endereço exibido no terminal (Local URL / Network URL).

---

## 4. Fluxo de Etapas do Usuário

### Etapa 0: Upload da Foto da Parede

* **Objetivo:** Carregar imagem da parede de escalada.
* **Ação:** Clique em **Choose an image...** e selecione o arquivo.

### Etapa 1: Recorte da Imagem (Cropping)

* **Objetivo:** Isolar a área da rota.
* **Ação:** Desenhe um retângulo e clique em **Crop Image**.

### Etapa 2: Seleção de Cor da Agarra

* **Objetivo:** Definir referência de cor para detecção.
* **Ação:** Clique sobre uma agarra; a cor RGB/HSV é exibida.

### Etapa 3: Ajuste de Máscara HSV e Operações Morfológicas

* **Objetivo:** Refinar segmentação das agarras para melhorar a precisão e remover ruídos.
* **Parâmetros disponíveis e seus efeitos:**
  - **H (Hue):**
    - **O que afeta:** Define a faixa de tonalidades (cores) que serão identificadas.
    - **Efeito de aumentar/diminuir:** Ao aumentar o valor mínimo ou máximo, você expande a seleção para incluir mais matizes (ex.: mais tons de vermelho ou verde). Reduzir estreita a faixa, capturando somente a cor mais pura.
  - **S (Saturation):**
    - **O que afeta:** Controla a intensidade da cor selecionada.
    - **Efeito de aumentar:** Captura cores mais vívidas e saturadas, eliminando tons mais acinzentados.
    - **Efeito de diminuir:** Inclui cores mais dessaturadas, mas pode adicionar ruídos de áreas menos coloridas.
  - **V (Value):**
    - **O que afeta:** Regula o brilho das regiões segmentadas.
    - **Efeito de aumentar:** Inclui áreas mais claras, permitindo captar agarras bem iluminadas.
    - **Efeito de diminuir:** Filtra regiões claras, focando em agarras mais escuras, útil para reduzir reflexos.
  - **Erosão:**
    - **O que afeta:** Remove pequenos artefatos (pontinhos soltos) na máscara.
    - **Efeito de aumentar elementos de erosão:** Reduz áreas finas e pequenos ruídos, mas pode encurtar os contornos das agarras.
  - **Dilatação:**
    - **O que afeta:** Expande regiões segmentadas, conectando fragmentos próximos.
    - **Efeito de aumentar elementos de dilatação:** Preenche buracos e conecta partes desconexas das agarras, mas pode unir agarras muito próximas.

* **Ação:** Ajuste os sliders até que a máscara destaque apenas as agarras desejadas, sem ruídos ou áreas desconectadas. Combine erosão e dilatação para obter contornos limpos e completos.

### Etapa 4: Identificação e Visualização das Agarras

* **Objetivo:** Detectar contornos das agarras e numerá-las.
* **Ação:** Observe as agarras segmentadas exibidas com bounding boxes e o contador atualizado.

### Etapa 5: Seleção de Pontos Iniciais e Final

* **Objetivo:** Definir ponto de partida (duas agarras iniciais) e ponto de chegada (agarras de topo).
* **Ação:** Clique em três agarras na ordem desejada.

### Etapa 6: Cálculo da Rota Mais Rápida

* **Objetivo:** Traçar a rota ótima conectando as agarras selecionadas.
* **Ação:** Clique em **Calcular Rota Mais Rápida**; a sequência numerada aparecerá sobre a imagem.

---