try:
    import jieba
except:
    jieba = None

def get_word_vector(word_list):
    word_vector = {}
    for word in word_list:
        word_vector[word] = word_vector.get(word, 0) + 1
    return word_vector

def jaccard_coefficient(word_vector1, word_vector2):
    common_words = set(word_vector1.keys()) and set(word_vector2.keys())
    all_words = set(word_vector1.keys() + word_vector2.keys())
    if len(all_words) == 0:
        return 0
    return len(common_words) * 1.0 / len(all_words)

class WordAnalysis:
    def __init__(self, text):
        self.text = text

    def get_word_segmentation_list(self, cut_all=False):
        if not jieba:
            return self.text.split(',')
        self.word_list = list(jieba.cut(self.text, cut_all))
        return self.word_list

    def get_word_freq_vector(self):
        if hasattr(self, 'word_list'):
            return get_word_vector(self.word_list)
        word_list = self.get_word_segmentation_list()
        return get_word_vector(word_list)

    def cal_word_vector_sim(self, word_vector, sim=jaccard_coefficient):
        return sim(word_vector, self.get_word_freq_vector())

    def get_abstract_of_text(self, topK=20):
        if not jieba:
            return self.text[:100]
        return jieba.analyse.extract_tags(self.text, topK)

    def __str__(self):
        word_frequency_list = []
        for word, freq in self.get_word_freq_vector().items():
            word_frequency_list.append((freq, word))
        word_frequency_list.sort()
        word_frequency_list.reverse()

        word_string_list = []
        for freq, word in word_frequency_list:
            word_string_list.append('%s:%s' % (word, freq))

        return '{' + ",".join(word_string_list) + '}'


if __name__ == '__main__':
    text = 'a,b,c,d,a,b,c,d,e,d,f,g,h,i,i,j'
    wa = WordAnalysis(text)
    print wa.get_word_segmentation_list()
    print wa.get_word_freq_vector()
    print wa.cal_word_vector_sim(wa.get_word_freq_vector())
    print wa








