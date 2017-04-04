from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def get_tf_idf( clean_reviews, ngram_range=(1,3), max_features=5000, min_df=0.0, max_df = 1.0):
    vectorizer = TfidfVectorizer(ngram_range = ngram_range,
                                 min_df = min_df,
                                 max_df = max_df,
                                 analyzer='word',
                                 max_features = max_features,
                                 stop_words=None,
                                 preprocessor=None,
                                 tokenizer=None
                                )
    

    feature_matrix = vectorizer.fit_transform(clean_reviews)

    return feature_matrix