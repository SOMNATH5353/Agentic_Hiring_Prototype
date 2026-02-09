# ingestion/preprocess.py

import re
from typing import List

# Regex patterns for PII
EMAIL_PATTERN = r"\b[\w\.-]+@[\w\.-]+\.\w+\b"
PHONE_PATTERN = r"\b(\+?\d[\d\s\-\(\)]{7,}\d)\b"
URL_PATTERN = r"(https?://\S+|www\.\S+)"


def redact_pii(text: str) -> str:
    """
    Remove personal identifiable information from text.
    """
    text = re.sub(EMAIL_PATTERN, "[EMAIL]", text)
    text = re.sub(PHONE_PATTERN, "[PHONE]", text)
    text = re.sub(URL_PATTERN, "[URL]", text)
    return text


def clean_text(text: str) -> str:
    """
    Clean text while preserving readability and word spacing.
    """
    # Remove multiple spaces but keep single spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep periods, commas, hyphens
    text = re.sub(r'[^\w\s\.\,\-\:\;\(\)]', '', text)
    
    # Clean up any resulting multiple spaces again
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def sentence_split(text: str) -> List[str]:
    """
    Split text into meaningful chunks (sentences or bullet points).
    """
    # First, split by double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    
    all_sentences = []
    
    for para in paragraphs:
        # Split by single newlines (lines within paragraph)
        lines = para.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if len(line) < 5:
                continue
            
            # If line ends with sentence terminator, it's likely a complete sentence
            if line.endswith(('.', '!', '?', ':')):
                all_sentences.append(line)
            # If line contains sentence terminators, split it
            elif any(term in line for term in ['. ', '! ', '? ']):
                # Split by sentence terminators but keep the terminator
                sub_sentences = re.split(r'([.!?])\s+', line)
                temp = ""
                for i in range(0, len(sub_sentences)-1, 2):
                    if i+1 < len(sub_sentences):
                        sent = (sub_sentences[i] + sub_sentences[i+1]).strip()
                        if len(sent) > 10:
                            all_sentences.append(sent)
                # Add any remaining text
                if len(sub_sentences) % 2 == 1 and len(sub_sentences[-1].strip()) > 10:
                    all_sentences.append(sub_sentences[-1].strip())
            # Otherwise, treat the whole line as a sentence/bullet point
            else:
                all_sentences.append(line)
    
    return all_sentences


def split_joined_words(text: str) -> str:
    """
    Attempt to fix joined words (camelCase, etc.).
    Only apply to obvious cases to avoid breaking valid text.
    """
    # Split camelCase only if there's a clear pattern
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    return text


def preprocess_text(text: str) -> List[str]:
    """
    Preprocess text by:
    1. Redacting PII first
    2. Splitting into sentences while preserving structure
    3. Minimal cleaning to maintain readability
    """
    # Step 1: Redact PII from original text
    text = redact_pii(text)
    
    # Step 2: Fix obvious joined words (be conservative)
    text = split_joined_words(text)
    
    # Step 3: Split into sentences BEFORE aggressive cleaning
    sentences = sentence_split(text)
    
    # Step 4: Light cleaning of each sentence
    cleaned_sentences = []
    for sent in sentences:
        cleaned = clean_text(sent)
        
        # Filter out very short sentences and obvious PII headers
        if len(cleaned) > 15:  # Increased minimum length
            # Skip lines that look like headers with personal info
            lower_sent = cleaned.lower()
            skip_keywords = ['linkedin', 'github', 'gmail', 'contact info', 
                           'personal details', 'email', 'phone']
            
            if not any(kw in lower_sent for kw in skip_keywords):
                # Skip lines with too many redactions
                if cleaned.count('[EMAIL]') + cleaned.count('[PHONE]') + cleaned.count('[URL]') < 3:
                    cleaned_sentences.append(cleaned)
    
    return cleaned_sentences
