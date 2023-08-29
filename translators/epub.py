import os
import shutil
import sys
import zipfile
from pathlib import Path

from helper import pcolors, create_html_translator, get_file_info
from translator import HTMLTranslator


def extract_epub(file_path, file_extracted_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip:
            print('Extracting the epub file...', end='\r')
            zip.extractall(file_extracted_path)
            print(
                f'Extracting the epub file: [{pcolors.GREEN} DONE {pcolors.ENDC}]')
        return True
    except Exception:
        print(
            f'Extracting the epub file: [{pcolors.FAIL} FAIL {pcolors.ENDC}]')
        return False


def get_epub_html_path(file_extracted_path):
    html_list_path = []

    for file_type in ['*.[hH][tT][mM][lL]', '*.[xX][hH][tT][mM][lL]', '*.[hH][tT][mM]']:
        html_list_path += [str(p.resolve()) for p in list(Path(file_extracted_path).rglob(file_type))]

    return html_list_path


def zip_epub(file_extracted_path):
    print('Making the translated epub file...', end='\r')
    try:
        filename = f"{file_extracted_path}.epub"
        file_extracted_absolute_path = Path(file_extracted_path)

        with open(str(file_extracted_absolute_path / 'mimetype'), 'w') as file:
            file.write('application/epub+zip')
        with zipfile.ZipFile(filename, 'w') as archive:
            archive.write(
                str(file_extracted_absolute_path / 'mimetype'), 'mimetype',
                compress_type=zipfile.ZIP_STORED)
            for file in file_extracted_absolute_path.rglob('*.*'):
                archive.write(
                    str(file), str(file.relative_to(
                        file_extracted_absolute_path)),
                    compress_type=zipfile.ZIP_DEFLATED)

        shutil.rmtree(file_extracted_path)
        print(f'Making the translated epub file: [{pcolors.GREEN} DONE {pcolors.ENDC}]')
    except Exception as e:
        print(e)
        print(f'Making the translated epub file: [{pcolors.FAIL} FAIL {pcolors.ENDC}]')


def start(html_translator: HTMLTranslator, file_path: str):
    filename, file_extracted_path = get_file_info(file_path)
    if extract_epub(file_path, file_extracted_path):
        htmls = get_epub_html_path(file_extracted_path)
        html_translator.multithreads_html_translate(htmls)
        zip_epub(file_extracted_path)


if __name__ == "__main__":
    html_translator, epub_abs_file_path = create_html_translator()

    if os.path.isfile(epub_abs_file_path) and epub_abs_file_path.endswith('.epub'):
        start(html_translator, epub_abs_file_path)
    else:
        print('Epub file path is incorrect!')
        sys.exit()
