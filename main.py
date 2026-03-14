import sys
import os
import json
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.bigram_mode import read_1_word, read_2_word, init_unigram_counts, viterbi as bigram_viterbi
from src.trigram_mode import read_1_word as read_1_word_tri, read_2_word as read_2_word_tri
from src.trigram_mode import read_3_word, init_unigram_counts as init_uni_tri, init_bigram_counts, viterbi as trigram_viterbi

from src.train_bigram import (
    load_pinyin_char_map,
    load_valid_chars,
    build_char_to_py,
    save_char_to_py,
    process_corpus as process_bigram,
    convert_counts_format
)
from src.train_trigram import (
    load_char_to_py,
    process_corpus as process_trigram
)

def train_all():
    py_char_fp = './data/拼音汉字表.txt'
    valid_fp = './data/一二级汉字表.txt'
    corpus_dir = 'corpus/sina_news_gbk'
    smp_file = 'usual_train_new.txt'

    need_bigram = not (os.path.exists('1_word.txt') and os.path.exists('2_word.txt'))
    need_trigram = not os.path.exists('3_word.txt')
    start_time = time.time()

    if not need_bigram and not need_trigram:
        print("data already exists. skip training!", file=sys.stderr)
        return

    print("start training model...", file=sys.stderr)

    py_to_char = load_pinyin_char_map(py_char_fp)
    valid_chars = load_valid_chars(valid_fp)
    char_to_py = build_char_to_py(py_to_char, valid_chars)
    save_char_to_py(char_to_py, 'char_to_py.txt')

    corpus_files = [os.path.join(corpus_dir, f) for f in os.listdir(corpus_dir) if f.endswith('.txt')]
    if os.path.exists(smp_file):
        corpus_files.append(smp_file)
    
    print(f"files loaded, train starting, time used: {time.time() - start_time:.2f}s", file=sys.stderr)

    if need_bigram:
        print("training bigram...", file=sys.stderr)
        start_time = time.time()
        single_counts, bi_counts = process_bigram(corpus_files, char_to_py, valid_chars)
        with open('1_word.txt', 'w', encoding='utf-8') as f:
            json.dump(convert_counts_format(single_counts), f, ensure_ascii=False, indent=2)
        with open('2_word.txt', 'w', encoding='utf-8') as f:
            json.dump(convert_counts_format(bi_counts), f, ensure_ascii=False, indent=2)
        print(f"files saved, bigram training time: {time.time() - start_time:.2f}s", file=sys.stderr)

    if need_trigram:
        print("training trigram...", file=sys.stderr)
        start_time = time.time()
        char_to_py = load_char_to_py('char_to_py.txt')  # 确保使用生成后的
        trigram_counts = process_trigram(corpus_files, char_to_py, valid_chars)
        filtered_trigrams = {
            k: {w: c for w, c in v.items() if c > 1}
            for k, v in trigram_counts.items()
        }
        filtered_trigrams = {k: v for k, v in filtered_trigrams.items() if v}
        with open('3_word.txt', 'w', encoding='utf-8') as f:
            json.dump(filtered_trigrams, f, ensure_ascii=False, indent=2)
        print(f"files saved, trigram training time: {time.time() - start_time:.2f}s", file=sys.stderr)

    print("training finished!", file=sys.stderr)

def run_bigram():
    start = time.time()
    single_word_data = read_1_word("1_word.txt")
    bi_word_data = read_2_word("2_word.txt")
    init_unigram_counts(single_word_data)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        pinyin_list = line.split()
        print(bigram_viterbi(pinyin_list, single_word_data, bi_word_data))
    print(f"decoding time (bigram, 501 lines): {time.time() - start:.2f}s", file=sys.stderr)

def run_trigram():
    start = time.time()
    single_word_data = read_1_word_tri("1_word.txt")
    bi_word_data = read_2_word_tri("2_word.txt")
    tri_word_data = read_3_word("3_word.txt")
    init_uni_tri(single_word_data)
    init_bigram_counts(bi_word_data)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        pinyin_list = line.split()
        print(trigram_viterbi(pinyin_list, single_word_data, bi_word_data, tri_word_data))
    print(f"decoding time (trigram, 501 lines): {time.time() - start:.2f}s", file=sys.stderr)

def main():
    use_trigram = len(sys.argv) >= 2 and sys.argv[1] == "trigram"
    train_all()
    print("now ready for input!", file=sys.stderr)
    if use_trigram:
        run_trigram()
    else:
        run_bigram()

if __name__ == "__main__":
    main()
