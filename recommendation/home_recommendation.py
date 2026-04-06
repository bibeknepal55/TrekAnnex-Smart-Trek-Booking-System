from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count, Q
from treks.models import Trek
from bookings.models import Booking

def get_home_recommendations(user):
    """
    Returns 6 personalized trek recommendations for home page.
    
    Logic:
    - Logged-in users: Content-based filtering using booking history
    - Anonymous users: Popularity-based recommendations
    """
    
    if user.is_authenticated:
        return _get_personalized_recommendations(user)
    else:
        return _get_popular_recommendations()


def _get_personalized_recommendations(user):
    """
    Personalized recommendations based on user's booking history.
    Uses content-based similarity matching.
    """
    
    # Get user's past bookings
    user_bookings = Booking.objects.filter(user=user).select_related('trek')
    
    if not user_bookings.exists():
        # No history - fallback to popular treks
        return _get_popular_recommendations()
    
    # Get booked trek IDs to exclude
    booked_trek_ids = user_bookings.values_list('trek_id', flat=True)
    
    # Get available treks (exclude already booked)
    available_treks = list(Trek.objects.exclude(id__in=booked_trek_ids))
    
    if not available_treks:
        # All treks booked - return popular ones
        return _get_popular_recommendations()
    
    # Build feature vectors for user's booked treks
    booked_treks = [booking.trek for booking in user_bookings]
    user_features = _build_trek_features(booked_treks)
    
    # Build feature vectors for available treks
    available_features = _build_trek_features(available_treks)
    
    # Compute similarity
    vectorizer = TfidfVectorizer()
    all_features = user_features + available_features
    tfidf_matrix = vectorizer.fit_transform(all_features)
    
    # User profile = average of booked trek vectors
    user_vectors = tfidf_matrix[:len(user_features)]
    user_profile = user_vectors.mean(axis=0).A1.reshape(1, -1)
    
    # Available trek vectors
    trek_vectors = tfidf_matrix[len(user_features):]
    
    # Calculate similarity scores
    similarities = cosine_similarity(user_profile, trek_vectors)[0]
    
    # Rank treks by similarity
    trek_scores = list(zip(available_treks, similarities))
    trek_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Get top 6
    recommendations = [trek for trek, score in trek_scores[:6]]
    
    # If less than 6, fill with popular treks
    if len(recommendations) < 6:
        popular = _get_popular_recommendations()
        for trek in popular:
            if trek not in recommendations and trek.id not in booked_trek_ids:
                recommendations.append(trek)
                if len(recommendations) == 6:
                    break
    
    return recommendations


def _get_popular_recommendations():
    """
    Returns popular treks based on booking count.
    Fallback for anonymous users or users without history.
    """
    
    # Get treks ordered by booking count
    popular_treks = Trek.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count', '-created_at')[:6]
    
    return list(popular_treks)


def _build_trek_features(treks):
    """
    Builds text feature representations for treks.
    Combines: region, difficulty, duration, cost, interests.
    """
    
    features = []
    for trek in treks:
        # Seasons
        seasons = []
        if trek.season_spring: seasons.append('spring')
        if trek.season_summer: seasons.append('summer')
        if trek.season_autumn: seasons.append('autumn')
        if trek.season_winter: seasons.append('winter')
        
        # Interests
        interests = []
        if trek.interest_scenic: interests.append('scenic')
        if trek.interest_adventure: interests.append('adventure')
        if trek.interest_photography: interests.append('photography')
        if trek.interest_wildlife: interests.append('wildlife')
        if trek.interest_cultural: interests.append('cultural')
        if trek.interest_family: interests.append('family')
        
        # Normalize cost into range category
        cost_range = 'budget' if trek.cost < 1000 else 'mid' if trek.cost < 2000 else 'premium'
        
        # Combine features
        feature = f"{trek.region} {trek.difficulty} {cost_range} {' '.join(seasons)} {' '.join(interests)}"
        features.append(feature)
    
    return features
