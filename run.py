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
from natsort import natsorted
import sys


def get_config_book_data(book_path) -> dict:
    # Read the JavaScript file
    with open(book_path / "config.js", "r", encoding="utf-8") as file:
        js_content = file.read()

        # Use regex to find all occurrences of the variable
        pattern = r'var BOOK_CONFIG = ({.*?});'
        matches = re.findall(pattern, js_content, re.DOTALL)

    # Parse each JSON string into a Python dictionary
    return [json.loads(match) for match in matches][0]

def get_book_level(config_book_data):
    for page in config_book_data["pages"]:
        if "sb_" in page["URL"] or "_la_" in page["URL"] or "_app_" in page["URL"]:
            if "_lv" in page["URL"] and "_book" in page["URL"]:
                return page["URL"].split("_")[2].replace("lv", "Level "), page["URL"].split("_")[3].replace("book", "Book ")

            elif "_nv" in page["URL"] and "_trim" and "libro" not in page["URL"] and "eefprim" not in page["URL"]:
                return page["URL"].split("_")[3].replace("nv", "Nivel "), page["URL"].split("_")[4].replace("trim", "Libro ")

            elif "_nv" in page["URL"] and "_trim" and "libro" in page["URL"]:
                return page["URL"].split("_")[1].replace("nv", "Nivel "), page["URL"].split("_")[2].replace("libro", "Libro ")

            elif "book" in page["URL"]:
                return page["URL"].split("_")[3].replace("niv", "Nivel "), page["URL"].split("_")[2].replace("trim", "Libro ")

            elif "book" not in page["URL"]:
                return page["URL"].split("_")[3].replace("nv", "Nivel "), page["URL"].split("_")[2].replace("trim", "Libro ")
            


