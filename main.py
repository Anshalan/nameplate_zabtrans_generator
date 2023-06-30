import shutil
import subprocess
import xml.etree.ElementTree as ET
import csv
import os


def fill_svg_template(template_file, csv_file, output_dir):
    output_dirs = [output_dir + "SVG/", output_dir + "PDF/", output_dir + "JPEG/"]
    for i in output_dirs:
        if not os.path.exists(i):
            os.makedirs(i)
            print("created " + i)
        else:
            print(f"Directory '{i}' already exists. Will be cleared out ")
            clear_dir(i)

    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get('IS_OK') == "nie":
                continue
            svg_tree = ET.parse(template_file)
            svg_root = svg_tree.getroot()

            # Find and update text elements based on row data
            for text_elem in svg_root.findall(".//svg:text", {'svg': 'http://www.w3.org/2000/svg'}):
                text_id = text_elem.get('id')  # ID
                text_content = row.get(text_id)

                if text_content is None:
                    continue
                if not text_content:
                    svg_root.remove(text_elem)
                else:
                    current_text = text_elem.text
                    if current_text is not None and current_text == "mm":
                        modified_text = f"{text_content}mm"
                    elif current_text is not None and current_text == "kg":
                        modified_text = f"{text_content}kg"
                    else:
                        modified_text = text_content

                    text_elem.text = modified_text

            # Save filled SVG as a new file
            output_file = os.path.join(output_dirs[0],
                                       f"{row['LP'] + '_' + row['OZNACZENIE_REGALU'].strip().replace(' ', '_')}.svg")
            svg_tree.write(output_file)
            print("saved " + row['LP'] + " to svg")

            ########### save to pdf ##############
            svg_file = output_file
            pdf_file = os.path.join(os.path.abspath(svg_file).replace("SVG", "PDF").replace("svg", "pdf"))
            jpeg_file = os.path.join(os.path.abspath(svg_file).replace("SVG", "JPEG").replace("svg", "jpeg"))

            print(svg_file)
            print(pdf_file)

            command_to_pdf = [
                "inkscape",
                "--export-type=pdf",
                f"--export-filename={pdf_file}",
                svg_file
            ]
            subprocess.run(command_to_pdf)

            command_to_jpg = [
                'inkscape',
                '--export-type=png',
                '--export-dpi=300',
                f'--export-filename={jpeg_file}',
                svg_file
            ]
            print(jpeg_file)

            subprocess.run(command_to_jpg)


def clear_dir(dir_name):
    for filename in os.listdir(dir_name):
        file_path = os.path.join(dir_name, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    print(dir_name + " cleared out of content")


def main():
    template_file = 'resources/META_WZOR.svg'
    csv_files = [
        'resources/TME_GOTOWE_29_06_2023.csv',
        'resources/TME_GOTOWE_06_2023.csv'
    ]

    for csv in csv_files:
        fill_svg_template(template_file, csv, os.path.join('output', os.path.splitext(os.path.basename(csv))[0], ''))


if __name__ == '__main__':
    main()
