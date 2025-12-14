from PIL import Image
import os

def create_icon(input_image_path, output_icon_path='app_icon.ico', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]):
    """
    Convert an image to .ico format with multiple sizes
    
    Args:
        input_image_path: Path to the input image
        output_icon_path: Path where to save the .ico file
        sizes: List of sizes to include in the .ico file
    """
    try:
        # Open the image
        img = Image.open(input_image_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create a list to store the resized images
        icon_sizes = []
        
        # Resize the image for each size
        for size in sizes:
            resized_img = img.resize(size, Image.LANCZOS)
            icon_sizes.append(resized_img)
        
        # Save as .ico file
        icon_sizes[0].save(
            output_icon_path,
            format='ICO',
            sizes=[(s.width, s.height) for s in icon_sizes],
            quality=100
        )
        
        print(f"Successfully created icon file: {output_icon_path}")
        print(f"Icon file size: {os.path.getsize(output_icon_path)} bytes")
        return True
        
    except Exception as e:
        print(f"Error creating icon: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    input_image = input("Enter the path to your image file: ").strip('"')
    if os.path.exists(input_image):
        create_icon(input_image)
    else:
        print("File not found. Please check the path and try again.") 