def get_book_type(url_path):
    with open(r"C:\Users\elios\Desktop\test.txt", "a", encoding="utf-8") as file:
            
        if "html" not in url_path:
            if "sb_" in url_path:
                file.write(f'{"Student's Book"} {url_path}\n')
                return "Student's Book"
            
            elif "tn_" in url_path:
                file.write(f'{"Teacher's Notes"} {url_path}\n')
                return "Teacher's Notes"
            
            elif "_lm_" in url_path or "_app_ndm_" in url_path:
                file.write(f'{"Libro del Maestro"} {url_path}\n')
                return "Libro del Maestro"
            
            elif "_la_" in url_path or "_app_" in url_path and "secuencia" not in url_path:
                file.write(f'{"Libro del Alumno"} {url_path}\n')
                return "Libro del Alumno"

            else:
                file.write(f'Manuales generales primaria {url_path}\n')
                return "Manuales generales primaria"



def create_book(book_code):
    book_data = {}
    chapter_ranges = {}

    book_path = Path(f'C:/Users/{os.getlogin()}/AppData/Local/Packages/ASC.ASC_yndy5v4xq42h4/LocalState/downloads/BOOK/{book_code}')
    output_path = Path("D:/English Teaching Content")
    config_book_data = get_config_book_data(book_path)

    book_level, book_number = get_book_level(config_book_data)

    # parse config book data
    school_level = config_book_data["type"].capitalize()

    book_level_path = output_path / school_level / book_number / book_level
    material_path = book_level_path / "Material"

    # make directories
    if not book_level_path.exists():
        os.makedirs(book_level_path)

    if not material_path.exists():
        os.makedirs(material_path)

    # Create page book ranges
    for dat in config_book_data["menuItems"]:
        bookType = dat["text"]

        if bookType == "Libro del alumno":
            bookType = "Libro del Alumno"

        elif bookType == "Notas del Maestro":
            bookType = "Libro del Maestro"
            
        if bookType not in ["Fit for Teaching", "Two Week Schedule", "Intellectual Abilities"]:
            if bookType not in chapter_ranges:
                chapter_ranges[bookType] = {}

            book_data[bookType] = {"Fundamentals": []}

            if "children" in dat:
                for contentOut in dat["children"]:
                    if "children" in contentOut: # .html to do...
                        contentsIn = contentOut["children"]
                        chapter_name = contentOut["text"]
                        
                        # print(chapter_name)
                        if bookType not in ["Libro del Alumno", "Libro del Maestro", "Manuales generales primaria"]:
                            # Store the chapter range separately // Compatible with English Book not Spanish
                            chapter_ranges[bookType][chapter_name] = f'{contentsIn[0]["URL"][:-4].split("_")[-1]}-{contentsIn[-1]["URL"][:-4].split("_")[-1]}'
                            # Initialize each chapter with an empty list in book_data
                            book_data[bookType][chapter_name] = []

                        else:
                            if bookType == "Libro del Alumno":
                                if "Unidad" in chapter_name:
                                    chapter_ranges[bookType][chapter_name] = contentsIn[0]["URL"][:-4].split("_")[-1]
                                else:
                                    chapter_ranges[bookType][chapter_name] = contentsIn[0]["children"][0]["URL"][:-4].split("_")[-1]
                            else:

                                if "URL" in contentsIn[0]:
                                    chapter_ranges[bookType][chapter_name] = contentsIn[0]["URL"][:-4].split("_")[-1]
                                    # print(contentsIn[0]["children"][0]["URL"][:-4].split("_")[-1])
                                else:
                                    chapter_ranges[bookType][chapter_name] = contentsIn[0]['children'][0]["URL"][:-4].split("_")[-1]
                                
                            # Initialize each chapter with an empty list in book_data
                            book_data[bookType][chapter_name] = []
                            

    # # Edit the props chapter ranges for spanish books
    for index, (key, val) in enumerate(chapter_ranges.items()):
        try:
            chapter_ranges[key] =f'{val}-{int(list(chapter_ranges.values())[index+1])-1}'
        except Exception:
            pass    

    if "Fundamentals" in chapter_ranges:
        del chapter_ranges["Fundamentals"]

    # Calculate the range for "Fundamentals"
    for key in chapter_ranges.keys():
        fundamentals_range = f"0-{int((list(chapter_ranges[key].values())[0].split('-')[0]))-1}"

        # Create a new dictionary with "Fundamentals" as the first entry
        chapter_ranges[key] = {"Fundamentals": fundamentals_range, **chapter_ranges[key]}

    page_ranges = {}

    content_types = list(chapter_ranges.keys())
    with open(f"C:/Users/{os.getlogin()}/Desktop/test.json", 'w', encoding="utf-8") as file:
        json.dump(config_book_data, file, indent=4)


    if "Nivel" in book_level:
        manuales_generales_primaria_contents = [i['text'] for i in config_book_data["menuItems"][2]["children"]]

        last_page = 0
        current_book_content_type_index = 0
        manuales_generales_primaria_index = 0
        for index, page in enumerate(config_book_data["pages"]):
            # replace "portada" or "00" to "0"
            new_page = page["URL"]
            if "portada" in new_page or "_00" in new_page: 
                new_page = new_page.replace("portada", "0").replace("00", "0")

            #get the current page to a variable
            if ''.join(filter(str.isdigit, new_page[:-4].split("_")[-1])):
                current_page = int(''.join(filter(str.isdigit, new_page[:-4].split("_")[-1])))

                if  current_page-last_page < 3 and "recortable" not in new_page and "_anexo" not in new_page:

                    # Access the object if not "Manuales generales primaria" only for "Libro del Alumno" and maetro
                    if last_page > current_page and content_types[current_book_content_type_index] != "Manuales generales primaria":
                        current_book_content_type_index += 1

                    elif last_page > current_page and manuales_generales_primaria_index < len(manuales_generales_primaria_contents)-1 and content_types[current_book_content_type_index] == "Manuales generales primaria":
                        manuales_generales_primaria_index += 1
                    
                    # save pages to a list
                    if content_types[current_book_content_type_index] not in page_ranges and content_types[current_book_content_type_index] != "Manuales generales primaria":
                        page_ranges[content_types[current_book_content_type_index]] = []
                    elif content_types[current_book_content_type_index] not in page_ranges and content_types[current_book_content_type_index] == "Manuales generales primaria":
                        page_ranges[content_types[current_book_content_type_index]] = {}

                    # append current page to list content type
                    if isinstance(page_ranges[content_types[current_book_content_type_index]], list) and content_types[current_book_content_type_index] != "Manuales generales primaria":
                        page_ranges[content_types[current_book_content_type_index]].append(current_page)

                    elif isinstance(page_ranges[content_types[current_book_content_type_index]], dict) and content_types[current_book_content_type_index] == "Manuales generales primaria":
                        if manuales_generales_primaria_contents[manuales_generales_primaria_index] not in page_ranges[content_types[current_book_content_type_index]]:
                            page_ranges[content_types[current_book_content_type_index]][manuales_generales_primaria_contents[manuales_generales_primaria_index]] = []
                        page_ranges[content_types[current_book_content_type_index]][manuales_generales_primaria_contents[manuales_generales_primaria_index]].append(current_page)
                        
                    # assign current page to last page to track it
                    last_page = current_page


        last_page = 0
        for key in chapter_ranges.keys():
            if key in ["Libro del Alumno", "Libro del Maestro"]:
                for index, subKey in enumerate(chapter_ranges[key]):
                    if subKey != "Fundamentals" and subKey != list(chapter_ranges[key].keys())[-1]:
                        chapter_ranges[key][subKey] = f"{last_page}-{int(chapter_ranges[key][list(chapter_ranges[key].keys())[index+1]])-1}"

                    elif subKey == list(chapter_ranges[key].keys())[-1]:
                        chapter_ranges[key][subKey] = f"{last_page}-{page_ranges[key][-1]}"

                    if len(list(chapter_ranges[key].keys()))-1 > index:
                        last_page = chapter_ranges[key][list(chapter_ranges[key].keys())[index+1]]
                
            else:
                for subKey in page_ranges[key]:
                    if book_code == "1445/6092" and subKey == "Secuencia y Alcance":
                        chapter_ranges[key][subKey] = f"{1}-{36}"
                    elif book_code == "1447/6098" and subKey == "Secuencia y Alcance":
                        chapter_ranges[key][subKey] = f"{1}-{31}"
                    elif book_code == "1469/6094" and subKey == "Secuencia y Alcance":
                        chapter_ranges[key][subKey] = f"{1}-{33}"
                    else:
                        chapter_ranges[key][subKey] = f"{1}-{page_ranges[key][subKey][-1]}"

        del chapter_ranges["Manuales generales primaria"]["Fundamentals"]

    chapter_ranges_index_map = {}
    ranges_chapters = {}
    
    for dat in config_book_data["pages"]:
        if dat["URL"].strip().endswith("jpg") and "recortable" not in dat["URL"].strip():
            page_number = dat["URL"][:-4].split("_")[-1]
            page_number = int(''.join(filter(str.isdigit, page_number))) if page_number != "portada" else 0
            book_type =  get_book_type(dat["URL"].strip())

            if book_type not in ranges_chapters:
                ranges_chapters[book_type] = {}

            if book_type not in chapter_ranges_index_map:
                chapter_ranges_index_map[book_type] = 0

            key = list(chapter_ranges[book_type].keys())[chapter_ranges_index_map[book_type]]
            from_chapter, to_chapter = map(int, chapter_ranges[book_type][key].split("-"))

            if key not in ranges_chapters[book_type]:
                ranges_chapters[book_type][key] = []


            misc_data = []
            if page_number < from_chapter:
                if dat.get("attachments", False):
                    for dat_attachment in dat["attachments"]:
                        if dat_attachment["type"] == "gallery":
                            for image in dat_attachment["images"]:
                                if "https:" not in image and "http:" not in image and ".com" not in image:
                                    misc_data.append(image)
                        else:
                            if "https:" not in dat_attachment["URL"] and "http:" not in dat_attachment["URL"] and ".com" not in dat_attachment["URL"]:
                                misc_data.append(dat_attachment["URL"])

            else:
                if dat.get("attachments", False):
                    for dat_attachment in dat["attachments"]:
                        if dat_attachment["type"] == "gallery":
                            for image in dat_attachment["images"]:
                                if "https:" not in image and "http:" not in image and ".com" not in image:
                                    misc_data.append(image)
                        else:
                            if "https:" not in dat_attachment["URL"] and "http:" not in dat_attachment["URL"] and ".com" not in dat_attachment["URL"]:
                                misc_data.append(dat_attachment["URL"])

            if page_number == to_chapter and chapter_ranges_index_map[book_type] < len(list(chapter_ranges[book_type].keys()))-1:
                chapter_ranges_index_map[book_type] += 1

            if misc_data:
                ranges_chapters[book_type][key].append({"URL": dat["URL"], "misc": misc_data})
            else:
                if dat["URL"] not in ranges_chapters[book_type][key]:
                    ranges_chapters[book_type][key].append({"URL": dat["URL"], "misc": misc_data})
            
    # #sort lists
    for key in list(ranges_chapters.keys()):
        for subKey in ranges_chapters[key]:
            if not "portada" in ranges_chapters[key][subKey][0]["URL"]:
                ranges_chapters[key][subKey] = natsorted(ranges_chapters[key][subKey], key=lambda x: x['URL'])


    sorted_book = {}

    for book_type in ranges_chapters.keys():
        if book_type not in sorted_book:
            sorted_book[book_type] = {}
        full_pdf_images = []
        for content in ranges_chapters[book_type].keys():
            if content not in sorted_book:
                sorted_book[book_type][content] = []
            for url_misc in ranges_chapters[book_type][content]:
                url_path = url_misc["URL"]
                miscs = url_misc["misc"]

                if str(book_path / url_path) not in sorted_book[book_type][content]:
                    sorted_book[book_type][content].append((str(book_path / url_path)))

                page_number = url_path[:-4].split("_")[-1]
                if page_number.lower() == "portada":
                    page_number = 0
                elif isinstance(page_number, str):
                    page_number = int(''.join(filter(str.isdigit, page_number)))

                #copy media to folder where the pdfs chapter will be created
                if miscs: # create dirs to every page that has materials available
                    # copy the materials to each folder page 
                    for misc in miscs:
                        if misc and misc != "@" and ".html" not in misc and "https:" not in misc:
                            _, file_extension = os.path.splitext(misc)
                            new_page_number = page_number-12 if "Level" in book_level else page_number

                            new_file_name = f"{book_number} - {book_level} - {content} - Page {new_page_number}{file_extension}" if not file_extension == ".jpg" else f"{book_number} - {book_level} - {content} - Page {new_page_number} - Recortable - {misc.split("_")[-1]}"
                            material_page_path = material_path / f"Page {new_page_number}" 

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


            # Define letter size in pixels (assuming 300 DPI)
            LETTER_SIZE = (2550, 3300)  # (width, height) in pixels for 8.5x11 inches at 300 DPI

            output_pdf_content = book_level_path / f"{book_type} - {book_number} - {book_level} - {content}.pdf"
            output_pdf = book_level_path / f"{book_type} - {book_number} - {book_level}.pdf"

            if not output_pdf.exists():
                images = []
                for img_path in sorted_book[book_type][content]:
                    try:
                        # Load image using OpenCV
                        img = cv2.imread(img_path)
                        if img is None:
                            print(f"Error loading image file: {img_path}")
                            continue  # Skip this file if it can't be loaded

                        # Resize the image to fit letter size
                        img_resized = cv2.resize(img, LETTER_SIZE, interpolation=cv2.INTER_AREA)

                        # Convert the resized image to a binary format
                        success, img_encoded = cv2.imencode('.jpg', img_resized)
                        if success:
                            images.append(img_encoded.tobytes())
                            full_pdf_images.append(img_encoded.tobytes())
                        else:
                            print(f"Error encoding image file: {img_path}")
                    except Exception as e:
                        print(f"Error processing image file: {img_path}")
                        print(f"Error details: {e}")
                        continue  # Skip this file and continue with the next

                if not output_pdf_content.exists():
                    if abs(len(images) - len(sorted_book[book_type][content])) < 3:
                        with open(output_pdf_content, "wb") as f:
                            f.write(img2pdf.convert(images))
                    else:
                        return output_pdf_content
                    
        print(book_code, ": ", f"PDF {book_type} - {book_number} - {book_level} - {content} - Created successfully!")

        if not output_pdf.exists(): # create full pdf
            with open(output_pdf, "wb") as f:
                f.write(img2pdf.convert(full_pdf_images))

    print(book_code, ": ",f"PDF {book_type} - {book_number} - {book_level} - Created successfully!")
    return False



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
        return_code = create_book(book_code)
        if return_code:
            print(return_code, book_code, "There was an issue processing one of the images!")
            os.remove(return_code)
            break

    except Exception as e:
        print(f"Error processing book_code {book_code}:")
        traceback.print_exc()