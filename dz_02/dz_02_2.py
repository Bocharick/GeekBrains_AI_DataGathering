#!/usr/bin/python3
import requests
import re
import os
from collections import Counter
import sys


def get_link(topic):
    if topic.startswith("http"):
        return topic
    else:
        return "https://ru.wikipedia.org/wiki/" + topic.capitalize()


def get_topic_page(topic):
    link = get_link(topic)
    html = requests.get(link).text
    return html


def get_topic_text(topic):
    content = get_topic_page(topic)
    words = re.findall("[а-яА-Я]+", content)
    return words


def get_common_words(topic):
    cntr = Counter(" ".join(get_topic_text(topic)).lower().split(" "))
    return cntr.most_common()


def get_additional_links(topic):
    page = get_topic_page(topic)
    tmp_page_text = re.findall('id=\"Ссылки\">[\s\S]*', page)
    if len(tmp_page_text) > 0:
        tmp_page_text = tmp_page_text[0]
        tmp_page_text = re.sub('</ul>[\s\S]*', "", tmp_page_text)
        additional_links = re.findall('\"http[^\">]*\">', tmp_page_text)
        for i in range(len(additional_links)):
            clean_pattern1 = "^[^ht]*"
            clean_pattern2 = "[^\w]*$"
            additional_links[i] = re.sub(clean_pattern1, "", additional_links[i])
            additional_links[i] = re.sub(clean_pattern2, "", additional_links[i])
        return sorted(additional_links)
    else:
        return []


def rec_most_common_to_file(most_common, filepath):
    with open(filepath, "wt", encoding="utf-8") as output_file:
        for pair in most_common:
            output_file.write("".join([str(pair[0]), "\t", str(pair[1]), "\n"]))


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:\n\t", "python3", os.path.basename(__file__), "topic\nExample:\n\t", "python3",
              os.path.basename(__file__), 'Россия')
        exit()
    else:
        topic = sys.argv[1]

        output_path = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_path, exist_ok=True)

        rec_most_common_to_file(get_common_words(topic), os.path.join(output_path, topic + ".txt"))

        additional_links = get_additional_links(topic)
        print("Всего дополнительных ссылок:", len(additional_links))
        print(*additional_links, sep="\n")
        print()
        for link in additional_links:
            tmp_most_common_words = get_common_words(link)
            tmp_output_path = os.path.join(output_path, re.sub("\W", "", link) + ".txt")
            rec_most_common_to_file(tmp_most_common_words, tmp_output_path)

        print("Все выходные файлы здесь:", os.path.abspath(output_path))
