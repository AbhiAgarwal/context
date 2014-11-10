context
=======

- Taking a news article that the user provides
  - Understanding the information behind that article
    - Using methods to find the item that is of the highest probability
  - Giving contextual background on that particular topic using certain sources
    - Contextual background could be: A timeline, news articles that relate, and definitions of words that are important
  - Good UI that takes an article, and displays it in a nice way with all this contextual information.

- Second build ontop:
  - Taking a term, and giving you context on that term.

- We can build initial term base by scraping articles, and seeing things that are relevent.

Libraries to use
  - https://github.com/miso-belica/sumy
  - http://libots.sourceforge.net/
  - https://github.com/nltk/nltk

```python
# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

LANGUAGE = "english"
SENTENCES_COUNT = 1

if __name__ == "__main__":
    url = "http://abhiagarwal.com/social-search"
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        print(sentence)
  ```
