import json
import math
import sys

alpha = 0.8
lmbda = 0.19991
delta = 1e-10

single_cache = {}
bigram_cache = {}
trigram_cache = {}
unigram_counts = {}
bigram_counts = {}

def read_1_word(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_2_word(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_3_word(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# read the data
def init_unigram_counts(single_word_data):
    for pinyin, info in single_word_data.items():
        words = info.get("words", [])
        counts = info.get("counts", [])
        for w, c in zip(words, counts):
            unigram_counts[w] = unigram_counts.get(w, 0) + c

def init_bigram_counts(bi_word_data):
    for pinyin, info in bi_word_data.items():
        words = info.get("words", [])
        counts = info.get("counts", [])
        for w, c in zip(words, counts):
            parts = w.split()
            if len(parts) != 2:
                continue
            key = (parts[0], parts[1])
            bigram_counts[key] = bigram_counts.get(key, 0) + c

def get_single_map(pinyin, single_word_data):
    if pinyin in single_cache:
        return single_cache[pinyin]
    info = single_word_data.get(pinyin, {})
    words = info.get("words", [])
    counts = info.get("counts", [])
    s = sum(counts)
    m = {}
    if s > 0:
        for w, c in zip(words, counts):
            if c > 0:
                m[w] = c / s
    single_cache[pinyin] = m
    return m

# calculate single, double, triple character probability distribution
def get_bi_map(p1, p2, bi_word_data):
    key = (p1, p2)
    if key in bigram_cache:
        return bigram_cache[key]
    info = bi_word_data.get(f"{p1} {p2}", {})
    words = info.get("words", [])
    counts = info.get("counts", [])
    d = {}
    for w, c in zip(words, counts):
        parts = w.split()
        if len(parts) != 2:
            continue
        prev_c, curr_c = parts
        t = unigram_counts.get(prev_c, 0)
        if t > 0 and c > 0:
            d[(prev_c, curr_c)] = c / t
    bigram_cache[key] = d
    return d

# read three characters frequency
def get_tri_map(p1, p2, p3, tri_word_data):
    key = (p1, p2, p3)
    if key in trigram_cache:
        return trigram_cache[key]
    info = tri_word_data.get(f"{p1} {p2} {p3}", {})
    d = {}
    for trigram_str, c in info.items():
        parts = trigram_str.split()
        if len(parts) != 3:
            continue
        prev_1_c, prev_2_c, curr_c = parts
        t = bigram_counts.get((prev_1_c, prev_2_c), 0)
        if t > 0 and c > 0:
            d[(prev_1_c, prev_2_c, curr_c)] = c / t
    trigram_cache[key] = d
    return d


def viterbi(pinyin_in, single_word_data, bi_word_data, tri_word_data):
    n = len(pinyin_in)
    cands = []
    for p in pinyin_in:
        info = single_word_data.get(p, {})
        w = info.get("words", [])
        cands.append(w if w else [" "])

    dp = [{} for _ in range(n)]
    dummy = "<S>"
    first_map = get_single_map(pinyin_in[0], single_word_data)
    for c0 in cands[0]:
        p_uni = first_map.get(c0, delta)
        dp[0][(dummy, c0)] = (math.log(p_uni), None)

    for i in range(1, n):
        p1_map = get_single_map(pinyin_in[i], single_word_data)
        p2_map = get_bi_map(pinyin_in[i - 1], pinyin_in[i], bi_word_data)
        if i >= 2:
            p3_map = get_tri_map(pinyin_in[i - 2], pinyin_in[i - 1], pinyin_in[i], tri_word_data)
        else:
            p3_map = {}

        for c_i in cands[i]:
            for (w, x), (score_prev, from_prev) in dp[i - 1].items():
                p_tri = p3_map.get((w, x, c_i), 0.0)
                p_bi = p2_map.get((x, c_i), 0.0)
                p_uni = p1_map.get(c_i, 0.0)
                s_tri = p_tri if p_tri > 0 else delta
                s_bi = p_bi if p_bi > 0 else delta
                s_uni = p_uni if p_uni > 0 else delta
                p_final = alpha * s_tri + lmbda * s_bi + (1 - alpha - lmbda) * s_uni
                if p_final <= 0:
                    continue
                score_cur = score_prev + math.log(p_final)
                new_key = (x, c_i)
                if new_key not in dp[i] or score_cur > dp[i][new_key][0]:
                    dp[i][new_key] = (score_cur, (w, x))

    best_pair = None
    best_score = -math.inf
    for pair, (sc, frm) in dp[n - 1].items():
        if sc > best_score:
            best_score = sc
            best_pair = pair

    path = []
    cur_pair = best_pair
    for i in range(n - 1, -1, -1):
        path.append(cur_pair[1])
        _, frm = dp[i][cur_pair]
        if frm is None:
            break
        cur_pair = frm

    path.reverse()
    return "".join(path)

def main():
    single_word_data = read_1_word("1_word.txt")
    bi_word_data = read_2_word("2_word.txt")
    tri_word_data = read_3_word("3_word.txt")
    init_unigram_counts(single_word_data)
    init_bigram_counts(bi_word_data)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            break
        pinyin_list = line.split()
        output = viterbi(pinyin_list, single_word_data, bi_word_data, tri_word_data)
        print(output)


if __name__ == "__main__":
    main()
