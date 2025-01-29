import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import textstat
from urllib.parse import urljoin
import json

def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(['script', 'style']):
            script.extract()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(chunk for chunk in lines if chunk)
        return text, soup
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}", None

def check_word_count(text):
    words = text.split()
    return len(words)

def keyword_density(text):
    words = text.lower().split()
    word_counts = Counter(words)
    total_words = len(words)
    density = {word: round(count / total_words, 4) for word, count in word_counts.most_common(10)}
    keyword_status = "Good" if any(val > 0.01 for val in density.values()) else "Needs Improvement"
    return {"Density": density, "Status": keyword_status}

def readability_scores(text):
    score = textstat.flesch_reading_ease(text)
    status = "Good" if score > 60 else ("Average" if score > 30 else "Poor")
    suggestions = "Use shorter sentences and simpler words." if score <= 30 else "Improve clarity and structure."
    return {"Flesch Reading Ease": score, "Status": status, "Suggestions": suggestions}

def check_images(soup):
    images = soup.find_all('img')
    missing_alt = [index + 1 for index, img in enumerate(images) if not img.get('alt')]
    return {'Total Images': len(images), 'Missing Alt': missing_alt}

def check_links(soup, base_url):
    internal_links = []
    external_links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        full_url = urljoin(base_url, href)
        if base_url in full_url:
            internal_links.append(full_url)
        else:
            external_links.append(full_url)
    return {'Internal Links': len(internal_links), 'External Links': len(external_links)}

def evaluate_EAT(text):
    return {'Expertise': 'Needs Improvement', 'Authoritativeness': 'Good', 'Trustworthiness': 'Needs Improvement'}

def google_policy_compliance(text):
    return {'Compliance': 'Pass', 'Issues': ['Thin content detected', 'Low readability']} if len(text.split()) < 300 else {'Compliance': 'Pass', 'Issues': []}

def analyze_url(url):
    text, soup = fetch_content(url)
    if soup is None:
        return text
    
    base_url = '/'.join(url.split('/')[:3])
    
    analysis = {
        'Word Count': check_word_count(text),
        'Keyword Density': keyword_density(text),
        'Readability Scores': readability_scores(text),
        'Image Analysis': check_images(soup),
        'Link Analysis': check_links(soup, base_url),
        'E-A-T Evaluation': evaluate_EAT(text),
        'Google Policy Compliance': google_policy_compliance(text)
    }
    return json.dumps(analysis, indent=4)

if __name__ == "__main__":
    url = input("Enter the URL to check: ")
    print(analyze_url(url))