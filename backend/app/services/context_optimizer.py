"""Context Optimizer

Optimizes context to fit within LLM token budgets while
maximizing relevance and completeness.

This is critical for cost management and ensuring the most
important context is included in every query.
"""
from typing import List, Dict, Optional
import tiktoken
import logging

logger = logging.getLogger(__name__)


class ContextOptimizer:
    """
    Optimize context to fit within token budget
    
    Uses priority-based greedy selection to include the most
    relevant context while staying within token limits.
    """
    
    # Priority scores for different context types
    PRIORITY_SCORES = {
        "schema": 100,      # Always include schema
        "metric": 90,       # Business metrics are critical
        "rule": 70,         # Business rules are important
        "example": 40,      # Examples are helpful but optional
        "glossary": 20,     # Glossary is nice-to-have
        "permissions": 100, # Always include permissions
    }
    
    def __init__(self, max_tokens: int = 8000, model: str = "gpt-4"):
        """
        Initialize optimizer
        
        Args:
            max_tokens: Maximum tokens for context
            model: Model name for tokenizer (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.max_tokens = max_tokens
        self.model = model
        
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
            logger.info(f"Tokenizer loaded for {model}")
        except KeyError:
            # Fallback to cl100k_base (GPT-4 encoding)
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4
    
    def optimize(
        self,
        context_items: List[Dict],
        query_tokens: int,
        reserved_for_response: int = 1000
    ) -> str:
        """
        Select and fit context items within token budget
        
        Args:
            context_items: List of context items with type, content, relevance
            query_tokens: Number of tokens in the query
            reserved_for_response: Tokens to reserve for LLM response
            
        Returns:
            Assembled context string that fits within budget
        """
        available_tokens = self.max_tokens - query_tokens - reserved_for_response
        
        if available_tokens <= 0:
            logger.warning(
                f"No tokens available for context! "
                f"Query: {query_tokens}, Reserved: {reserved_for_response}"
            )
            return ""
        
        logger.info(
            f"Optimizing context: {available_tokens} tokens available, "
            f"{len(context_items)} items to consider"
        )
        
        # Calculate priority score for each item
        scored_items = []
        for item in context_items:
            content = self._format_item(item)
            tokens = self.count_tokens(content)
            
            # Base priority from type
            base_priority = self.PRIORITY_SCORES.get(item.get("type", "other"), 10)
            
            # Boost by relevance score
            relevance = item.get("relevance", 0.5)
            score = base_priority * relevance
            
            # Penalize by size (prefer smaller items for same priority)
            size_penalty = tokens / 1000  # Small penalty
            final_score = score - size_penalty
            
            scored_items.append({
                "content": content,
                "tokens": tokens,
                "score": final_score,
                "type": item.get("type", "other"),
                "original": item
            })
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        
        # Greedy selection within budget
        selected = []
        used_tokens = 0
        
        for item in scored_items:
            if used_tokens + item["tokens"] <= available_tokens:
                selected.append(item)
                used_tokens += item["tokens"]
                logger.debug(
                    f"Selected {item['type']}: {item['tokens']} tokens "
                    f"(score: {item['score']:.2f})"
                )
            else:
                # Try to fit summary if available
                summary = item["original"].get("summary")
                if summary:
                    summary_content = self._format_summary(item["original"])
                    summary_tokens = self.count_tokens(summary_content)
                    
                    if used_tokens + summary_tokens <= available_tokens:
                        selected.append({
                            **item,
                            "content": summary_content,
                            "tokens": summary_tokens
                        })
                        used_tokens += summary_tokens
                        logger.debug(
                            f"Selected {item['type']} (summary): "
                            f"{summary_tokens} tokens"
                        )
        
        # Assemble final context
        context = self._assemble_context(selected)
        final_tokens = self.count_tokens(context)
        
        logger.info(
            f"Context optimized: {len(selected)}/{len(context_items)} items, "
            f"{final_tokens}/{available_tokens} tokens used "
            f"({final_tokens/available_tokens*100:.1f}%)"
        )
        
        return context
    
    def _format_item(self, item: Dict) -> str:
        """
        Format context item as string
        
        Args:
            item: Context item dict
            
        Returns:
            Formatted string
        """
        item_type = item.get("type", "other")
        
        if item_type == "schema":
            return self._format_schema(item)
        elif item_type == "metric":
            return self._format_metric(item)
        elif item_type == "rule":
            return self._format_rule(item)
        elif item_type == "example":
            return self._format_example(item)
        elif item_type == "glossary":
            return self._format_glossary(item)
        else:
            return str(item.get("content", ""))
    
    def _format_schema(self, item: Dict) -> str:
        """Format schema item"""
        table = item.get("table", "unknown")
        columns = item.get("columns", [])
        
        lines = [f"Table: {table}"]
        if columns:
            lines.append("Columns:")
            for col in columns[:20]:  # Limit columns
                col_type = col.get("type", "")
                nullable = " NULL" if col.get("nullable") else " NOT NULL"
                lines.append(f"  - {col['name']} ({col_type}){nullable}")
        
        return "\n".join(lines)
    
    def _format_metric(self, item: Dict) -> str:
        """Format metric item"""
        lines = [
            f"Metric: {item.get('display_name', item.get('name', 'unknown'))}",
            f"Definition: {item.get('description', '')}",
            f"SQL: {item.get('sql_definition', '')}",
        ]
        
        if item.get("certified"):
            lines.append("Status: ✓ Certified")
        
        if item.get("filters"):
            lines.append(f"Filters: {item['filters']}")
        
        return "\n".join(lines)
    
    def _format_rule(self, item: Dict) -> str:
        """Format business rule"""
        lines = [
            f"Rule: {item.get('name', 'unknown')}",
            f"Type: {item.get('rule_type', '')}",
            f"Definition: {item.get('definition', '')}"
        ]
        return "\n".join(lines)
    
    def _format_example(self, item: Dict) -> str:
        """Format example query"""
        lines = [
            f"Example Question: {item.get('question', '')}",
            f"SQL: {item.get('sql', '')}",
        ]
        if item.get("explanation"):
            lines.append(f"Explanation: {item['explanation']}")
        return "\n".join(lines)
    
    def _format_glossary(self, item: Dict) -> str:
        """Format glossary term"""
        return f"{item.get('term', '')}: {item.get('definition', '')}"
    
    def _format_summary(self, item: Dict) -> str:
        """Format item summary (shorter version)"""
        item_type = item.get("type", "other")
        
        if item_type == "metric":
            return f"Metric: {item.get('name')} = {item.get('sql_definition', '')}"
        elif item_type == "example":
            return f"Example: {item.get('question')} → {item.get('sql', '')[:50]}..."
        else:
            return str(item.get("summary", item.get("content", "")))[:100]
    
    def _assemble_context(self, items: List[Dict]) -> str:
        """
        Assemble selected items into coherent context
        
        Args:
            items: Selected context items
            
        Returns:
            Assembled context string
        """
        sections = []
        
        # Group by type
        by_type = {}
        for item in items:
            item_type = item["type"]
            by_type.setdefault(item_type, []).append(item)
        
        # Build sections in priority order
        if "permissions" in by_type:
            sections.append("## User Permissions")
            sections.extend([i["content"] for i in by_type["permissions"]])
        
        if "schema" in by_type:
            sections.append("\n## Database Schema")
            sections.extend([i["content"] for i in by_type["schema"]])
        
        if "metric" in by_type:
            sections.append("\n## Business Metrics")
            sections.extend([i["content"] for i in by_type["metric"]])
        
        if "rule" in by_type:
            sections.append("\n## Business Rules")
            sections.extend([i["content"] for i in by_type["rule"]])
        
        if "example" in by_type:
            sections.append("\n## Example Queries")
            sections.extend([i["content"] for i in by_type["example"]])
        
        if "glossary" in by_type:
            sections.append("\n## Business Glossary")
            sections.extend([i["content"] for i in by_type["glossary"]])
        
        return "\n\n".join(sections)
    
    def estimate_cost(
        self,
        context_tokens: int,
        query_tokens: int,
        response_tokens: int
    ) -> Dict[str, float]:
        """
        Estimate API cost for a query
        
        Args:
            context_tokens: Tokens in context
            query_tokens: Tokens in query
            response_tokens: Expected tokens in response
            
        Returns:
            Dict with cost estimates for different models
        """
        total_tokens = context_tokens + query_tokens + response_tokens
        
        # Pricing per 1K tokens (as of 2024)
        pricing = {
            "gpt-4-turbo": {
                "input": 0.01,  # $0.01 per 1K input tokens
                "output": 0.03  # $0.03 per 1K output tokens
            },
            "gpt-4": {
                "input": 0.03,
                "output": 0.06
            },
            "gpt-3.5-turbo": {
                "input": 0.0005,
                "output": 0.0015
            }
        }
        
        costs = {}
        for model, prices in pricing.items():
            input_cost = (context_tokens + query_tokens) / 1000 * prices["input"]
            output_cost = response_tokens / 1000 * prices["output"]
            costs[model] = {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": input_cost + output_cost,
                "total_tokens": total_tokens
            }
        
        return costs


def get_context_optimizer(max_tokens: int = 8000) -> ContextOptimizer:
    """Factory function to create ContextOptimizer"""
    return ContextOptimizer(max_tokens=max_tokens)


