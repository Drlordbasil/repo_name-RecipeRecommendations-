from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import re
import nltk
import pandas as pd
from bs4 import BeautifulSoup
import requests
Optimized Python script:


class Recipe:
    def __init__(self, title, ingredients, preparation_steps, rating, reviews):
        self.title = title
        self.ingredients = ingredients
        self.preparation_steps = preparation_steps
        self.rating = rating
        self.reviews = reviews


class User:
    def __init__(self, name, dietary_preferences, ingredient_restrictions, cuisine_choices, cooking_preferences):
        self.name = name
        self.dietary_preferences = dietary_preferences
        self.ingredient_restrictions = ingredient_restrictions
        self.cuisine_choices = cuisine_choices
        self.cooking_preferences = cooking_preferences
        self.reviews = []


class RecipeRecommendationSystem:
    def __init__(self):
        self.recipes = []
        self.users = []
        self.user_profiles = {}

    def run(self):
        self.load_recipes()
        self.load_users()
        self.create_user_profiles()
        self.generate_recommendations()

    def load_recipes(self):
        # Replace with desired website containing recipes
        url = "https://www.allrecipes.com"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        recipe_elements = soup.find_all("div", class_="card__detailsContainer")

        for element in recipe_elements:
            title = element.find("h3", class_="headline").text.strip()
            ingredients = [
                ingredient.text.strip()
                for ingredient in element.find_all("span", itemprop="recipeIngredient")
            ]
            preparation_steps = element.find(
                "div", class_="directions-section").text.strip().split("\n")
            rating = element.find(
                "span", class_="review-star-text").text.strip()
            comments = element.find_all("div", class_="review-comment")
            reviews = [comment.text.strip() for comment in comments]

            recipe = Recipe(title, ingredients,
                            preparation_steps, rating, reviews)
            self.recipes.append(recipe)

    def load_users(self):
        user_profile_data = [
            {"name": "John", "dietary_preferences": ["vegetarian"],
             "ingredient_restrictions": ["nuts"], "cuisine_choices": ["Italian"],
             "cooking_preferences": ["quick"]},
            {"name": "Mary", "dietary_preferences": ["gluten-free"],
             "ingredient_restrictions": ["dairy"], "cuisine_choices": ["Mexican"],
             "cooking_preferences": ["slow"]},
            {"name": "David", "dietary_preferences": ["vegan"],
             "ingredient_restrictions": ["gluten"], "cuisine_choices": ["Indian"],
             "cooking_preferences": ["balanced"]}
        ]

        self.users = [User(data["name"], data["dietary_preferences"], data["ingredient_restrictions"],
                           data["cuisine_choices"], data["cooking_preferences"]) for data in user_profile_data]

        self.user_profiles = {
            user.name: user.__dict__ for user in self.users
        }

    def create_user_profiles(self):
        nltk.download("stopwords")
        nltk.download("vader_lexicon")
        stop_words = set(stopwords.words("english"))

        reviews = [recipe.reviews for recipe in self.recipes]
        cleaned_reviews = [self.clean_text(
            review) for review_list in reviews for review in review_list]
        without_stop_words = [self.remove_stop_words(
            review, stop_words) for review in cleaned_reviews]
        sentiment_scores = [self.sentiment_analysis(
            review) for review in without_stop_words]
        sentiment_scores = [score for score, _ in sentiment_scores]

        for user in self.users:
            user_profile = self.user_profiles[user.name]
            user_profile["reviews"] = sentiment_scores

    def clean_text(self, text):
        cleaned_text = text.lower()
        cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)
        cleaned_text = re.sub(r"\d+", "", cleaned_text)
        return cleaned_text

    def remove_stop_words(self, text, stop_words):
        words = text.split()
        filtered_words = [word for word in words if word not in stop_words]
        text_without_stop_words = " ".join(filtered_words)
        return text_without_stop_words

    def sentiment_analysis(self, text):
        sid = SentimentIntensityAnalyzer()
        sentiment_score = sid.polarity_scores(text)
        return sentiment_score

    def generate_recommendations(self):
        user_profiles = self.user_profiles
        recipe_data = [" ".join(recipe.ingredients) for recipe in self.recipes]

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(recipe_data)
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        scaler = MinMaxScaler()
        scaled_similarity_matrix = scaler.fit_transform(similarity_matrix)

        n_clusters = len(self.users)
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(
            scaled_similarity_matrix)

        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(scaled_similarity_matrix)
        principal_df = pd.DataFrame(
            data=principal_components, columns=["PC1", "PC2"])
        principal_df["User"] = kmeans.labels_

        user_profiles_df = pd.DataFrame.from_dict(
            user_profiles, orient="index")
        combined_df = pd.concat([principal_df, user_profiles_df], axis=1)

        recommendations = []

        for user in self.users:
            user_cluster = combined_df[combined_df["User"] == user.name]["User"].to_numpy()[
                0]
            user_recommendations = combined_df[combined_df["User"] == user.name].drop(columns=["User"]).to_dict(
                orient="records")[0]
            recommendations.append({
                "user": user.name,
                "user_cluster": user_cluster,
                "user_recommendations": user_recommendations
            })

        self.serve_recommendations(recommendations)

    def serve_recommendations(self, recommendations):
        for recommendation in recommendations:
            user = recommendation["user"]
            user_recommendations = recommendation["user_recommendations"]

            print(f"Recommendations for {user}:")
            for rec in user_recommendations:
                print(rec)

    def collect_feedback(self):
        pass

    def refine_recommendations(self):
        pass


rrs = RecipeRecommendationSystem()
rrs.run()
