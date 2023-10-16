import os
import shutil

# Define your paths
root_directory = os.getcwd()
input_csv_path = os.path.join(root_directory, 'FindSteve_csv.csv')
image_directory = os.path.join(root_directory, 'steve/')
output_directory = os.path.join(root_directory, 'steveannotations/')

# Create the required directories if they don't exist
os.makedirs(os.path.join(image_directory, 'images/train/'), exist_ok=True)
os.makedirs(os.path.join(image_directory, 'images/val/'), exist_ok=True)
os.makedirs(os.path.join(image_directory, 'labels/train/'), exist_ok=True)
os.makedirs(os.path.join(image_directory, 'labels/val/'), exist_ok=True)

# Move the images and labels to the right directories
# Assuming all images are for training, adjust accordingly if you have validation data

for filename in os.listdir(image_directory):
    if filename.endswith('.jpg') or filename.endswith('.png'):  # Add more image types if needed
        shutil.move(os.path.join(image_directory, filename), os.path.join(image_directory, 'images/train/', filename))
        
for filename in os.listdir(output_directory):
    if filename.endswith('.txt'):
        shutil.move(os.path.join(output_directory, filename), os.path.join(image_directory, 'labels/train/', filename))

print("Directory structure adjusted!")
