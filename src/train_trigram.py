import os
import json
import ast
import re
import sys
from collections import defaultdict

# similar to how other training data is get, we used processed char_to_py list here
def load_char_to_py(path):
    mapping = defaultdict(list)
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                ch, py = parts
                mapping[ch].append(py)
    return dict(mapping)

def load_valid_chars(fp):
    valid = set()
    with open(fp, 'r', encoding='gbk') as f:
        for line in f:
            for ch in line.strip():
                valid.add(ch)
    return valid

def read_json_file(fp):
    with open(fp, 'r', encoding='gbk', errors='ignore') as f:
        return json.load(f)

def read_literal_file(fp):
    with open(fp, 'r', encoding='gbk') as f:
        return [ast.literal_eval(line) for line in f if line.strip()]

# clean and split text the same way
def clean_and_split_text(text, valid):
    chunks = re.findall(r"[\u4e00-\u9fff]+", text)
    results = []
    for chunk in chunks:
        filtered = ''.join(ch for ch in chunk if ch in valid)
        if len(filtered) > 2:
            results.append(filtered)
    return results

def update_trigram_counts(record, char_to_py, valid, tri_counts):
    text = ""
    if "html" in record and "title" in record:
        text = record.get("title", "") + record.get("html", "")
    elif "content" in record:
        text = record.get("content", "")

    sentences = clean_and_split_text(text, valid)

    for sentence in sentences:
        chars = [ch for ch in sentence if ch in valid]
        if len(chars) < 3:
            continue
        for i in range(len(chars) - 2):
            ch1, ch2, ch3 = chars[i], chars[i+1], chars[i+2]
            py1s = char_to_py.get(ch1, [])
            py2s = char_to_py.get(ch2, [])
            py3s = char_to_py.get(ch3, [])
            if not py1s or not py2s or not py3s:
                continue

            # distribute equally to (len(py1s)*len(py2s)*len(py3s)) combinations
            total_comb = len(py1s) * len(py2s) * len(py3s)
            if total_comb == 0:
                continue
            each_value = 1.0 / total_comb

            for py1 in py1s:
                for py2 in py2s:
                    for py3 in py3s:
                        key = f"{py1} {py2} {py3}"
                        if key not in tri_counts:
                            tri_counts[key] = {}
                        trigram = f"{ch1} {ch2} {ch3}"
                        tri_counts[key][trigram] = tri_counts[key].get(trigram, 0) + each_value

def process_corpus(corpus_files, char_to_py, valid):
    tri_counts = {}
    rec_total = 0
    for fp in corpus_files:
        try:
            data = read_json_file(fp)
        except Exception:
            data = read_literal_file(fp)
        print(f"processing file {os.path.basename(fp)}... record count: {len(data)}", file=sys.stderr)
        for idx, rec in enumerate(data):
            rec_total += 1
            if idx % 1000 == 0:
                print(f"processed {idx} records", file=sys.stderr)
            update_trigram_counts(rec, char_to_py, valid, tri_counts)
    print(f"records processed: {rec_total}", file=sys.stderr)
    return tri_counts

def main():
    valid_fp = './data/一二级汉字表.txt'
    char_to_py_fp = 'char_to_py.txt'
    corpus_dir = 'sina_news_gbk'
    smp_file = 'usual_train_new.txt'

    valid_chars = load_valid_chars(valid_fp)
    char_to_py = load_char_to_py(char_to_py_fp)

    corpus_files = [os.path.join(corpus_dir, f) for f in os.listdir(corpus_dir) if f.endswith('.txt')]
    if os.path.exists(smp_file):
        corpus_files.append(smp_file)

    trigram_counts = process_corpus(corpus_files, char_to_py, valid_chars)

    print("filtering low frequency trigrams (count = 1)...", file=sys.stderr)
    filtered_trigrams = {
        k: {w: c for w, c in v.items() if c > 1} # filter out the low frequency trigrams that are not important
        for k, v in trigram_counts.items()
    }
    filtered_trigrams = {k: v for k, v in filtered_trigrams.items() if v}

    with open('3_word.txt', 'w', encoding='utf-8') as f:
        json.dump(filtered_trigrams, f, ensure_ascii=False, indent=2)

    print("Filtered trigram counts saved to 3_word.txt", file=sys.stderr)

if __name__ == '__main__':
    main()
