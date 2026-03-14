# 拼音输入法

本项目实现了一个基于语言模型的拼音输入法系统，支持二元（默认）和三元（可选）两种解码模式。

请确保以下资源文件已经放置到指定目录中：

- `data/拼音汉字表.txt`：拼音到汉字映射表  
- `data/一二级汉字表.txt`：合法汉字列表  
- `corpus/sina_news_gbk/`：原始语料库  
- `data/input.txt`：输入拼音序列（每行一句）

语料库说明：

本项目需要语料库来训练语言模型。

在开发和测试过程中，我使用的是 `sina_news_gbk`，即新浪新闻 2016 年新闻语料库。该语料库未包含在本仓库中，因此使用者需要自行准备兼容的语料库，并将其放置在 `corpus/` 目录下后再进行训练。

运行前可执行以下命令生成模型数据（首次运行会自动训练）：

默认运行（二元模型）：
```bash
python main.py < data/input.txt > data/output.txt
```

指定运行三元模型需要传入trigram参数：
```bash
python main.py trigram < data/input.txt > data/output.txt
```

三元所需的运行时长较长，请耐心等待。

项目结构如下：

```
.
├── main.py                      # 主程序入口
├── data/                        # 输入输出数据和辅助表格
│   ├── input.txt                # 输入拼音序列
│   ├── output.txt               # 解码输出结果
│   ├── 拼音汉字表.txt            # 拼音到汉字映射表
│   └── 一二级汉字表.txt           # 合法汉字列表
├── corpus/
│   └── sina_news_gbk/          # 语料库文件夹（txt 格式）
├── src/                         # 所有源码文件
│   ├── bigram_mode.py          # Bigram 解码逻辑
│   ├── trigram_mode.py         # Trigram 解码逻辑
│   ├── train_bigram.py         # Bigram 模型训练代码
│   └── train_trigram.py        # Trigram 模型训练代码
└── readme.md                   # 本说明文档
```

依赖库说明：  
本项目仅使用以下 Python 标准库，无需安装第三方库：

- os  
- sys  
- json  
- math  
- re  
- ast  
- collections.defaultdict


# Pinyin Input Method

This project implements a pinyin input method system based on language models, supporting both **bigram** decoding (default) and **trigram** decoding (optional).

Please make sure the following resource files are placed in the correct directories:

- `data/拼音汉字表.txt`: mapping table from pinyin to Chinese characters
- `data/一二级汉字表.txt`: list of valid Chinese characters
- `corpus/sina_news_gbk/`: training corpus directory
- `data/input.txt`: input pinyin sequences, one sentence per line

For training and testing, I used `sina_news_gbk`, a corpus of Sina News articles from 2016.  
The corpus is not included in this repository, so users should prepare their own compatible corpus and place it under `corpus/`.

Before running the program, make sure the model resources can be generated properly.  
The model will be trained automatically on first run.

Default run (bigram model):

```bash
python main.py < data/input.txt > data/output.txt
```

To run the trigram model, pass the `trigram` argument:

```bash
python main.py trigram < data/input.txt > data/output.txt
```

Please note that the trigram mode takes significantly longer to run, so patience is advised.

## Project Structure

```text
.
├── main.py                      # main entry point
├── data/                        # input/output data and auxiliary tables
│   ├── input.txt                # input pinyin sequences
│   ├── output.txt               # decoded output
│   ├── 拼音汉字表.txt            # pinyin-to-character mapping table
│   └── 一二级汉字表.txt           # valid Chinese character list
├── corpus/
│   └── sina_news_gbk/           # corpus directory (txt files)
├── src/                         # source code
│   ├── bigram_mode.py           # bigram decoding logic
│   ├── trigram_mode.py          # trigram decoding logic
│   ├── train_bigram.py          # bigram model training code
│   └── train_trigram.py         # trigram model training code
└── README.md                    # this document
```

## Dependencies

This project uses only the following Python standard libraries, so no third-party packages are required:

- `os`
- `sys`
- `json`
- `math`
- `re`
- `ast`
- `collections.defaultdict`