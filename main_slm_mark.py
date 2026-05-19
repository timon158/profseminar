import re
import csv
import pickle
import random
import matplotlib.pyplot as plt


k = int(input('Введите длину марковской цепи: '))


path_dataset = ''


def count_words(message: str, data_dict: dict):

    """"Проходится по сообщению, добавляет в словарь данных
    (data_dict) ключ в виде кортежа из k слов
    и значение - словарь из пар ключ - значение, где ключ
    это возможное слово, а значение это кортеж всех встречающихся после него слов"""

    message = message.split()

    if len(message) < k:
        return 
    for word in range(len(message) - k):

        kortezh = tuple(message[word:word + k])

        next_word = message[word + k]
        if kortezh in data_dict:
            data_dict[kortezh].append(next_word)

        else:
            data_dict[kortezh] = [next_word]
    


def make_data_dict(path, k):

    """Составляет матрицу перехода (словарь)"""

    data_dict = {}

    with open(path, 'r', encoding='utf-8', errors='ignore') as file:

        reader = csv.reader(file, delimiter=',', quotechar='"')
        for row in reader:
            message = clear_message(row[5])
            # print(message)
            # input()
            count_words(message, data_dict)


    with open(f'data{k}.pickle', 'wb') as file:
        pickle.dump(data_dict, file)

    return data_dict




def clear_message(text: str) -> str:

    """ Очищает строку текста, удаляя:
    URL, обращения @user, хештеги, лишние пробелы """

    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text



try:
    with open(f'data{k}.pickle', 'rb') as file:
        data_dict = pickle.load(file)
except FileNotFoundError:
    print(f'Матрица перехода для k = {k} не найдена, создаем новую...')
    data_dict = make_data_dict(path_dataset, k)


question = input('Введите свой вопрос: ').lower()
question = tuple(question.split())

M = int(input('Введите желаемую длину ответа: '))
counter = 0

while True:

    question = question[len(question) - k:]

    try:
        possible_words = data_dict[question]
        word = random.choice(possible_words)
        print(word, end=' ')
        question = question[1:] + (word,)

    except KeyError:
        print('\n\nТакой комбинации слов нет или все закончились')
        break

    finally:
        counter += 1
        if counter == M:
            break







def plot_next_words_histogram(target_word, pickle_path='data1.pickle', top_n=15):

    """Загружает словарь из pickle-файла и строит гистограмму частотности слов,
    которые встречаются в тексте сразу после target_word."""


    with open(pickle_path, 'rb') as file:
        data_dict = pickle.load(file)

    next_words = data_dict.get(tuple([target_word]))
    
    if next_words is None:
        print(f"Слово '{target_word}' отсутствует в словаре")
        return
    if not next_words:
        print(f"После слова '{target_word}' в тексте ничего не следовало")
        return

    word_counts = {}
    for word in next_words:
        word_counts[word] = word_counts.get(word, 0) + 1

    sorted_words = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)

    if top_n and len(sorted_words) > top_n:
        sorted_words = sorted_words[:top_n]
    
    words_to_plot = []
    for word, count in sorted_words:
        words_to_plot.extend([word] * count)

    plt.figure(figsize=(12, 6))
    
    unique_words = list(set(words_to_plot))
    unique_words_count = len(unique_words)
    
    plt.hist(words_to_plot, bins=unique_words_count, edgecolor='black', rwidth=0.8, color='royalblue')
    
    plt.title(f"Частотность слов, идущих после слова '{target_word}'", fontsize=14, fontweight='bold')
    plt.xlabel("Последующие слова", fontsize=12)
    plt.ylabel("Количество упоминаний", fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()


print('\nДля какого слова построить гистограмму частотности слов? - ', end='')
target_word = input()
plot_next_words_histogram(target_word)

