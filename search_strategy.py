# search_strategy.py
import arxiv
from typing import List, Iterator, Optional
from datetime import datetime, timedelta, timezone

class ArxivSearchStrategy:
    def __init__(self):
        self.client = arxiv.Client()

    def search_by_keywords(self, keywords: str, max_results: int = 10) -> Iterator[arxiv.Result]:
        """Simple keyword search across all fields."""
        search = arxiv.Search(
            query=keywords,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        return self.client.results(search)
    
    def search_by_author(self, author_name: str, max_results: int = 10) -> Iterator[arxiv.Result]:
        """Search papers by a specific author."""
        search = arxiv.Search(
            query=f"au:{author_name}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        return self.client.results(search)
    
    def search_by_title(self, title_keywords: str, max_results: int = 10) -> Iterator[arxiv.Result]:
        """Search papers by title keywords."""
        search = arxiv.Search(
            query=f"ti:{title_keywords}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        return self.client.results(search)
    
    def search_by_category(self, category: str, max_results: int = 10) -> Iterator[arxiv.Result]:
        """Search papers in a specific category (e.g., cs.AI, math.NT)."""
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        return self.client.results(search)
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[arxiv.Result]:
        """Retrieve a specific paper by its arXiv ID."""
        search = arxiv.Search(id_list=[arxiv_id])
        try:
            return next(self.client.results(search))
        except StopIteration:
            return None
    
    #Advanced Search
    def complex_query(self, query: str, max_results: int = 10, 
                      sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance) -> Iterator[arxiv.Result]:
        """Boolean operations"""
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        return self.client.results(search)
    
    def search_recent_papers(self, keywords: str, days: int = 7, max_results: int = 50) -> Iterator[arxiv.Result]:
        """Search for papers submitted in the last N days."""
        search = arxiv.Search(
            query=keywords,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for result in self.client.results(search):
            if result.published >= cutoff_date:
                yield result
            else:
                break

    def search_recent_papers(
        self,
        keywords: str,
        days: int = 7,
        max_results: int = 50,
    ) -> Iterator[arxiv.Result]:
        """
        Search for papers submitted in the last N days.
        Uses UTC time to avoid naive/aware datetime issues.
        """
        search = arxiv.Search(
            query=keywords,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        for result in self.client.results(search):
            pub = getattr(result, "published", None)
            if pub is None:
                continue

            if pub >= cutoff_date:
                yield result
            else:
                break
    
    def search_author_in_category(self, author: str, category: str, max_results: int = 10) -> Iterator[arxiv.Result]:
        """Find papers by a specific author in a specific category."""
        search = arxiv.Search(
            query=f"au:{author} AND cat:{category}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        return self.client.results(search)
    
    #Gets results more efficiently 
    def paginated_search(self, query: str, page_size: int = 100, total_results: int = 1000):
        """
        Retrieve large result sets efficiently with pagination.
        Respects arXiv's rate limits (3 seconds between requests recommended).
        """
        import time
        
        for start in range(0, total_results, page_size):
            search = arxiv.Search(
                query=query,
                max_results=page_size,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results_page = list(self.client.results(search))
            
            if not results_page:
                break
            
            for result in results_page:
                yield result
            
            # Rate limiting - be respectful to arXiv servers
            time.sleep(3)
    
    #Filtering
    
    def filter_by_date_range(self, results: Iterator[arxiv.Result], 
                            start_date: datetime, end_date: datetime) -> List[arxiv.Result]:
        """Filter results by publication date range."""
        filtered = []
        for result in results:
            if start_date <= result.published <= end_date:
                filtered.append(result)
        return filtered
    
    def filter_by_keywords_in_abstract(self, results: Iterator[arxiv.Result], 
                                      keywords: List[str]) -> List[arxiv.Result]:
        """Post-process results to filter by keywords in abstract."""
        filtered = []
        keywords_lower = [k.lower() for k in keywords]
        
        for result in results:
            abstract_lower = result.summary.lower()
            if any(keyword in abstract_lower for keyword in keywords_lower):
                filtered.append(result)
        
        return filtered
    
    
    #Ranking - order to return results 
    def rank_by_relevance_score(self, results: Iterator[arxiv.Result], 
                                query_terms: List[str]) -> List[tuple]:
        """
        Custom relevance ranking using TF-IDF-like scoring.
        Returns list of (score, result) tuples sorted by score.
        """
        
        scored_results = []
        query_terms_lower = [term.lower() for term in query_terms]
        
        for result in results:
            # Combine title and abstract for scoring
            text = (result.title + " " + result.summary).lower()
            
            # Count query term occurrences
            score = sum(text.count(term) for term in query_terms_lower)
            
            # Weight title matches more heavily
            title_lower = result.title.lower()
            score += sum(title_lower.count(term) * 2 for term in query_terms_lower)
            
            scored_results.append((score, result))
        
        # Sort by score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return scored_results