import os
import json
import datetime

import piexif

current_path = os.path.abspath("/Users/lucifer/Downloads/takeout-test")
procesed_path = os.path.join(current_path,"processed")

def parse_json_files():
    file_list = os.scandir(current_path)

    for year_folder in file_list:
        if not year_folder.name.startswith('.'):
            print("processing folder: {0}".format(year_folder.name))
            with os.scandir(os.path.join(current_path,year_folder.name)) as it:
                for file in it:
                    if file.name.endswith(".json"):
                        json_file = None
                        with open(file.path) as f:
                            json_file = json.load(f)
                        exif_data = piexif.load(os.path.join(current_path, year_folder, json_file['title']))

                        if piexif.ImageIFD.DateTime in exif_data['0th']:
                            print("exif data already exists for image: {0}".format(os.path.join(current_path, year_folder, json_file['title'])))
                        else:
                            print("writing exif data...")
                            # extract time from json file
                            photo_time = datetime.datetime.fromtimestamp(int(json_file['photoTakenTime']['timestamp']))
                            # add the new time to the current exif dictionary
                            exif_data['0th'][piexif.ImageIFD.DateTime] = photo_time.strftime("%Y:%m:%d %H:%M:%S")
                            # write exif data to the image file
                            piexif.insert(piexif.dump(exif_data), os.path.join(current_path, year_folder, json_file['title']))
                            # move the processed json file away
                            os.renames(file.path, os.path.join(procesed_path, year_folder.name, file.name))


def parse_edited_files():
    file_list = os.scandir(current_path)

    for year_folder in file_list:
        if not year_folder.name.startswith('.'):
            with os.scandir(os.path.join(current_path,year_folder.name)) as _file_iter:
                for img_file in _file_iter:
                    if "-edited" in img_file.name:
                        piexif.transplant(img_file.path.replace("-edited", ""), img_file.path)

def main():
    print("initializing...")
    parse_json_files()
    parse_edited_files()

if __name__ == "__main__":
    main()