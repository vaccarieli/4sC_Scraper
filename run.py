import img2pdf
from pathlib import Path
import json
import os
import shutil
import re
import traceback
import json
import cv2
import img2pdf
from pathlib import Path



def get_config_book_data(book_path) -> dict:
    # Read the JavaScript file
    with open(book_path / "config.js", "r", encoding="utf-8") as file:
        js_content = file.read()

        # Use regex to find all occurrences of the variable
        pattern = r'var BOOK_CONFIG = ({.*?});'
        matches = re.findall(pattern, js_content, re.DOTALL)

    # Parse each JSON string into a Python dictionary
    return [json.loads(match) for match in matches][0]


def create_book(book_code):
    book_data = {}
    chapter_ranges = {}

    book_path = Path(f'C:/Users/{os.getlogin()}/AppData/Local/Packages/ASC.ASC_yndy5v4xq42h4/LocalState/downloads/BOOK/{book_code}')
    output_path = Path("D:/English Teaching Content")
    config_book_data = get_config_book_data(book_path)


    for book_content_type in ["Libro del Alumno"]: #"Student's Book", "Teacher's Notes", 
        # book_content_type = "Student's Material"
        book_level, book_number = "", ""

        if book_content_type  == "Student's Book":
            prefix = "sb_"
            book_level = config_book_data["pages"][0]["URL"].split("_")[2].replace("lv", "Level ")
            book_number = config_book_data["pages"][0]["URL"].split("_")[3].replace("book", "Book ")

        elif book_content_type == "Teacher's Notes":
            prefix = "tn_"
            book_level = config_book_data["pages"][0]["URL"].split("_")[2].replace("lv", "Level ")
            book_number = config_book_data["pages"][0]["URL"].split("_")[3].replace("book", "Book ")

        elif book_content_type == "Libro del Alumno":
            # print(config_book_data["pages"][0]["URL"])
            if "nv" in config_book_data["pages"][0]["URL"].split("_")[3]:
                book_level = config_book_data["pages"][0]["URL"].split("_")[3].replace("nv", "Nivel ")
                prefix = ""
                # print(config_book_data["pages"][0]["URL"])
                # primef_la_9rev_nv1_trim1_book_portada.jpg

            elif "lv" in config_book_data["pages"][0]["URL"].split("_")[2]:
                book_level = config_book_data["pages"][0]["URL"].split("_")[2].replace("lv", "Nivel ")
                prefix = "tn_"
                continue
                # tn_ffe_lv1_book1_9ed_00.jpg
                # print(config_book_data["pages"][0]["URL"])

            elif "nv" in config_book_data["pages"][0]["URL"].split("_")[1]:
                book_level = config_book_data["pages"][0]["URL"].split("_")[1].replace("nv", "Nivel ")
                prefix = ""
            
            else:
                book_level = config_book_data["pages"][0]["URL"].split("_")[3].replace("niv", "Nivel ")
                prefix = ""

                # primef_nv4_libro1_9rev_app_00.jpg
                # primef_nv5_libro1_9rev_app_00.jpg
                # primef_nv4_libro2_9rev_app_00.jpg
                # primef_nv5_libro2_9rev_app_00.jpg
                # eefprim_9rev_trim2_niv6_la_book_portada.jpg
                # eefprim_9rev_trim3_niv2_la_book_0_portada.jpg
                # primef_nv4_libro3_9rev_app_00.jpg
                # primef_nv5_libro3_9rev_app_00.jpg
                # eefprim_9rev_trim3_niv6_la_book_0_portada.jpg
                # print(config_book_data["pages"][0]["URL"])

            if "trim" in config_book_data["pages"][0]["URL"].split("_")[4]:
                book_number = config_book_data["pages"][0]["URL"].split("_")[4].replace("trim", "Libro ")
                # print(config_book_data["pages"][0]["URL"])
                # primef_la_9rev_nv1_trim1_book_portada.jpg

            elif "book" in config_book_data["pages"][0]["URL"].split("_")[3]:
                book_number = config_book_data["pages"][0]["URL"].split("_")[3].replace("book", "Libro ")
                continue
                # tn_ffe_lv1_book1_9ed_00.jpg
                # print(config_book_data["pages"][0]["URL"])

            elif "libro" in config_book_data["pages"][0]["URL"].split("_")[2]:
                book_number = config_book_data["pages"][0]["URL"].split("_")[2].replace("libro", "Libro ")
                # primef_nv4_libro1_9rev_app_00.jpg
                # primef_nv5_libro1_9rev_app_00.jpg
                # eefprim_9rev_trim2_nv2_la_portada.jpg
                # primef_nv4_libro2_9rev_app_00.jpg
                # primef_nv5_libro2_9rev_app_00.jpg
                # eefprim_9rev_trim2_niv6_la_book_portada.jpg
                # eefprim_9rev_trim3_niv2_la_book_0_portada.jpg
                # primef_nv4_libro3_9rev_app_00.jpg
                # primef_nv5_libro3_9rev_app_00.jpg
                # eefprim_9rev_trim3_niv6_la_book_0_portada.jpg
                # print(config_book_data["pages"][0]["URL"])
                # "eefprim_9rev_trim2_nv2_la_portada.jpg"


            else:
                book_number = config_book_data["pages"][0]["URL"].split("_")[2].replace("trim", "Libro ")

            
        if not book_level and not book_number:
            continue

        # parse config book data
        school_level = config_book_data["type"].capitalize()

        book_level_path = output_path / school_level / book_number / book_level
        material_path = book_level_path / "Material"

        # make directories
        if not book_level_path.exists():
            os.makedirs(book_level_path)

        if not material_path.exists():
            os.makedirs(material_path)

        # print(json.dumps(config_book_data, indent=4)) 

        # print(book_level, book_number)

        for dat in config_book_data["menuItems"]:
            bookType = dat["text"]

            if bookType == "Libro del alumno":
                bookType = "Libro del Alumno"

            if bookType == book_content_type:
                book_data[bookType] = {"Fundamentals": []}
                try:
                    contents = dat["children"]
                except Exception:
                    pass

                for contentOut in contents:
                    try:
                        contentsIn = contentOut["children"]
                        chapter_name = contentOut["text"]

                        if book_content_type not in ["Libro del Alumno"]:
                            # Store the chapter range separately // Compatible with English Book not Spanish
                            chapter_ranges[chapter_name] = f'{contentsIn[0]["URL"][:-4].split("_")[-1]}-{contentsIn[-1]["URL"][:-4].split("_")[-1]}'

                            # Initialize each chapter with an empty list in book_data
                            book_data[bookType][chapter_name] = []

                        else:
                            try:
                                if "Unidad" in chapter_name:
                                    
                                    chapter_ranges[chapter_name] = contentsIn[0]["URL"][:-4].split("_")[-1]
                                else:
                                    chapter_ranges[chapter_name] = contentsIn[0]["children"][0]["URL"][:-4].split("_")[-1]

                                # Initialize each chapter with an empty list in book_data
                                book_data[bookType][chapter_name] = []
                                
                            except KeyError:
                                pass
                            # print(contentsIn[1]["children"])
                            # new_list = [contentsIn[0]["URL"]]
                            # for children in contentsIn[1]["children"]:
                            #     new_list.append(children["URL"])
                    except Exception:
                        pass
                        # traceback.print_exc()
                        # sys.exit()


        # Edit the props chapter ranges for spanish books
        if book_content_type in ["Libro del Alumno"]:
            for index, (key, val) in enumerate(chapter_ranges.items()):
                try:
                    chapter_ranges[key] =f'{val}-{int(list(chapter_ranges.values())[index+1])-1}'
                except Exception:
                    pass
        
        chapter_index = 1
        chapter_read = False

        if "Fundamentals" in chapter_ranges:
            del chapter_ranges["Fundamentals"]

        print(chapter_ranges)

        # {'Unidad 1': '7-26', 'Unidad 2': '27-46', 'Unidad 3': '47-66', 
        #  'Unidad 4': '67-86', 'Unidad 5': '87-106', 'Unidad 6': '107-127', 
        #  'Unidad 7': '128-146', 'Unidad 8': '147-165', 'Lecturas de comprensión': '166'}

        # { "Fundamentals": '0-6',
        #     'Unidad 1': '7-26', 'Unidad 2': '27-46', 'Unidad 3': '47-66', 
        #  'Unidad 4': '67-86', 'Unidad 5': '87-106', 'Unidad 6': '107-127',
        #   'Unidad 7': '128-146', 'Unidad 8': '147-165', 
        #   'Lecturas de comprensión': '166-178'}

        for dat in config_book_data["pages"]:
            if dat["URL"].endswith(".jpg") and dat["URL"].startswith(prefix):
                # Retrieve chapter bounds using chapter_ranges dictionary
                
                if not chapter_read:
                    if book_content_type in ["Libro del Alumno"]:  #, "Libro del Maestro"
                        
                        chapter_name = f"Unidad {chapter_index}"
                    else:
                        chapter_name = f"Chapter {chapter_index}"
                    try:
                        from_chapter, to_chapter = map(int, chapter_ranges[chapter_name].split("-"))
                        
                    except KeyError:
                        break

                    chapter_read = True
                
                try:
                    page_number = int(dat["URL"][:-4].split("_")[-1]) if dat["URL"][:-4].split("_")[-1] != "portada" else 0
                except ValueError:
                    page_number = dat["URL"][:-4].split("_")[-1]

                if page_number == to_chapter:
                    chapter_index += 1
                    chapter_read = False

                try:
                    if page_number < from_chapter:
                        misc_data = []
                        if dat.get("attachments", False):
                            for dat_attachment in dat["attachments"]:
                                if dat_attachment["type"] == "gallery":
                                    for image in dat_attachment["images"]:
                                        misc_data.append(image)
                                else:
                                    misc_data.append(dat_attachment["URL"])

                        if {"path":dat["URL"], "misc": misc_data} not in book_data[book_content_type]["Fundamentals"]:
                            book_data[book_content_type]["Fundamentals"].append({"path":dat["URL"], "misc": misc_data})

                    else:
                        misc_data = []
                        if dat.get("attachments", False):
                            for dat_attachment in dat["attachments"]:
                                if dat_attachment["type"] == "gallery":
                                    for image in dat_attachment["images"]:
                                        misc_data.append(image)
                                else:
                                    misc_data.append(dat_attachment["URL"])

                        if {"path":dat["URL"], "misc": misc_data} not in book_data[book_content_type][chapter_name]:
                            book_data[book_content_type][chapter_name].append({"path":dat["URL"], "misc": misc_data})

                except TypeError:
                    # import sys
                    book_data[book_content_type][chapter_name].append({"path":dat["URL"], "misc": misc_data})
                    # print(json.dumps(book_data, indent=4)) 
                    # sys.exit()
                
        
        sorted_book = {}
        
        try:
            for content in book_data[book_content_type].keys():
                sorted_book[content] = []
                for page in book_data[book_content_type][content]:
                    sorted_book[content].append((book_path / page["path"]))

                    #copy media to folder where the pdfs chapter will be created
                    miscs = page["misc"]
                    page_number = page["path"][:-4].split("_")[-1]

                    if miscs: # create dirs to every page that has materials available
                        # copy the materials to each folder page 
                        for misc in miscs:
                            if misc and misc != "@" and ".html" not in misc and "https:" not in misc:
                                _, file_extension = os.path.splitext(misc)
                                new_file_name = f"{book_number} - {book_level} - {content} - Page {int(page_number)-12}{file_extension}" if not file_extension == ".jpg" else f"{book_number} - {book_level} - {content} - Page {int(page_number)-12} - Recortable - {misc.split("_")[-1]}"
                                material_page_path = material_path / f"Page {int(page_number)-12}" 

                                if not material_page_path.exists():
                                    os.makedirs(material_page_path)

                                if not (material_page_path / new_file_name).exists():
                                    index = 0
                                    first_passed = False
                                    tempMisc = misc.replace("-recortable", "_recortable").replace(" dictionary", "_dictionary").replace(" development", "_development")
                                    while True:
                                        try:
                                            shutil.copy(book_path / tempMisc, material_page_path / new_file_name)
                                            break
                                        except Exception:
                                            if index == 0 and not first_passed:
                                                tempMisc = misc.replace("_recortable", "-recortable")
                                                first_passed = True
                                                continue
                                            print(book_code, "Failed copying file: ", tempMisc)
                                            traceback.print_exc()
                                            filename, file_extension = os.path.splitext(misc)
                                            tempMisc = (filename + str(index) + file_extension)
                                            index+=1


                # print(json.dumps(book_data, indent=4))      

                # Define letter size in pixels (assuming 300 DPI)
                LETTER_SIZE = (2550, 3300)  # (width, height) in pixels for 8.5x11 inches at 300 DPI

                output_pdf = book_level_path / f"{book_content_type} - {book_number} - {book_level} - {content}.pdf"
                if not output_pdf.exists():
                    with open(output_pdf, "wb") as f:
                        images = []
                        for img_path in sorted_book[content]:
                            try:
                                # Load image using OpenCV
                                img = cv2.imread(str(img_path))
                                if img is None:
                                    print(f"Error loading image file: {img_path}")
                                    continue  # Skip this file if it can't be loaded

                                # Resize the image to fit letter size
                                img_resized = cv2.resize(img, LETTER_SIZE, interpolation=cv2.INTER_AREA)

                                # Convert the resized image to a binary format
                                success, img_encoded = cv2.imencode('.jpg', img_resized)
                                if success:
                                    images.append(img_encoded.tobytes())
                                else:
                                    print(f"Error encoding image file: {img_path}")
                            except Exception as e:
                                print(f"Error processing image file: {img_path}")
                                print(f"Error details: {e}")
                                continue  # Skip this file and continue with the next

                        if abs(len(images) - len(sorted_book[content])) < 2:
                            f.write(img2pdf.convert(images))
                        else:
                            print("There was an issue processing one of the images!")

        except KeyError:
            # traceback.print_exc()
            continue

        print(f"PDF created successfully!", book_code)



def find_config_js_numbers(directory):
    dir_path = Path(directory)
    config_js_files = list(dir_path.rglob('config.js'))
    
    # Extract the numbers from the paths
    numbers = []
    for file in config_js_files:
        match = re.search(r'BOOK\\(\d+)\\(\d+)\\config.js', str(file))
        if match:
            numbers.append(f"{match.group(1)}/{match.group(2)}")
    
    return numbers

directory = f'C:/Users/{os.getlogin()}/AppData/Local/Packages/ASC.ASC_yndy5v4xq42h4/LocalState/downloads/BOOK/'
book_codes = find_config_js_numbers(directory)

for book_code in book_codes:
    try:
        create_book("1441/6078")

    except Exception as e:
        print(f"Error processing book_code {"1441/6078"}:")
        traceback.print_exc()
    break