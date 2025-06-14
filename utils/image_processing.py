import numpy as np
import cv2
from collections import deque
from math import sqrt
from PIL import Image

def apply_hsv_filter(image_np_rgb, base_hsv_color, tol_h, tol_s, tol_v):
    """
    Applies an HSV color filter to an image.
    Args:
        image_np_rgb (numpy.ndarray): Input image as a NumPy array in RGB format.
        base_hsv_color (tuple): The base color (H, S, V) to filter around (OpenCV range).
        tol_h (int): Hue tolerance.
        tol_s (int): Saturation tolerance.
        tol_v (int): Value tolerance.
    Returns:
        numpy.ndarray: The filtered image as a NumPy array in RGB format,
                       where pixels outside the range are black.
    """
    # Convert the RGB image (NumPy array) to HSV
    image_hsv = cv2.cvtColor(image_np_rgb, cv2.COLOR_RGB2HSV)

    # Extract the H, S, V from the base color
    h, s, v = base_hsv_color
    h, s, v = int(h), int(s), int(v) # Ensure they are integers

    # Calculate min and max bounds for HSV
    min_h = np.clip(h - tol_h, 0, 179) # H is 0-179 in OpenCV
    max_h = np.clip(h + tol_h, 0, 179)
    min_s = np.clip(s - tol_s, 0, 255) # S is 0-255
    max_s = np.clip(s + tol_s, 0, 255)
    min_v = np.clip(v - tol_v, 0, 255) # V is 0-255
    max_v = np.clip(v + tol_v, 0, 255)

    # Create the lower and upper bounds for cv2.inRange
    lower_bound = np.array([min_h, min_s, min_v], dtype=np.uint8)
    upper_bound = np.array([max_h, max_s, max_v], dtype=np.uint8)

    # Generate the mask based on the HSV range
    mascara = cv2.inRange(image_hsv, lower_bound, upper_bound)

    # Create the result image: pixels within range keep original color, others become black
    resultado = np.zeros_like(image_np_rgb)
    resultado[mascara == 255] = image_np_rgb[mascara == 255]

    return resultado, mascara

def bfs_segmentation(binary_image):
    """
    Performs Breadth-First Search (BFS) to find connected components (agarras)
    in a binary image.
    Args:
        binary_image (numpy.ndarray): A 2D binary image (0 or 255).
    Returns:
        list: A list of lists, where each inner list contains (x, y) coordinates
              of pixels belonging to a connected component.
    """
    visited = np.zeros_like(binary_image, dtype=bool)
    height, width = binary_image.shape
    components = []

    # 4-directional connectivity
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y in range(height):
        for x in range(width):
            if binary_image[y, x] == 255 and not visited[y, x]:
                queue = deque()
                queue.append((y, x))
                component = []
                visited[y, x] = True

                while queue:
                    cy, cx = queue.popleft()
                    component.append((cx, cy)) # Store as (x, y)
                    for dy, dx in directions:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < height and 0 <= nx < width:
                            if binary_image[ny, nx] == 255 and not visited[ny, nx]:
                                visited[ny, nx] = True
                                queue.append((ny, nx))

                components.append(component)

    return components

def calculate_centroid(component):
    """
    Calculates the centroid (average x, y) of a connected component.
    Args:
        component (list): A list of (x, y) coordinates belonging to a component.
    Returns:
        tuple: (cx, cy) representing the centroid of the component.
    """
    if not component:
        return (0, 0) # Or handle error appropriately
    sum_x = sum(p[0] for p in component)
    sum_y = sum(p[1] for p in component)
    return (sum_x / len(component), sum_y / len(component))

