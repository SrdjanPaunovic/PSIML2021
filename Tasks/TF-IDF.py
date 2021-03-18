import os
import math
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
import sys

total_stems_dict = {}
num_of_documents: int
selected_file: str
stemmer = SnowballStemmer("english")


def print_to_stdout(*a):
    sys.stdout.reconfigure(encoding='utf-8')
    print(*a, file=sys.stdout)


def tokenize_and_stem(text):
    tokens = [word for sent in sent_tokenize(text) for word in word_tokenize(sent)]
    stems = [stemmer.stem(t.lower()) for t in tokens if t.isalnum()]
    return stems


def get_stems(text):
    stems = tokenize_and_stem(text)
    return stems


def get_all_stems_dict(file_names):
    result = {}

    for file_name in file_names:
        file = open(file_name, encoding="utf-8")
        text = file.read()
        stems = get_stems(text)
        for stem in stems:
            if stem in result:
                if file_name in result[stem]:
                    result[stem][file_name] += 1
                else:
                    result[stem][file_name] = 1
            else:
                result[stem] = {}
                result[stem][file_name] = 1

    return result


def tf_idf(stem):
    num_cont_doc = len(total_stems_dict[stem])
    tf = total_stems_dict[stem][selected_file]
    return tf * math.log(num_of_documents/num_cont_doc)


def get_sorted_stems_by_tf_idf(stems):
    result = dict((x, tf_idf(x)) for x in stems)
    return dict(sorted(result.items(), key=lambda item: item[1], reverse=True))


def find_five_sent(text, sorted_stems_by_tf_idf):
    tokens = sent_tokenize(text)
    sent_map = []
    for i in range(len(tokens)):
        token = tokens[i]
        word_stems = [stemmer.stem(t.lower()) for t in word_tokenize(token) if t.isalnum()]
        word_tf_idf_list = [(word, sorted_stems_by_tf_idf[word]) for word in word_stems]
        word_tf_idf_list = sorted(word_tf_idf_list, key=lambda item: item[1], reverse=True)
        word_tf_idf_list = [k for k in word_tf_idf_list[:10]]

        sent_map.append((i, sum([k[1] for k in word_tf_idf_list])))

    sorted_by_tf_idf_top5 = sorted(sent_map, key=lambda item: item[1], reverse=True)[:5]
    sorted_by_index = sorted(sorted_by_tf_idf_top5, key=lambda item: item[0])

    return [tokens[index] for index, _ in sorted_by_index]


if __name__ == '__main__':

    corpus_location = input()
    selected_file = input()

    file_names = []
    for path, _, files in os.walk(corpus_location):
        for name in files:
            file_names.append(os.path.join(path, name).lower())

    num_of_documents = len(file_names)
    total_stems_dict = get_all_stems_dict(file_names)

    selected_file = selected_file.lower()
    file = open(selected_file, encoding="utf-8")
    selected_text = file.read()
    selected_stems = get_stems(selected_text)

    sorted_stems_by_tf_idf = get_sorted_stems_by_tf_idf(selected_stems)

    top10_list = {k: sorted_stems_by_tf_idf[k] for k in list(sorted_stems_by_tf_idf)[:10]}

    # sort lexicographically if tf-idf equal
    top10_list = dict(sorted(sorted(top10_list.items(), key=lambda item: item[0]), key=lambda item: item[1], reverse= True))
    print_to_stdout(', '.join(top10_list))

    top5_sent = find_five_sent(selected_text, sorted_stems_by_tf_idf)
    print_to_stdout(' '.join(top5_sent))
