import csv
import os
from PIL import Image

def custom_eval(s):
    try:
        return eval(s.replace('undefined', 'None'))
    except:
        return None

# Set your paths
input_csv_path = 'FindSteve_csv.csv'
image_directory = 'steve/'
output_directory = 'steveannotations/'

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Define a dictionary for classes
class_dict = {"Steve Barry": 0}  # You can extend this dictionary as needed

with open(input_csv_path, 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)  # Skip the header
    
    for row in reader:
        filename = row[0]
        region_shape_attributes = custom_eval(row[5])
        region_attributes = custom_eval(row[6])

        # Skip rows without the necessary attributes
        if not region_shape_attributes or not region_attributes:
            continue
        
        if 'Steve Barry' in region_attributes and region_attributes['Steve Barry'] in class_dict:
            class_id = class_dict[region_attributes['Steve Barry']]
        else:
            continue

        # Open the image to get its size
        img_path = os.path.join(image_directory, filename)
        with Image.open(img_path) as img:
            width, height = img.size

        # Extract bounding box
        x = region_shape_attributes["x"]
        y = region_shape_attributes["y"]
        w = region_shape_attributes["width"]
        h = region_shape_attributes["height"]

        # Convert to YOLO format
        x_center = (x + w / 2) / width
        y_center = (y + h / 2) / height
        w_norm = w / width
        h_norm = h / height

        # Save to output .txt file
        output_filename = os.path.splitext(filename)[0] + '.txt'
        with open(os.path.join(output_directory, output_filename), 'a') as out_file:
            out_file.write(f"{class_id} {x_center} {y_center} {w_norm} {h_norm}\n")