def euclidean_distance(p1, p2):
    """
    Calculates the Euclidean distance between two points.
    Args:
        p1 (tuple): (x1, y1)
        p2 (tuple): (x2, y2)
    Returns:
        float: The Euclidean distance.
    """
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def find_fastest_route(all_holds_components, initial_holds_coords, final_hold_coord):
    """
    Finds the fastest route from initial holds to the final hold using a greedy approach.
    At each step, it selects the closest hold that is at an equal or higher altitude.
    Args:
        all_holds_components (list): List of all detected hold components (from bfs_segmentation).
        initial_holds_coords (list): List of (x, y) coordinates of the initial holds.
        final_hold_coord (tuple): (x, y) coordinate of the final hold.
    Returns:
        list: A list of (x, y) coordinates representing the fastest route,
              or None if no route is found.
    """
    if not all_holds_components or not initial_holds_coords or not final_hold_coord:
        return None

    hold_centroids = [calculate_centroid(comp) for comp in all_holds_components]

    def get_closest_hold_index(target_coord, centroids):
        min_dist = float("inf")
        closest_idx = -1
        for i, centroid in enumerate(centroids):
            dist = euclidean_distance(target_coord, centroid)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
        return closest_idx

    initial_hold_indices = [get_closest_hold_index(coord, hold_centroids) for coord in initial_holds_coords]
    final_hold_index = get_closest_hold_index(final_hold_coord, hold_centroids)

    if final_hold_index == -1 or any(idx == -1 for idx in initial_hold_indices):
        print("Erro: Não foi possível mapear as agarras selecionadas pelo usuário para as agarras detectadas.")
        return None

    best_greedy_route = None
    min_greedy_distance = float("inf")

    # Try building a greedy path from each initial hold
    for start_hold_idx in initial_hold_indices:
        print(f"\n--- Iniciando caminho guloso da agarra inicial: {hold_centroids[start_hold_idx]} ---")
        current_greedy_route = [hold_centroids[start_hold_idx]]
        current_greedy_distance = 0
        visited_indices = {start_hold_idx} # To avoid cycles and redundant visits
        current_hold_idx = start_hold_idx

        step_count = 0
        while current_hold_idx != final_hold_index:
            step_count += 1
            print(f"Passo {step_count}: Agarra atual: {hold_centroids[current_hold_idx]} (Índice: {current_hold_idx})")
            print(f"  Agarras visitadas: {visited_indices}")
            
            next_hold_idx = -1
            min_dist_to_next = float("inf")
            
            potential_neighbors = []
            for neighbor_idx, neighbor_centroid in enumerate(hold_centroids):
                if neighbor_idx == current_hold_idx or neighbor_idx in visited_indices:
                    continue
                potential_neighbors.append((neighbor_idx, neighbor_centroid))
            
            print(f"  Vizinhos potenciais (não visitados): {len(potential_neighbors)}")
            for idx, centroid in potential_neighbors:
                print(f"    - Potencial: {centroid} (Índice: {idx}, Y: {centroid[1]:.2f})")
            
            valid_neighbors_altitude_filtered = []
            for neighbor_idx, neighbor_centroid in potential_neighbors:
                # Condition: next hold must be at a lower or equal y-coordinate (higher or equal altitude)
                # In image coordinates, lower Y means higher on the image.
                # So, neighbor_centroid[1] (y) should be <= current_hold_idx's y
                if neighbor_centroid[1] <= hold_centroids[current_hold_idx][1]:
                    dist = euclidean_distance(hold_centroids[current_hold_idx], neighbor_centroid)
                    valid_neighbors_altitude_filtered.append((dist, neighbor_idx, neighbor_centroid))
            
            print(f"  Vizinhos válidos (filtrados por altitude): {len(valid_neighbors_altitude_filtered)}")
            for dist, idx, centroid in valid_neighbors_altitude_filtered:
                print(f"    - Válido: {centroid} (Índice: {idx}, Y: {centroid[1]:.2f}, Dist: {dist:.2f})")
            
            if valid_neighbors_altitude_filtered:
                # Sort by distance to find the closest
                valid_neighbors_altitude_filtered.sort(key=lambda x: x[0])
                min_dist_to_next, next_hold_idx, next_hold_centroid = valid_neighbors_altitude_filtered[0]
                print(f"  Próxima agarra selecionada: {next_hold_centroid} (Índice: {next_hold_idx}) com distância {min_dist_to_next:.2f}")
            else:
                print("  Nenhuma agarra válida encontrada para o próximo passo. Caminho travado.")
                current_greedy_route = None
                break # Exit while loop if no valid next hold

            current_greedy_route.append(hold_centroids[next_hold_idx])
            current_greedy_distance += min_dist_to_next
            visited_indices.add(next_hold_idx)
            current_hold_idx = next_hold_idx

        if current_greedy_route and current_hold_idx == final_hold_index:
            print(f"  Caminho para a agarra final encontrado! Distância total: {current_greedy_distance:.2f}")
            if current_greedy_distance < min_greedy_distance:
                min_greedy_distance = current_greedy_distance
                best_greedy_route = current_greedy_route
        elif current_greedy_route is None:
            print("  Caminho não chegou à agarra final (travado).")
        else:
            print(f"  Caminho terminou, mas a agarra final não foi alcançada. Última agarra: {hold_centroids[current_hold_idx]}")

    print(f"\n--- Melhor rota gulosa encontrada: {best_greedy_route} ---")
    return best_greedy_route

