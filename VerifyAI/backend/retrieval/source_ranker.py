class SourceRanker:
    def rank(self, results: list[dict], query: str) -> list[dict]:
        query_words = set(query.lower().split())
        if not query_words:
            return results

        ranked = []
        for res in results:
            text = res.get('text', '') + res.get('snippet', '')
            text_words = set(text.lower().split())
            
            overlap = len(query_words.intersection(text_words)) / len(query_words)
            reliability = res.get('reliability', 0.5)
            relevance = res.get('relevance', 1.0)
            
            score = overlap * reliability * relevance
            res['_rank_score'] = score
            ranked.append(res)
            
        ranked.sort(key=lambda x: x['_rank_score'], reverse=True)
        
        # Clean up temporary score
        for r in ranked:
            del r['_rank_score']
            
        return ranked
