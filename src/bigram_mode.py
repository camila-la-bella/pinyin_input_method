import json
import math
import sys
from math import log, exp

alpha = 0.9
delta = 0.1

single_cache = {}
bigram_cache = {}
unigram_counts = {}


def read_1_word(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_2_word(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
# read the data

def init_unigram_counts(single_word_data):
    for pinyin, info in single_word_data.items():
        words = info.get("words", [])
        counts = info.get("counts", [])
        for w, c in zip(words, counts):
            unigram_counts[w] = unigram_counts.get(w, 0) + c


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
                m[w] = math.log(c / s)
            else:
                m[w] = -math.inf
    else:
        for w in words:
            m[w] = -math.inf
    single_cache[pinyin] = m
    return m
# calculate single character log frequency; uses cache, if already has calculated return directly

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
            d[(prev_c, curr_c)] = math.log(c / t)
        else:
            d[(prev_c, curr_c)] = -math.inf
    bigram_cache[key] = d
    return d
#read two characters frequency

def log_interp(lp1, lp2, lmbda=0.99991):
    # small alter of smoothing function: put the "lambda" inside the log brackets!
    if lp1 == float("-inf"):
        return lp2 + math.log(1 - lmbda)
    if lp2 == float("-inf"):
        return lp1 + math.log(lmbda)
    # P(wi|wi-1) = λP(wi|wi-1) + (1-λ)P(wi)
    # log(P) = log(λexp(lp1) + (1-λ)exp(lp2))
    if lp1 > lp2:
        return lp1 + math.log(lmbda + (1 - lmbda) * math.exp(lp2 - lp1))
    else:
        return lp2 + math.log(lmbda * math.exp(lp1 - lp2) + (1 - lmbda))


def viterbi(pinyin_in, single_word_data, bi_word_data):
    n = len(pinyin_in)
    # length of input
    # print (n)
    cands = []
    for p in pinyin_in:
        # find possible candidate characters for all pinyin, one pinyin for one list of characters possible
        info = single_word_data.get(p, {})
        # print(f"info: {info}")
        # print(f"word: {w}")
        w = info.get("words", [])
        cands.append(w)
    # print (f"candidate words: {cands}")

    dp = []
    back = []
    for i in range(n):
        dp.append([-math.inf] * len(cands[i]))
        back.append([-1] * len(cands[i]))
    # set two lists for recording possibility points and backtrack routes, set the default values -inf and -1
    first_map = get_single_map(pinyin_in[0], single_word_data)
    # print(f"pinyin_in_first:{pinyin_in}")
    # print(f"single word data:{single_word_data}")
    # print(f"first_map: {first_map}")
    for ci, ch in enumerate(cands[0]):
        dp[0][ci] = first_map.get(ch, -math.inf)
        # iterate the first pinyin-to-character choices
    for i in range(1, n):
        curr_map = get_single_map(pinyin_in[i], single_word_data)
        bi_map = get_bi_map(pinyin_in[i - 1], pinyin_in[i], bi_word_data)
        # iterate the following pinyin-to-character choices. both 2-gram and current 1-gram are considered
        # score/possibility dictionary is updated with the function, and uses cache
        for ci, ch2 in enumerate(cands[i]):
            em = curr_map.get(ch2, -math.inf)
            best_val = -math.inf
            best_idx = -1
            # set best_val and best_index(backtracking)
            for pi, ch1 in enumerate(cands[i - 1]):
                sc = dp[i - 1][pi] + log_interp(bi_map.get((ch1, ch2), -math.inf), em)
                # calculate the score possibility, use function for smoothing
                if sc > best_val:
                    best_val = sc
                    best_idx = pi
            dp[i][ci] = best_val
            back[i][ci] = best_idx
    last_row = dp[n - 1] # get the end of dp list
    # print(f"last row of viterbi:{last_row}")
    li = max(range(len(last_row)), key=lambda x: last_row[x]) #find the maximum score, return index
    path = [li]
    for i in range(n - 1, 0, -1):
        idx = path[-1]
        if idx < 0 or idx >= len(back[i]): # in case path does not exist as -1
            continue
        path.append(back[i][idx]) #backtrack path
    path.reverse()
    res = []
    for i in range(n):
        res.append(cands[i][path[i]])
    return "".join(res)


def main():
    single_word_data = read_1_word("1_word.txt")
    bi_word_data = read_2_word("2_word.txt")
    init_unigram_counts(single_word_data)
    print("Ready! now go:", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        pinyin_list = line.split()
        print(viterbi(pinyin_list, single_word_data, bi_word_data))


if __name__ == "__main__":
    main()
# newest
