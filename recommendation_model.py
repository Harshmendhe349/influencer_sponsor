# recommendation_model.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    def __init__(self, data_items, item_type="influencer"):
        self.data_items = data_items
        self.item_type = item_type
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.texts = [f"{item['category']} {item['niche']}" for item in self.data_items]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.texts)

    def recommend(self, input_category, input_niche, top_n=5):
        input_text = f"{input_category} {input_niche}"
        input_vec = self.vectorizer.transform([input_text])
        similarity_scores = cosine_similarity(input_vec, self.tfidf_matrix).flatten()

        for i, item in enumerate(self.data_items):
            self.data_items[i]["score"] = round(float(similarity_scores[i]), 4)

        sorted_items = sorted(self.data_items, key=lambda x: x["score"], reverse=True)

        if all(score["score"] == 0.0 for score in sorted_items):
            if self.item_type == "influencer":
                sorted_items = sorted(self.data_items, key=lambda x: x.get("followers", 0), reverse=True)
            elif self.item_type == "campaign":
                sorted_items = sorted(self.data_items, key=lambda x: x.get("budget", 0), reverse=True)

        return sorted_items[:top_n]
