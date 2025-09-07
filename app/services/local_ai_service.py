"""
Local AI service using free libraries and APIs.
No OpenAI required!
"""
import logging
import re
import requests
import os
from typing import Optional
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class LocalAIService:
    """Local AI service using free libraries."""
    
    def __init__(self):
        logging.info("Local AI Service initialized")
    
    async def generate_title(self, content: str) -> str:
        """Generate a title using TextBlob and NLTK."""
        if not content or len(content.strip()) < 10:
            return "Untitled Note"
        
        try:
            # Use TextBlob for sentiment and key phrase extraction
            blob = TextBlob(content)
            
            # Extract noun phrases as potential title words
            noun_phrases = blob.noun_phrases
            
            if noun_phrases:
                # Take the first few noun phrases
                title_words = noun_phrases[:3]
                title = " ".join(title_words).title()
            else:
                # Fallback: use first sentence
                sentences = sent_tokenize(content)
                if sentences:
                    first_sentence = sentences[0]
                    # Clean and shorten
                    title = re.sub(r'[^\w\s]', '', first_sentence)
                    title = ' '.join(title.split()[:6])  # Max 6 words
                else:
                    title = content[:30].strip()
            
            # Clean up title
            title = re.sub(r'\s+', ' ', title).strip()
            return title[:50] if title else "Untitled Note"
            
        except Exception as e:
            logging.error(f"Local title generation failed: {e}")
            return self._fallback_title(content)
    
    async def summarize_content(self, content: str) -> str:
        """Summarize content using extractive summarization."""
        if not content or len(content.strip()) < 20:
            return content
        
        try:
            # Split into sentences
            sentences = sent_tokenize(content)
            
            if len(sentences) <= 2:
                return content
            
            # Use TextBlob for sentence scoring
            blob = TextBlob(content)
            
            # Simple extractive summarization
            # Take first and last sentences, plus middle if long enough
            if len(sentences) >= 4:
                summary_sentences = [sentences[0], sentences[-1]]
                if len(sentences) > 4:
                    # Add middle sentence
                    middle_idx = len(sentences) // 2
                    summary_sentences.insert(1, sentences[middle_idx])
            else:
                summary_sentences = sentences[:2]
            
            summary = '. '.join(summary_sentences)
            
            # Ensure proper ending
            if not summary.endswith(('.', '!', '?')):
                summary += '.'
            
            return summary
            
        except Exception as e:
            logging.error(f"Local summarization failed: {e}")
            return self._fallback_summary(content)
    
    async def improve_content(self, content: str) -> str:
        """Improve content using smart text processing."""
        if not content or len(content.strip()) < 10:
            return content
        
        try:
            # Start with original content
            improved = content.strip()
            
            # Fix common capitalization issues
            improved = self._fix_capitalization(improved)
            
            # Fix common punctuation issues
            improved = self._fix_punctuation(improved)
            
            # Fix common spacing issues
            improved = self._fix_spacing(improved)
            
            # Fix common grammar issues
            improved = self._fix_common_grammar(improved)
            
            # Fix technical terms
            improved = self._fix_technical_terms(improved)
            
            # Ensure proper sentence structure
            improved = self._improve_sentence_structure(improved)
            
            return f"[AI Enhanced] {improved}"
            
        except Exception as e:
            logging.error(f"Local content improvement failed: {e}")
            return self._fallback_improvement(content)
    
    def _fix_capitalization(self, text: str) -> str:
        """Fix capitalization issues."""
        # Capitalize first letter of each sentence
        sentences = re.split(r'([.!?]\s*)', text)
        result = []
        
        for i, part in enumerate(sentences):
            if i == 0 or (i > 0 and sentences[i-1].endswith(('.', '!', '?'))):
                if part.strip() and part[0].islower():
                    part = part[0].upper() + part[1:]
            result.append(part)
        
        return ''.join(result)
    
    def _fix_punctuation(self, text: str) -> str:
        """Fix punctuation issues."""
        # Fix multiple periods
        text = re.sub(r'\.\s*\.+', '.', text)
        # Fix spaces before punctuation
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)
        # Fix missing spaces after punctuation
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        return text
    
    def _fix_spacing(self, text: str) -> str:
        """Fix spacing issues."""
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Fix spaces at beginning and end
        text = text.strip()
        return text
    
    def _fix_common_grammar(self, text: str) -> str:
        """Fix common grammar issues."""
        # Fix common contractions and grammar
        fixes = {
            r'\bit\s+allow\b': 'it allows',
            r'\bit\s+are\b': 'it is',
            r'\bit\s+have\b': 'it has',
            r'\bit\s+offer\b': 'it offers',
            r'\bit\s+represent\b': 'it represents',
            r'\bflutter\s+have\b': 'Flutter has',
            r'\bflutter\s+represent\b': 'Flutter represents',
            r'\bstate\s+management\s+are\b': 'state management is',
            r'\bthere\s+is\s+several\b': 'there are several',
            r'\bthe\s+community\s+support\s+are\b': 'the community support is',
        }
        
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_technical_terms(self, text: str) -> str:
        """Fix technical terms and proper nouns."""
        # Fix common technical terms
        fixes = {
            r'\bflutter\b': 'Flutter',
            r'\bdart\b': 'Dart',
            r'\bios\b': 'iOS',
            r'\bandroid\b': 'Android',
            r'\bgoogle\b': 'Google',
            r'\bpub\.dev\b': 'pub.dev',
            r'\bprovider\b': 'Provider',
            r'\briverpod\b': 'Riverpod',
            r'\bbloc\b': 'Bloc',
            r'\bgetx\b': 'GetX',
            r'\bapi\b': 'API',
            r'\bui\b': 'UI',
            r'\bux\b': 'UX',
        }
        
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _improve_sentence_structure(self, text: str) -> str:
        """Improve sentence structure and flow."""
        # Split into sentences
        sentences = re.split(r'([.!?])', text)
        result = []
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i].strip()
                punctuation = sentences[i + 1]
                
                if sentence:
                    # Add some improvements
                    if sentence.lower().startswith('overall'):
                        sentence = sentence[0].upper() + sentence[1:]
                        if not sentence.endswith(('.')):
                            sentence += '.'
                    
                    result.append(sentence + punctuation)
        
        return ' '.join(result)
    
    async def suggest_tags(self, content: str) -> str:
        """Suggest tags using NLTK and TextBlob."""
        if not content or len(content.strip()) < 10:
            return "general, notes"
        
        try:
            # Use TextBlob for noun extraction
            blob = TextBlob(content)
            
            # Get noun phrases
            noun_phrases = blob.noun_phrases
            
            # Get individual nouns
            nouns = [word for word, pos in blob.tags if pos in ['NN', 'NNS', 'NNP', 'NNPS']]
            
            # Combine and filter
            all_words = noun_phrases + nouns
            
            # Remove stopwords and short words
            try:
                stop_words = set(stopwords.words('english') + stopwords.words('turkish'))
            except:
                stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
            
            filtered_words = []
            for word in all_words:
                word_lower = word.lower()
                if (len(word_lower) > 3 and 
                    word_lower not in stop_words and 
                    word_lower not in ['flutter', 'app', 'application']):
                    filtered_words.append(word_lower)
            
            # Remove duplicates and limit
            unique_words = list(dict.fromkeys(filtered_words))[:5]
            
            # Add some default tags if not enough
            if len(unique_words) < 2:
                unique_words.extend(['development', 'notes'])
            
            return ', '.join(unique_words[:5])
            
        except Exception as e:
            logging.error(f"Local tag suggestion failed: {e}")
            return self._fallback_tags(content)
    
    async def analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment using TextBlob."""
        if not content:
            return "neutral"
        
        try:
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return "positive"
            elif polarity < -0.1:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            logging.error(f"Sentiment analysis failed: {e}")
            return "neutral"
    
    async def generate_ideas(self, content: str) -> str:
        """Generate ideas based on content using Hugging Face API."""
        if not content or len(content.strip()) < 10:
            return "Please provide more content to generate ideas."
        
        try:
            # Use Hugging Face Inference API for idea generation
            # Using a text generation model like GPT-2 or similar
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
            
            if not huggingface_token:
                logging.warning("HUGGINGFACE_TOKEN not found, using local generation")
                return await self._local_generate_ideas(content)
            
            headers = {"Authorization": f"Bearer {huggingface_token}"}
            
            # Create a prompt for idea generation
            prompt = f"Based on this content: '{content[:200]}...', here are some related ideas and suggestions:\n\n"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 200,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Clean up the generated text
                    ideas = generated_text.replace(prompt, '').strip()
                    if ideas:
                        return f"[AI Generated Ideas]\n\n{ideas}"
            
            # Fallback to local idea generation
            return await self._local_generate_ideas(content)
            
        except Exception as e:
            logging.error(f"Hugging Face idea generation failed: {e}")
            return await self._local_generate_ideas(content)
    
    async def _local_generate_ideas(self, content: str) -> str:
        """Local fallback for idea generation."""
        try:
            blob = TextBlob(content)
            
            # Extract key concepts
            noun_phrases = blob.noun_phrases
            sentences = sent_tokenize(content)
            
            ideas = []
            
            # Generate ideas based on content
            if "flutter" in content.lower():
                ideas.extend([
                    "• Consider using different state management solutions (Provider, Riverpod, Bloc)",
                    "• Explore Flutter's new features and widgets",
                    "• Implement responsive design for different screen sizes",
                    "• Add animations and transitions for better UX"
                ])
            
            if "development" in content.lower():
                ideas.extend([
                    "• Set up automated testing and CI/CD pipeline",
                    "• Implement code review process",
                    "• Consider using design patterns and best practices",
                    "• Document your code and create user guides"
                ])
            
            if "app" in content.lower():
                ideas.extend([
                    "• Add user authentication and authorization",
                    "• Implement offline functionality",
                    "• Add push notifications",
                    "• Consider monetization strategies"
                ])
            
            # Generic ideas based on content length and complexity
            if len(sentences) > 3:
                ideas.extend([
                    "• Break down complex topics into smaller sections",
                    "• Add examples and use cases",
                    "• Create a step-by-step guide",
                    "• Include troubleshooting tips"
                ])
            
            if noun_phrases:
                ideas.extend([
                    f"• Research more about {noun_phrases[0]}",
                    f"• Explore related concepts to {noun_phrases[0]}",
                    "• Create a comparison with similar topics",
                    "• Add practical applications and examples"
                ])
            
            # Default ideas if nothing specific found
            if not ideas:
                ideas = [
                    "• Expand on the main points with more detail",
                    "• Add examples and case studies",
                    "• Include pros and cons analysis",
                    "• Create a summary or conclusion",
                    "• Add related topics and references"
                ]
            
            return f"[AI Generated Ideas]\n\n" + "\n".join(ideas[:6])  # Limit to 6 ideas
            
        except Exception as e:
            logging.error(f"Local idea generation failed: {e}")
            return "[AI Generated Ideas]\n\n• Expand on the main points\n• Add examples and details\n• Include practical applications\n• Create a comprehensive guide"
    
    def _fallback_title(self, content: str) -> str:
        """Fallback title generation."""
        sentences = content.split('.')
        if sentences and len(sentences[0]) > 10:
            title = sentences[0].strip()
        else:
            title = content[:50].strip()
        
        title = re.sub(r'[^\w\s-]', '', title)
        title = ' '.join(title.split())
        return title[:50] if title else "Untitled Note"
    
    def _fallback_summary(self, content: str) -> str:
        """Fallback summary."""
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        if len(sentences) <= 2:
            return content
        
        if len(sentences) >= 3:
            summary = f"{sentences[0]}. {sentences[-1]}."
        else:
            summary = sentences[0]
        
        return summary[:200]
    
    def _fallback_improvement(self, content: str) -> str:
        """Fallback improvement."""
        improved = content.strip()
        improved = re.sub(r'\s+', ' ', improved)
        
        if improved and improved[0].islower():
            improved = improved[0].upper() + improved[1:]
        
        if improved and not improved.endswith(('.', '!', '?')):
            improved += '.'
        
        return f"[Basic] {improved}"
    
    def _fallback_tags(self, content: str) -> str:
        """Fallback tag suggestion."""
        words = re.findall(r'\b\w+\b', content.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        word_count = {}
        for word in keywords:
            word_count[word] = word_count.get(word, 0) + 1
        
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        tags = [word for word, count in sorted_words[:3]]
        
        return ', '.join(tags) if tags else 'general, notes'


# Global local AI service instance
local_ai_service = LocalAIService()
