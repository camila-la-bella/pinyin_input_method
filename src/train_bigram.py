import os
import json
import ast
import re
import sys


def load_pinyin_char_map(fp):
    pinyin_to_char = {}
    with open(fp, 'r', encoding='gbk') as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            py = parts[0]
            chars = parts[1:]
            pinyin_to_char[py] = [ch for ch in chars]  # not filtered yet, we have valid_chars function
    return pinyin_to_char


def load_valid_chars(fp):
    valid = set()
    with open(fp, 'r', encoding='gbk') as f:
        for line in f:
            for ch in line.strip():
                valid.add(ch)
    return valid


def build_char_to_py(py_to_char, valid):
    char_to_py = {}
    for py, chars in py_to_char.items():
        for ch in chars:
            if ch in valid:  #only keep the valid
                if ch not in char_to_py:
                    char_to_py[ch] = [] # in case of 多音字
                if py not in char_to_py[ch]:
                    char_to_py[ch].append(py)
    return char_to_py


def save_char_to_py(mapping, out_file):
    with open(out_file, 'w', encoding='utf-8') as f:
        for ch, pys in mapping.items():
            for py in pys:
                f.write(f"{ch} {py}\n")


def read_json_file(fp):
    with open(fp, 'r', encoding='gbk', errors='ignore') as f:
        return json.load(f)


def read_literal_file(fp):
    with open(fp, 'r', encoding='gbk') as f: #one of the files is punctuated with '' instead of "", which cant be complied in my environment
        return [ast.literal_eval(line) for line in f if line.strip()]


def clean_and_split_text(text, valid):
    # extract all "continuous" chinese character pieces
    raw_chunks = re.findall(r"[\u4e00-\u9fa5]+", text)
    results = []
    for chunk in raw_chunks:
        # check if character is in "一二级汉字" valid, if valid add to "filtered"
        filtered = ''.join(ch for ch in chunk if ch in valid)
        # if filtered result has more than one character, add to results
        if len(filtered) > 1:
            results.append(filtered)

    return results


def update_counts(record, char_to_py, valid, single_counts, bi_counts):
    text = ""
    if "html" in record and "title" in record:
        text = record.get("title", "") + record.get("html", "")
    elif "content" in record:
        text = record.get("content", "") #get texts from input files

    sentences = clean_and_split_text(text, valid)

    for sentence in sentences:
        chars = [ch for ch in sentence if ch in valid]
        if not chars:
            continue
        for ch in chars:
            pys = char_to_py.get(ch, [])
            if not pys: continue
            for py in pys:
                single_counts.setdefault(py, {})
                single_counts[py][ch] = single_counts[py].get(ch, 0) + 1  # use +1 for all pronunciations
        for i in range(len(chars) - 1):
            ch1, ch2 = chars[i], chars[i + 1]
            py1s = char_to_py.get(ch1, []) #use char_to_py to get pinyin
            py2s = char_to_py.get(ch2, [])
            if not py1s or not py2s:
                continue
            for py1 in py1s:
                for py2 in py2s:
                    key = f"{py1} {py2}"
                    pair = f"{ch1} {ch2}"
                    if key not in bi_counts:
                        bi_counts[key] = {}
                    bi_counts[key][pair] = bi_counts[key].get(pair, 0) + 1  # use +1 for all combinations if "多音字" exists


def process_corpus(corpus_paths, char_to_py, valid): #function to process everything in the directory
    single_counts = {}
    bi_counts = {}
    rec_total = 0
    for fp in corpus_paths:
        try:
            data = read_json_file(fp)
        except Exception:
            data = read_literal_file(fp)
        print(f"processing file {os.path.basename(fp)}... record count: {len(data)}", file=sys.stderr)
        rec_count = 0
        for rec in data:
            rec_count += 1
            rec_total += 1
            if rec_count % 1000 == 0:
                print(f"{os.path.basename(fp)}: Processed {rec_count} records", file=sys.stderr)
            update_counts(rec, char_to_py, valid, single_counts, bi_counts)
    print(f"total records processed: {rec_total}", file=sys.stderr)
    return single_counts, bi_counts

def convert_counts_format(input_dict):
    output = {}
    for py, inner in input_dict.items():
        words = []
        counts = []
        for ch, count in inner.items():
            words.append(ch)
            counts.append(count)
        output[py] = {"words": words, "counts": counts} #change the counts into format that match the OJ system so the code works without further altering
    return output


def main():
    py_char_fp = './data/拼音汉字表.txt'
    valid_fp = './data/一二级汉字表.txt'
    corpus_dir = 'sina_news_gbk'
    smp_file = 'usual_train_new.txt'

    py_to_char = load_pinyin_char_map(py_char_fp)
    valid_chars = load_valid_chars(valid_fp)
    char_to_py = build_char_to_py(py_to_char, valid_chars)
    save_char_to_py(char_to_py, 'char_to_py.txt')

    corpus_files = [os.path.join(corpus_dir, f) for f in os.listdir(corpus_dir) if f.endswith('.txt')]
    if os.path.exists(smp_file):
        corpus_files.append(smp_file)

    single_counts, bi_counts = process_corpus(corpus_files, char_to_py, valid_chars)

    with open('1_word.txt', 'w', encoding='utf-8') as f:
        json.dump(convert_counts_format(single_counts), f, ensure_ascii=False, indent=2)
    with open('2_word.txt', 'w', encoding='utf-8') as f:
        json.dump(convert_counts_format(bi_counts), f, ensure_ascii=False, indent=2)

    print("output files have been written.", file=sys.stderr)


if __name__ == '__main__':
    main()