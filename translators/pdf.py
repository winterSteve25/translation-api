import os

from helper import create_html_translator, get_file_info

if __name__ == "__main__":
    html_translator, file_path = create_html_translator()
    filename, result_name = get_file_info(file_path)

    os.system(f"ebook-convert {file_path} {result_name}.html --output-profile tablet")
    html_translator.translate_html(f"{result_name}.html")
    os.system(f"ebook-convert {result_name}.html {result_name}.pdf --output-profile tablet")

    os.remove(f"{result_name}.html")