def visualize_components_colored(components, image_shape):
    """
    Creates an image where each connected component is colored differently.
    Args:
        components (list): List of connected components (from bfs_segmentation).
        image_shape (tuple): The (height, width) of the original image.
    Returns:
        numpy.ndarray: An RGB image with components colored.
    """
    result = np.zeros((image_shape[0], image_shape[1], 3), dtype=np.uint8)
    
    # Generate distinct colors. More colors can be added or generated programmatically.
    cores = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),       # Red, Green, Blue
        (255, 255, 0), (255, 0, 255), (0, 255, 255), # Yellow, Magenta, Cyan
        (128, 0, 0), (0, 128, 0), (0, 0, 128),       # Darker shades
        (128, 128, 0), (128, 0, 128), (0, 128, 128),
        (255, 128, 0), (0, 255, 128), (128, 0, 255), # Orange, Spring Green, Purple
        (128, 255, 0), (0, 128, 255), (255, 0, 128), # Lime Green, Sky Blue, Rose
        (75, 0, 130), (0, 100, 0), (255, 165, 0) # Indigo, Dark Green, Orange
    ]

    for idx, comp in enumerate(components):
        # Use modulo to cycle through colors if there are more components than predefined colors
        cor = cores[idx % len(cores)]
        for x, y in comp:
            if 0 <= y < image_shape[0] and 0 <= x < image_shape[1]: # Basic bounds check
                result[y, x] = cor
            
    return result

def visualize_route(image_pil, route_coords):
    """
    Visualizes the fastest route on the image, marking holds with numbers.
    Args:
        image_pil (PIL.Image.Image): The original image (cropped).
        route_coords (list): List of (x, y) coordinates representing the route.
    Returns:
        PIL.Image.Image: Image with the route drawn.
    """
    if not route_coords:
        return image_pil

    image_np = np.array(image_pil.convert("RGB"))
    output_image = image_np.copy()

    # Draw lines between consecutive holds and number them
    for i in range(len(route_coords)):
        x, y = int(route_coords[i][0]), int(route_coords[i][1])
        
        # Draw circle for the hold
        cv2.circle(output_image, (x, y), 10, (255, 0, 0), -1) # Red circle

        # Put number on the hold
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        text = str(i + 1)
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x = x - text_size[0] // 2
        text_y = y + text_size[1] // 2
        cv2.putText(output_image, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

        # Draw line to next hold
        if i < len(route_coords) - 1:
            next_x, next_y = int(route_coords[i+1][0]), int(route_coords[i+1][1])
            cv2.line(output_image, (x, y), (next_x, next_y), (0, 255, 0), 2) # Green line

    return Image.fromarray(output_image)


