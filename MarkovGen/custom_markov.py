import markovify
import re
import spacy

nlp = spacy.load("pl_core_news_sm")


class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        doc = nlp(sentence)
        words = [f"{token.text}::{token.pos_}" for token in doc]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        no_multiple_spaces = re.sub(r'\s+', ' ', sentence)
        return no_multiple_spaces