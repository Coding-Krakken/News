import openai
import os
from typing import List, Dict
from ..models.schemas import Article, Claim, FactLedger
import json
import re

class FactCheckingService:
    """Service for AI-powered fact extraction and cross-corroboration"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
    
    async def extract_claims(self, articles: List[Article]) -> List[Claim]:
        """Extract claims from articles with attribution"""
        all_claims = []
        
        for article in articles:
            try:
                claims = await self._extract_claims_from_article(article)
                all_claims.extend(claims)
            except Exception as e:
                print(f"Error extracting claims from {article.url}: {str(e)}")
        
        return all_claims
    
    async def _extract_claims_from_article(self, article: Article) -> List[Claim]:
        """Extract claims from a single article using AI"""
        if not self.api_key:
            # Fallback to simple extraction without AI
            return self._simple_claim_extraction(article)
        
        try:
            prompt = f"""Extract factual claims from the following news article. 
For each claim, provide:
1. The exact claim text
2. Whether it's a factual assertion (not opinion)

Article Title: {article.title}
Source: {article.source_name}
Content: {article.content[:1500]}

Return a JSON array of claims with format:
[{{"text": "claim text", "is_factual": true}}]
"""
            
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a fact extraction assistant. Extract only verifiable factual claims."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            claims_data = json.loads(response.choices[0].message.content)
            
            claims = []
            for claim_dict in claims_data:
                if claim_dict.get("is_factual", False):
                    claim = Claim(
                        text=claim_dict["text"],
                        attribution=article.source_name,
                        article_url=article.url
                    )
                    claims.append(claim)
            
            return claims
        except Exception as e:
            print(f"AI extraction failed, using fallback: {str(e)}")
            return self._simple_claim_extraction(article)
    
    def _simple_claim_extraction(self, article: Article) -> List[Claim]:
        """Simple rule-based claim extraction (fallback)"""
        claims = []
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', article.content)
        
        for sentence in sentences[:5]:  # Limit to first 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:  # Minimum length
                claim = Claim(
                    text=sentence,
                    attribution=article.source_name,
                    article_url=article.url
                )
                claims.append(claim)
        
        return claims
    
    def cross_corroborate(self, claims: List[Claim]) -> List[Claim]:
        """Cross-corroborate claims across sources"""
        # Group similar claims
        claim_groups = self._group_similar_claims(claims)
        
        corroborated_claims = []
        
        for group in claim_groups:
            if len(group) > 1:
                # Multiple sources support this claim
                base_claim = group[0]
                base_claim.is_confirmed = True
                base_claim.corroboration_count = len(group)
                base_claim.supporting_sources = list(set([c.attribution for c in group]))
                corroborated_claims.append(base_claim)
            else:
                # Single source, uncorroborated
                corroborated_claims.append(group[0])
        
        return corroborated_claims
    
    def _group_similar_claims(self, claims: List[Claim]) -> List[List[Claim]]:
        """Group similar claims together"""
        groups = []
        used_indices = set()
        
        for i, claim1 in enumerate(claims):
            if i in used_indices:
                continue
            
            group = [claim1]
            used_indices.add(i)
            
            for j, claim2 in enumerate(claims[i+1:], start=i+1):
                if j in used_indices:
                    continue
                
                # Simple similarity check (could be improved with embeddings)
                if self._are_claims_similar(claim1.text, claim2.text):
                    group.append(claim2)
                    used_indices.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_claims_similar(self, text1: str, text2: str) -> bool:
        """Check if two claims are similar"""
        # Simple word overlap check
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1 & words2)
        min_length = min(len(words1), len(words2))
        
        return overlap / min_length > 0.5
    
    async def generate_fact_ledger(self, story_id: str, articles: List[Article]) -> FactLedger:
        """Generate a fact ledger for a story"""
        # Extract claims from all articles
        all_claims = await self.extract_claims(articles)
        
        # Cross-corroborate claims
        corroborated_claims = self.cross_corroborate(all_claims)
        
        # Separate into confirmed, disputed, and uncorroborated
        confirmed = [c for c in corroborated_claims if c.is_confirmed]
        disputed = [c for c in corroborated_claims if c.is_disputed]
        uncorroborated = [c for c in corroborated_claims if not c.is_confirmed and not c.is_disputed]
        
        ledger = FactLedger(
            story_id=story_id,
            confirmed_claims=confirmed,
            disputed_claims=disputed,
            uncorroborated_claims=uncorroborated
        )
        
        return ledger
