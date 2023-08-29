import os
import re
from multiprocessing.dummy import Pool as ThreadPool

import tqdm
from bs4 import BeautifulSoup as bs
from bs4 import element
from google_trans_new import google_translator
from helper import pcolors


class HTMLTranslator:
    def __init__(self, dest_lang: str):
        self.dest_lang = dest_lang
        self.translation_dict = {}
        self.translation_dict_file_path = ''
        self.dict_format = '^[^:]+:[^:]+$'
        self.max_trans_words = 5e3

    def multithreads_html_translate(self, htmls):
        pool = ThreadPool(8)
        try:
            for _ in tqdm.tqdm(pool.imap_unordered(self.translate_html, htmls), total=len(htmls), desc='Translating'):
                pass
        except Exception:
            print(f'Translating: [{pcolors.FAIL} FAIL {pcolors.ENDC}]')
            raise
        pool.close()
        pool.join()

    def translate_html(self, html_file):
        with open(html_file, encoding='utf-8') as f:
            soup = bs(f, 'xml')

            epub_eles = list(soup.descendants)

            text_list = []
            for ele in epub_eles:
                if isinstance(ele, element.NavigableString) and str(ele).strip() not in ['', 'html']:
                    text_list.append(str(ele))

            translated_text = self.translate_tag(text_list)
            nextpos = -1

            for ele in epub_eles:
                if isinstance(ele, element.NavigableString) and str(ele).strip() not in ['', 'html']:
                    nextpos += 1
                    if nextpos < len(translated_text):
                        content = self.replace_translation_dict(
                            translated_text[nextpos])
                        ele.replace_with(element.NavigableString(content))

            with open(html_file, "w", encoding="utf-8") as w:
                w.write(str(soup))
            w.close()
        f.close()

    def replace_translation_dict(self, text):
        if self.translation_dict:
            for replace_text in self.translation_dict.keys():
                if replace_text in text:
                    text = text.replace(
                        replace_text, self.translation_dict[replace_text])
        return text

    def get_translation_dict_contents(self):
        if os.path.isfile(self.translation_dict_file_path) and self.translation_dict_file_path.endswith('.txt'):
            print('Translation dictionary detected.')
            with open(self.translation_dict_file_path, encoding='utf-8') as f:
                for line in f.readlines():
                    if re.match(self.dict_format, line):
                        split = line.rstrip().split(':')
                        self.translation_dict[split[0]] = split[1]
                    else:
                        print(
                            f'Translation dictionary is not in correct format: {line}')
                        return False
            f.close()
        else:
            print('Translation dictionary file path is incorrect!')
            return False
        return True

    def translate_tag(self, text_list):
        combined_contents = self.combine_words(text_list)
        translated_contents = self.multithreads_translate(combined_contents)
        extracted_contents = self.extract_words(translated_contents)

        return extracted_contents

    def translate_text(self, text):
        translator = google_translator(timeout=5)
        if type(text) is not str:
            translate_text = ''
            for substr in text:
                translate_substr = translator.translate(substr, self.dest_lang)
                translate_text += translate_substr
        else:
            translate_text = translator.translate(text, self.dest_lang)
        return translate_text

    def multithreads_translate(self, text_list):
        pool = ThreadPool(8)
        try:
            results = pool.map(self.translate_text, text_list)
        except Exception:
            print(f'Translating epub: [{pcolors.FAIL} FAIL {pcolors.ENDC}]')
            raise
        pool.close()
        pool.join()
        return results

    def combine_words(self, text_list):
        combined_text = []
        combined_single = ''
        for text in text_list:
            combined_single_prev = combined_single
            if combined_single:
                combined_single += '\n-----\n' + text
            else:
                combined_single = text
            if len(combined_single) >= self.max_trans_words:
                combined_text.append(combined_single_prev)
                combined_single = '\n-----\n' + text
        combined_text.append(combined_single)
        return combined_text

    def extract_words(self, text_list):
        extracted_text = []
        for text in text_list:
            extract = text.split('-----')
            extracted_text += extract
        return extracted_text