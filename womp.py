import os
from pathlib import Path
import imageio.v3 as iio
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx
import cv2
import os


def split_metalness_and_roughness():
    # Path to the directory containing the texture
    model_dir = "./default_womp_object"

    # Path to the input texture that combines metalness and roughness
    input_texture_path = os.path.join(model_dir, "model_0_metallicRoughness.png")

    # Load the image
    image = cv2.imread(input_texture_path, cv2.IMREAD_UNCHANGED)

    # Check if the image is loaded properly
    if image is None:
        raise ValueError("Image not found or the path is incorrect")

    # Split the image into its channels
    # OpenCV loads images in BGR format by default
    blue, green, red, alpha = cv2.split(image)

    # Save the metalness and roughness maps
    # Assume blue channel is metalness, green channel is roughness
    metalness_path = os.path.join(model_dir, "model_0_metalness.png")
    roughness_path = os.path.join(model_dir, "model_0_roughness.png")

    # Save channels as new images
    cv2.imwrite(metalness_path, blue)
    cv2.imwrite(roughness_path, green)

    print("Metalness and roughness maps have been saved.")

# create metalness and roughness as separate files
split_metalness_and_roughness()

# Initialize
canvas = WgpuCanvas(size=(640, 480), title="pygfx_womp")
renderer = gfx.renderers.WgpuRenderer(canvas)
scene = gfx.Scene()

# Load environment cube image and convert to 3D texture
env_img = iio.imread("imageio:meadow_cube.jpg")
cube_size = env_img.shape[1]
env_img.shape = 6, cube_size, cube_size, env_img.shape[-1]
env_tex = gfx.Texture(env_img, dim=2, size=(cube_size, cube_size, 6), generate_mipmaps=True)

# Create environment map and skybox
background = gfx.Background(None, gfx.BackgroundSkyboxMaterial(map=env_tex))
scene.add(background)

# Load additional textures
model_dir = "./default_womp_object"
color_texture = gfx.Texture(iio.imread(model_dir + "/model_0_color.png"),dim=2)
# Assuming metalness and roughness are packed in the same image, load them.
# If they are separate images, load them separately.
metallic_roughness_texture = gfx.Texture(iio.imread(model_dir + "/model_0_metallicRoughness.png"),dim=2)
# For simplicity, assume metalness is the blue channel and roughness is the green channel
metalness_map = gfx.Texture(iio.imread(model_dir + "/model_0_metalness.png"),dim=2)
roughness_map = gfx.Texture(iio.imread(model_dir + "/model_0_roughness.png"),dim=2)
transmittance_texture = gfx.Texture(iio.imread(model_dir + "/model_0_transmittance.png"),dim=2)

# Load mesh and assign textures
gltf_path = model_dir + "/Untitled 723050-Mesh 900474.gltf"
meshes = gfx.load_mesh(gltf_path)
scene.add(*meshes)
mesh = meshes[0]

# Assign additional textures to material using MeshStandardMaterial
material = gfx.MeshStandardMaterial(map=color_texture, env_map=env_tex)
material.roughness_map = roughness_map
material.metalness_map = metalness_map
material.emissive_map = transmittance_texture
mesh.material = material

# Additional scene setup
light = gfx.SpotLight(color="#ffffff")  # Adjusted light color for better visibility
light.local.position = (-500, 1000, -1000)
scene.add(light)

camera = gfx.PerspectiveCamera(45, 640 / 480)
camera.show_object(mesh, view_dir=(1.8, -0.6, -2.7))
controller = gfx.OrbitController(camera, register_events=renderer)

if __name__ == "__main__":
    renderer.request_draw(lambda: renderer.render(scene, camera))
    run()