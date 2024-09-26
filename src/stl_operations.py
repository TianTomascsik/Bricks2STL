import numpy as np
from stl import mesh
import os
import file_operations

LDRAW_PATH = './'
save_directory = './'

def generate_circle_segments(center, radius, segments=100):
    """
    Generate vertices for a smooth circle in the specified plane.

    Parameters:
    center (array): The center of the circle.
    radius (float): The radius of the circle.
    segments (int): Number of segments to approximate the circle.

    Returns:
    list: A list of points forming the circle.
    """
    theta = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    circle_points = [(center[0] + radius * np.cos(t), center[1], center[2] + radius * np.sin(t)) for t in theta]
    return circle_points

def parse_ldraw_dat(content, transformations=None):
    """
    Parse the LDraw .dat file content and return vertices and faces.
    This function also considers sub-file references and transformations.
    """
    missing_parts = []

    if transformations is None:
        transformations = np.identity(4)

    vertices = []
    faces = []

    lines = content.splitlines()
    circle_approx_points = []

    for line in lines:
        parts = line.split()
        if len(parts) == 0:
            continue

        line_type = parts[0]

        if line_type == '0':  # Comment or META command
            continue

        elif line_type == '1':  # Sub-file reference
            color_code = int(parts[1])

            sub_transform = np.array([
                [float(parts[5]), float(parts[6]), float(parts[7]), float(parts[2])],
                [float(parts[8]), float(parts[9]), float(parts[10]), float(parts[3])],
                [float(parts[11]), float(parts[12]), float(parts[13]), float(parts[4])],
                [0, 0, 0, 1]
            ])

            new_transformations = transformations @ sub_transform

            subfile_name = parts[14].strip().replace('\\', '()')
            subfile_path = os.path.join(LDRAW_PATH, subfile_name)

            if os.path.isfile(subfile_path):
                with open(subfile_path, 'r') as subfile:
                    subfile_content = subfile.read()
                    sub_vertices, sub_faces = parse_ldraw_dat(subfile_content, new_transformations)

                    index_offset = len(vertices)
                    vertices.extend(sub_vertices)

                    for face in sub_faces:
                        if len(face) == 3:  # Only add triangles
                            faces.append((face[0] + index_offset, face[1] + index_offset, face[2] + index_offset))

            else:
                #print(f"Subfile {subfile_name} not found.")
                missing_parts.append(subfile_name)

        elif line_type == '2':  # Line (used for circle approximation)
            v1 = np.array([float(parts[2]), float(parts[3]), float(parts[4]), 1])
            v2 = np.array([float(parts[5]), float(parts[6]), float(parts[7]), 1])

            v1_transformed = transformations @ v1
            v2_transformed = transformations @ v2

            circle_approx_points.append((v1_transformed[:3], v2_transformed[:3]))

        elif line_type == '3':  # Triangle
            v1 = np.array([float(parts[2]), float(parts[3]), float(parts[4]), 1])
            v2 = np.array([float(parts[5]), float(parts[6]), float(parts[7]), 1])
            v3 = np.array([float(parts[8]), float(parts[9]), float(parts[10]), 1])

            v1_transformed = transformations @ v1
            v2_transformed = transformations @ v2
            v3_transformed = transformations @ v3

            vertices.extend([v1_transformed[:3], v2_transformed[:3], v3_transformed[:3]])
            faces.append((len(vertices) - 3, len(vertices) - 2, len(vertices) - 1))

        elif line_type == '4':  # Quadrilateral
            v1 = np.array([float(parts[2]), float(parts[3]), float(parts[4]), 1])
            v2 = np.array([float(parts[5]), float(parts[6]), float(parts[7]), 1])
            v3 = np.array([float(parts[8]), float(parts[9]), float(parts[10]), 1])
            v4 = np.array([float(parts[11]), float(parts[12]), float(parts[13]), 1])

            v1_transformed = transformations @ v1
            v2_transformed = transformations @ v2
            v3_transformed = transformations @ v3
            v4_transformed = transformations @ v4

            vertices.extend([v1_transformed[:3], v2_transformed[:3], v3_transformed[:3], v4_transformed[:3]])
            # Add two triangles to represent the quad
            faces.append((len(vertices) - 4, len(vertices) - 3, len(vertices) - 2))
            faces.append((len(vertices) - 4, len(vertices) - 2, len(vertices) - 1))

        elif line_type == '5':  # Optional Line
            v1 = np.array([float(parts[2]), float(parts[3]), float(parts[4]), 1])
            v2 = np.array([float(parts[5]), float(parts[6]), float(parts[7]), 1])
            v3 = np.array([float(parts[8]), float(parts[9]), float(parts[10]), 1])
            v4 = np.array([float(parts[11]), float(parts[12]), float(parts[13]), 1])

            v1_transformed = transformations @ v1
            v2_transformed = transformations @ v2
            v3_transformed = transformations @ v3
            v4_transformed = transformations @ v4

            vertices.extend([v1_transformed[:3], v2_transformed[:3]])

    # Replace circle approximation with smooth circle
    if circle_approx_points:
        center = np.mean([point[0] for point in circle_approx_points], axis=0)
        radius = np.linalg.norm(circle_approx_points[0][0] - center)

        # Generate a smooth circle
        circle_points = generate_circle_segments(center, radius, segments=100)

        # Clear out old vertices and faces related to the circle
        circle_vertex_start_index = len(vertices)
        vertices.extend(circle_points)

        # Add new faces (as quads, or you can use triangles if preferred)
        for i in range(len(circle_points)):
            next_index = (i + 1) % len(circle_points)
            faces.append((circle_vertex_start_index + i, circle_vertex_start_index + next_index))

    if len(missing_parts) != 0:
        file_operations.get_missing_parts(missing_parts)
        missing_parts = []
        parse_ldraw_dat(content, transformations)

    # Convert to numpy array ensuring all faces are triangles
    return np.array(vertices), np.array([face for face in faces if len(face) == 3])

def ldraw_to_stl(dat_filename, stl_filename):
    """
    Convert a .dat file to an STL file.
    """
    # check if the file is already downloaded
    dat_file_path = os.path.join(LDRAW_PATH, dat_filename)

    # Skip download if the file already exists
    if not os.path.isfile(dat_file_path):
        file_operations.get_dat_part(dat_filename)

    with open(dat_file_path, 'r') as file:
        content = file.read()

    vertices, faces = parse_ldraw_dat(content)

    vertices = np.array(vertices)
    faces = np.array([face for face in faces if len(face) == 3])  # Ensure only triangles are used

    # Create the mesh
    part_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            part_mesh.vectors[i][j] = vertices[face[j], :]

    # Write the mesh to file
    filename = './STL/' + stl_filename
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    part_mesh.save(filename)
    print(f"STL file '{stl_filename}' created successfully.")

def scale_stl(stl_filename, scaling_factor):
    """
    Scales the given STL file by the specified scaling factor.
    """
    print(stl_filename.replace("./STL/", ""))
    your_mesh = mesh.Mesh.from_file(stl_filename)
    your_mesh.vectors *= scaling_factor
    your_mesh.save(stl_filename)

def create_stl(vertices, faces, filename='output.stl'):
    """
    Create an STL file from the given vertices and faces.
    """
    vertices = np.array(vertices)
    faces = np.array([face for face in faces if len(face) == 3])  # Ensure only triangles are used

    # Create the mesh
    part_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            part_mesh.vectors[i][j] = vertices[face[j], :]

    # Write the mesh to file
    filename = './STL/' + filename
    part_mesh.save(filename)