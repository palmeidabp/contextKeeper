#!/usr/bin/env python3
"""Extract and categorize information from stdin text."""

import sys
import json
import re


def categorize_content(text):
    """Categorize content based on keywords and patterns."""
    text_lower = text.lower()
    
    # Define category patterns
    if any(kw in text_lower for kw in ['todo', 'task', 'action item', 'follow up']):
        return 'action'
    elif any(kw in text_lower for kw in ['meeting', 'discussed', 'agreed', 'decided']):
        return 'meeting_note'
    elif any(kw in text_lower for kw in ['idea', 'thought', 'consider', 'maybe']):
        return 'idea'
    elif any(kw in text_lower for kw in ['question', 'how to', 'what is', 'why']):
        return 'question'
    elif any(kw in text_lower for kw in ['bug', 'error', 'issue', 'problem', 'fix']):
        return 'issue'
    else:
        return 'note'


def extract_keywords(text, max_keywords=5):
    """Extract important keywords from text."""
    # Simple keyword extraction: find capitalized words and important terms
    words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{5,}\b', text)
    
    # Filter out common stop words
    stop_words = {'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'when', 'where', 'what', 'which', 'their', 'would', 'could', 'should'}
    keywords = [w.lower() for w in words if w.lower() not in stop_words]
    
    # Return unique keywords, limited to max_keywords
    seen = set()
    result = []
    for kw in keywords:
        if kw not in seen and len(kw) > 2:
            seen.add(kw)
            result.append(kw)
        if len(result) >= max_keywords:
            break
    
    return result


def determine_importance(text, category):
    """Determine importance level based on content."""
    text_lower = text.lower()
    
    high_indicators = ['critical', 'urgent', 'asap', 'deadline', 'blocking', 'important', 'must', 'need to']
    low_indicators = ['maybe', 'someday', 'nice to have', 'consider', 'think about']
    
    if any(kw in text_lower for kw in high_indicators):
        return 'high'
    elif any(kw in text_lower for kw in low_indicators):
        return 'low'
    elif category in ['action', 'issue']:
        return 'medium'
    else:
        return 'low'


def process_text(text):
    """Process text and return structured data."""
    lines = text.strip().split('\n')
    results = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        category = categorize_content(line)
        keywords = extract_keywords(line)
        importance = determine_importance(line, category)
        
        results.append({
            'category': category,
            'content': line,
            'keywords': keywords,
            'importance': importance
        })
    
    return results


def main():
    """Read from stdin and output JSON array."""
    text = sys.stdin.read()
    
    if not text.strip():
        print(json.dumps([], indent=2))
        return
    
    results = process_text(text)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
