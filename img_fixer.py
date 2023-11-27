import os
import json
import datetime

import piexif

current_path = os.path.abspath("/Users/lucifer/Downloads/takeout-test")
procesed_path = os.path.join(current_path,"processed")
skipped_path = os.path.join(current_path, "skipped")
edit_path = os.path.join(current_path, "edited")

def parse_json_files():
    file_list = os.scandir(current_path)

    for year_folder in file_list:
        if year_folder.name.startswith("Photos from "):
            print("processing folder: {0}".format(year_folder.name))
            with os.scandir(os.path.join(current_path,year_folder.name)) as it:
                for file in it:
                    if file.name.endswith(".json") and file.name != 'metadata.json':
                        json_file = None
                        with open(file.path) as f:
                            json_file = json.load(f)
                        try:
                            exif_data = piexif.load(os.path.join(current_path, year_folder.name, json_file['title']))
                        except FileNotFoundError:
                            os.renames(file.path, os.path.join(procesed_path, year_folder.name, file.name))
                            continue
                        except piexif._exceptions.InvalidImageDataError:
                            os.renames(file.path, os.path.join(procesed_path, year_folder.name, file.name))
                            continue

                        if piexif.ImageIFD.DateTime in exif_data['0th']:
                            if "-" in str(exif_data["0th"][piexif.ImageIFD.DateTime].decode()):
                                existing_date = datetime.datetime.strptime(exif_data["0th"][piexif.ImageIFD.DateTime].decode(), "%Y-%m-%d %H:%M:%S")
                            else:
                                existing_date = datetime.datetime.strptime(exif_data["0th"][piexif.ImageIFD.DateTime].decode(), "%Y:%m:%d %H:%M:%S")
                            photo_time = datetime.datetime.fromtimestamp(int(json_file['photoTakenTime']['timestamp']))
                            if existing_date > photo_time:
                                exif_data['0th'][piexif.ImageIFD.DateTime] = photo_time.strftime("%Y:%m:%d %H:%M:%S")
                                try:
                                    piexif.insert(piexif.dump(exif_data), os.path.join(current_path, year_folder, json_file['title']))
                                except ValueError:
                                    pass
                                os.renames(file.path, os.path.join(procesed_path, year_folder.name, file.name))
                            else:
                                os.renames(file.path, os.path.join(skipped_path, year_folder.name, file.name))

                        else:
                            photo_time = datetime.datetime.fromtimestamp(int(json_file['photoTakenTime']['timestamp']))
                            exif_data['0th'][piexif.ImageIFD.DateTime] = photo_time.strftime("%Y:%m:%d %H:%M:%S")
                            piexif.insert(piexif.dump(exif_data), os.path.join(current_path, year_folder, json_file['title']))
                            os.renames(file.path, os.path.join(procesed_path, year_folder.name, file.name))
                    else:
                        pass


def parse_edited_files():
    file_list = os.scandir(current_path)

    for year_folder in file_list:
        if not year_folder.name.startswith('.'):
            with os.scandir(os.path.join(current_path,year_folder.name)) as _file_iter:
                for img_file in _file_iter:
                    if "-edited" in img_file.name:
                        try:
                            piexif.transplant(img_file.path.replace("-edited", ""), img_file.path)
                            os.renames(img_file.path.replace("-edited", ""), os.path.join(edit_path, year_folder.name, img_file.name.replace("-edited", "")))
                        except FileNotFoundError:
                            pass
                        except piexif._exceptions.InvalidImageDataError:
                            break

def main():
    print("initializing...")
    parse_json_files()
    parse_edited_files()

if __name__ == "__main__":
    main()