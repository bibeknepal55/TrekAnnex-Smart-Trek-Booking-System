from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def recommend_treks(user_prefs, treks):
    if not treks:
        return []
    
    # Build trek features
    trek_features = []
    for trek in treks:
        seasons = []
        if trek.season_spring: seasons.append('spring')
        if trek.season_summer: seasons.append('summer')
        if trek.season_autumn: seasons.append('autumn')
        if trek.season_winter: seasons.append('winter')
        
        interests = []
        if trek.interest_scenic: interests.append('scenic')
        if trek.interest_adventure: interests.append('adventure')
        if trek.interest_photography: interests.append('photography')
        if trek.interest_wildlife: interests.append('wildlife')
        if trek.interest_cultural: interests.append('cultural')
        if trek.interest_family: interests.append('family')
        
        feature = f"{trek.region} {trek.difficulty} {' '.join(seasons)} {' '.join(interests)} {trek.description}"
        trek_features.append(feature)
    
    # Build user preference feature
    user_seasons = user_prefs.get('seasons', [])
    user_interests = user_prefs.get('interests', [])
    user_region = user_prefs.get('region', 'Any')
    user_difficulty = user_prefs.get('difficulty', 'Any')
    
    user_feature = f"{user_region if user_region != 'Any' else ''} {user_difficulty if user_difficulty != 'Any' else ''} {' '.join(user_seasons)} {' '.join(user_interests)}"
    
    # TF-IDF and cosine similarity
    vectorizer = TfidfVectorizer()
    all_features = trek_features + [user_feature]
    tfidf_matrix = vectorizer.fit_transform(all_features)
    
    user_vector = tfidf_matrix[-1]
    trek_vectors = tfidf_matrix[:-1]
    
    similarities = cosine_similarity(user_vector, trek_vectors)[0]
    
    # Filter by budget, duration, altitude
    results = []
    for idx, trek in enumerate(treks):
        score = similarities[idx] * 100
        
        # Apply filters
        if trek.cost > user_prefs.get('max_budget', 10000):
            continue
        if trek.cost < user_prefs.get('min_budget', 0):
            continue
        if trek.max_duration > user_prefs.get('max_duration', 100):
            continue
        if trek.max_altitude > user_prefs.get('max_altitude', 10000):
            continue
        
        if score >= 3:
            results.append({
                'trek': trek,
                'score': round(score)
            })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]
