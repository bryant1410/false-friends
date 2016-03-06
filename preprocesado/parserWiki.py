#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import re

from lxml import etree
from wikiextractor import clean, drop_nested, section

RE_LINKS_FILES = re.compile(r'\[\[([\s\(\)\w\-]*):([\s\(\)\w\-]*)[\s]*?\|*?[\s\(\)\w\-]*?\]\]',
                            re.IGNORECASE | re.UNICODE | re.DOTALL)
RE_PUNCTUATION = re.compile(r'\W', re.IGNORECASE | re.UNICODE)


def paragraphs(wiki_text):
    return wiki_text.lstrip()


# noinspection SpellCheckingInspection
def replace_digits_with_words(text, lang):
    if lang == 'es':
        return text.replace('0', ' cero ') \
            .replace('1', ' uno ') \
            .replace('2', ' dos ') \
            .replace('3', ' tres ') \
            .replace('4', ' cuatro ') \
            .replace('5', ' cinco ') \
            .replace('6', ' seis ') \
            .replace('7', ' siete ') \
            .replace('8', ' ocho ') \
            .replace('9', ' nueve ')
    elif lang == 'pt':
        return text.replace('0', ' zero ') \
            .replace('1', ' um ') \
            .replace('2', ' dois ') \
            .replace('3', ' três ') \
            .replace('4', ' quatro ') \
            .replace('5', ' cinco ') \
            .replace('6', ' seis ') \
            .replace('7', ' sete ') \
            .replace('8', ' oito ') \
            .replace('9', ' nove ')


def remove_non_letters(text, lang):
    return ' '.join(RE_PUNCTUATION.sub(' ', replace_digits_with_words(text, lang)).split())


def pre_process_wiki(in_file, out_file, lang):
    context = etree.iterparse(in_file, tag='page')

    with open(out_file, 'w') as file:
        for _, page_elem in context:
            ns_elem = page_elem.find('ns')
            redirect_elem = page_elem.find('redirect')

            if redirect_elem is None:
                text_elem = page_elem.find('revision/text')
                text = text_elem.text

                text = RE_LINKS_FILES.sub('', text)
                text = paragraphs(text)
                text = clean(text)
                text = section.sub('', text)
                text = '\n'.join(
                    line for line in (
                        remove_non_letters(line, lang) for line in text.split('\n')
                    ) if line != '')
                text = text.lower()
                file.write(text + '\n')

                text_elem.clear()
            else:
                redirect_elem.clear()

            ns_elem.clear()
            page_elem.clear()
            while page_elem.getprevious() is not None:
                del page_elem.getparent()[0]
    del context


if __name__ == '__main__':
    print(datetime.datetime.now())
    pre_process_wiki('sample.xml', 'sample_output.txt', 'es')
    print(datetime.datetime.now())
