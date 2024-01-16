import os
import shutil
from PIL import Image
from datetime import datetime



def main( source_folder = "source", destination_folder = "destination" ):

    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Function to extract the creation date from an image
    def get_image_creation_date(image_path):
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    date_taken = exif_data.get(36867)  # Tag for date and time original
                    if date_taken:
                        date_obj = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
                        return date_obj
        except Exception as e:
            print(f"Error extracting date from {image_path}: {e}")
        return None

    # Get today's date for images without date information
    today_date = datetime.now().strftime("%d-%m-%Y")

    # Iterate through the files in the source folder
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)
        
        # Check if it's a file and not a folder
        if os.path.isfile(source_path):
            # Get the creation date of the image
            date_taken = get_image_creation_date(source_path)
            
            if date_taken:
                # Create a subfolder in the destination folder based on the date
                destination_subfolder = date_taken.strftime("%d-%m-%Y")
                destination_path = os.path.join(destination_folder, destination_subfolder)
                
                # Create the subfolder if it doesn't exist
                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)
                
                # Move the image to the corresponding subfolder
                shutil.move(source_path, os.path.join(destination_path, filename))
                print(f"Moved {filename} to {destination_subfolder}")
            else:
                # Move the image to the "Today" folder if no date information is available
                today_path = os.path.join(destination_folder, today_date)
                
                # Create the "Today" folder if it doesn't exist
                if not os.path.exists(today_path):
                    os.makedirs(today_path)
                
                # Move the image to the "Today" folder
                shutil.move(source_path, os.path.join(today_path, filename))
                print(f"Moved {filename} to {today_date}")

    print("Done!")



if __name__ == "__main__":
    main()

