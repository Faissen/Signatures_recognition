# Importing necessary libraries
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance # For image creation and drawing
from faker import Faker # For generating random names
import numpy as np # For numerical operations
import random # For generating random positions and font sizes
import os # For file path operations
import json # For saving metadata

fake = Faker() # generates random names
name_map = {} # Dictionary to map filenames to names

# Directory to save generated signatures
OUTPUT_DIR = "generated_signatures"
os.makedirs(OUTPUT_DIR, exist_ok=True) # Create directory if it doesn't exist

# Choose a cursive font from Windows
FONT_PATH = "C:/Windows/Fonts/seguisbi.ttf" 

# Function to add noise and distortions to the image
def add_noise(img):
    # Convert to numpy array to manipulate pixels
    arr = np.asarray(img, dtype=np.int16) 
    
    # Gaussian noise  is added with 70% probability
    if random.random() < 0.7:
        noise = np.random.normal(0, 15, arr.shape) # Mean 0, stddev 15
        arr = arr + noise # Add noise to the image array
    # Speckle noise is added with 50% probability
    if random.random() < 0.5:
        # Speckle noise is multiplicative of the image
        speckle = arr * (1 + np.random.randn(*arr.shape) * 0.1)
        arr = speckle 
    
    # Clip values back to valid range 
    arr = np.clip(arr, 0, 255).astype(np.uint8) # Convert back to uint8 to form an image
    noisy_img = Image.fromarray(arr) # Convert back to PIL Image
    
    # Random blur 
    if random.random() < 0.5:
        # Apply Gaussian blur to simulate pen smudges
        noisy_img = noisy_img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5))) 
        # Random contrast change to simulate ink variations
    if random.random() < 0.5: 
        enhancer = ImageEnhance.Contrast(noisy_img) # Create contrast enhancer to adjust contrast
        noisy_img = enhancer.enhance(random.uniform(0.7, 1.3)) # Random contrast factor 
    
    return noisy_img


# Function to generate a signature image
def generate_signature(text, filename): 
    img = Image.new("RGB", (600, 200), "white") # Create a blank white image
    draw = ImageDraw.Draw(img) # Prepare to draw on the image
    
    font_size = random.randint(40, 70) # Random font size between 40 and 70
    font = ImageFont.truetype(FONT_PATH, font_size)  # Load the font
    
    x = random.randint(10, 50) # Random x position
    y = random.randint(20, 80) # Random y position
    
    draw.text((x, y), text, font=font, fill="black") # Draw the text on the image
    
    img = img.rotate(random.randint(-10, 10), expand=1, fillcolor="white") 
    # Slightly rotate the image for realism
    # Random angle between -10 and 10 degrees
    # Expand=1 to adjust the image size after rotation
    
    img.save(os.path.join(OUTPUT_DIR, filename)) # Save the image

    # Add noise 
    img = add_noise(img)
    img.save(os.path.join(OUTPUT_DIR, filename)) # Save the noisy image in the same file

# Generate 200 signatures with random names 
for i in range(200): 
    name = fake.name() # random name 
    filename = f"signature_{i+1}.png" # Filename for the signature image
    generate_signature(name, filename) # Generate and save the signature image
    name_map[filename] = name # Map filename to the generated name

# Save the name mapping to a JSON file
# Encoding to ensure UTF-8 support, mode w for writing
with open("signature_names.json", "w", encoding="utf-8") as f:
    # indent for readability, ensure_ascii for UTF-8 support
    json.dump(name_map, f, indent=4, ensure_ascii=False) 

print("Saved name mapping to signature_names.json")

print("200 random signatures generated successfully!")
