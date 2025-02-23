def compute_confidence_score(source_reliability, news_severity, language_certainty, contextual_relevance):
    """
    Computes a confidence score (0-1.0) for adverse news classification.
    
    Parameters:
        source_reliability (float): 0 to 1.0 based on trustworthiness of the source.
        news_severity (float): 0 to 1.0 based on the severity of the news type.
        language_certainty (float): 0 to 1.0 based on certainty in language used.
        contextual_relevance (float): 0 to 1.0 based on how directly the article relates to financial crime.
        
    Returns:
        float: Confidence score between 0 and 1.0
    """
    return (0.4 * source_reliability) + (0.3 * news_severity) + (0.2 * language_certainty) + (0.1 * contextual_relevance)


# Example 1: High-confidence case
source_reliability = 1.0  # Government report
news_severity = 1.0  # Money laundering case
language_certainty = 1.0  # Strong language ("arrested for...")
contextual_relevance = 1.0  # Directly linked to financial crime

score = compute_confidence_score(source_reliability, news_severity, language_certainty, contextual_relevance)
print(f"Confidence Score: {score:.2f}")  # Expected: 1.0

# Example 2: Medium-confidence case
source_reliability = 0.7  # Reputable news agency
news_severity = 0.8  # Fraud case
language_certainty = 0.6  # Moderate certainty ("alleged fraud")
contextual_relevance = 0.7  # Indirect but strong connection

score = compute_confidence_score(source_reliability, news_severity, language_certainty, contextual_relevance)
print(f"Confidence Score: {score:.2f}")  # Expected: ~0.76

# Example 3: Low-confidence case
source_reliability = 0.4  # Blog post
news_severity = 0.5  # Ethical misconduct
language_certainty = 0.4  # Speculative wording
contextual_relevance = 0.3  # Weak connection

score = compute_confidence_score(source_reliability, news_severity, language_certainty, contextual_relevance)
print(f"Confidence Score: {score:.2f}")  # Expected: ~0.47
