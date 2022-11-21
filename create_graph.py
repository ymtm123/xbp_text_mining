import re
import nlplot
import pandas as pd
from datetime import datetime
from janome.tokenizer import Tokenizer


def main():
    # stop_n_topで指定する頻出上位の単語, stop_min_freqで指定する頻出回数以下の単語を指定できる
    stopwords = ["する", "ある", "あと", "いる", "なる", "思う"]
    stop_n_top = 7
    stop_min_freq = 5

    # 指定数以下のエッジのノードをプロット対象から除外する
    min_edge_frequency = 4

    str_now = datetime.now().strftime("%H%M%S")
    create(stopwords, stop_n_top, stop_min_freq, min_edge_frequency, str_now)


def create(stopwords, top_n, min_freq, min_edge_frequency, str_now):
    # figure
    width = 800
    height = 600

    # dataset
    f = open('./myfile.txt', 'r', encoding="utf-8")
    data = f.read()
    f.close()

    # df = pd.DataFrame({'text': data.split("。")})
    df = pd.DataFrame({'text': re.split('[。?？()（）]', data)})

    # 形態素結果をリスト化し、データフレームdfに結果を列追加する
    df['words'] = df['text'].apply(subtract_words)

    npt = nlplot.NLPlot(df, target_col='words')

    # top_nで指定する頻出上位の単語, min_freqで指定する頻出回数以下の単語を指定できる
    stopwords += npt.get_stopword(top_n=top_n, min_freq=min_freq)

    # 頻出ランキンググラフ
    npt.bar_ngram(
        title=str_now + '_単語頻出',
        xaxis_label='word_count',
        yaxis_label='word',
        ngram=1,
        top_n=20,
        stopwords=stopwords,
        width=width,
        height=height,
        save=True
    )

    # ワードクラウド
    # npt.wordcloud(
    #     max_words=100,
    #     max_font_size=100,
    #     colormap='tab20_r',
    #     stopwords=stopwords,
    #     width=width,
    #     height=height,
    #     save=True
    # )

    npt.build_graph(stopwords=stopwords, min_edge_frequency=min_edge_frequency)

    try:
        # 共起ネットワーク
        npt.co_network(
            title=str_now + '_共起ネットワーク',
            node_size='adjacency_frequency',
            width=width,
            height=height,
            save=True
        )

        # サンバースト
        npt.sunburst(
            title=str_now + '_サンバースト',
            colorscale=True,
            color_continuous_scale='Oryel',
            width=width,
            height=height,
            save=True
        )
    except ZeroDivisionError:
        print("min_edge_frequencyの値が大きすぎます。")


def subtract_words(text):
    tokenizer = Tokenizer('./user_dict.csv', udic_enc='utf8')
    tokens = tokenizer.tokenize(text)

    # 形態素解析した結果を格納するリスト
    wordlist = []
    for token in tokens:
        base_word = token.base_form
        hinshi_00 = token.part_of_speech.split(',')[0]
        hinshi_01 = token.part_of_speech.split(',')[1]

        if hinshi_01 != "非自立":
            if hinshi_00 == "名詞":
                if hinshi_01 != "数":
                    wordlist.append(base_word)
            elif hinshi_00 == "形容詞":
                wordlist.append(base_word)
            elif hinshi_00 == "動詞":
                if hinshi_01 == "自立":
                    wordlist.append(base_word)

    return wordlist


if __name__ == "__main__":
    main()
