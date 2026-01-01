"""
Athena Search Module - Quantum-coherent search across local LLMs and the open web.
"""

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class SearchSource(Enum):
    LOCAL_LLM = "local_llm"
    WEB = "web"
    CACHE = "cache"


@dataclass
class SearchConfig:
    """Configuration for search operations - groups related parameters."""
    max_results: int = 10
    use_cache: bool = True
    cache_ttl: int = 3600
    timeout: float = 30.0
    retry_count: int = 3
    privacy_mode: bool = True
    score_threshold: float = 0.5
    dedup: bool = True
    combine_strategy: str = "weighted"
    local_models: List[str] = field(default_factory=lambda: ["default"])
    web_endpoints: List[str] = field(default_factory=lambda: ["https://api.search.default/v1"])
    result_filter: Optional[Dict[str, Any]] = None


@dataclass
class SearchResult:
    content: str
    source: SearchSource
    score: float
    metadata: Dict[str, Any]


def execute_search(
    query: str,
    sources: List[str],
    config: Optional[SearchConfig] = None
) -> Dict[str, Any]:
    """
    Execute a quantum-coherent search across multiple sources.

    Args:
        query: The search query string
        sources: List of sources to search (e.g., ["local_llm", "web", "cache"])
        config: Search configuration options (uses defaults if not provided)

    Returns:
        Dictionary with 'results' list and 'metadata' about the search
    """
    config = config or SearchConfig()
    start_time = time.time()
    errors: List[Dict[str, Any]] = []

    # Check cache first
    cache_key = _generate_cache_key(query, sources, config)
    cached_response = _try_get_cached(cache_key, config, start_time)
    if cached_response:
        return cached_response

    # Query all sources and collect results
    raw_results = _query_all_sources(query, sources, config, errors)

    # Process results: filter, deduplicate, and sort
    processed_results = _process_results(raw_results, config)

    # Cache and return final results
    final_results = processed_results[:config.max_results]
    _cache_results(cache_key, final_results, config)

    return {
        "results": final_results,
        "metadata": {
            "cache_hit": False,
            "duration_ms": (time.time() - start_time) * 1000,
            "sources_queried": sources,
            "total_raw_results": len(raw_results),
            "errors": errors
        }
    }


# -----------------------------------------------------------------------------
# Cache Operations
# -----------------------------------------------------------------------------

def _generate_cache_key(query: str, sources: List[str], config: SearchConfig) -> str:
    """Generate a unique cache key for the search parameters."""
    cache_data = f"{query}:{':'.join(sorted(sources))}:{config.max_results}:{config.score_threshold}"
    return hashlib.sha256(cache_data.encode()).hexdigest()


def _try_get_cached(
    cache_key: str,
    config: SearchConfig,
    start_time: float
) -> Optional[Dict[str, Any]]:
    """Attempt to retrieve valid cached results. Returns None if cache miss."""
    if not config.use_cache:
        return None

    cached = _get_from_cache(cache_key)
    if cached is None:
        return None

    cache_time = cached.get("timestamp", 0)
    if time.time() - cache_time >= config.cache_ttl:
        return None

    results = _apply_filters(cached.get("results", []), config.result_filter)
    return {
        "results": results[:config.max_results],
        "metadata": {
            "cache_hit": True,
            "duration_ms": (time.time() - start_time) * 1000,
            "sources_queried": [],
            "errors": []
        }
    }


def _cache_results(cache_key: str, results: List[Dict], config: SearchConfig) -> None:
    """Store results in cache if caching is enabled."""
    if config.use_cache:
        _store_in_cache(cache_key, {"results": results, "timestamp": time.time()})


# -----------------------------------------------------------------------------
# Source Querying
# -----------------------------------------------------------------------------

def _query_all_sources(
    query: str,
    sources: List[str],
    config: SearchConfig,
    errors: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Query all requested sources and aggregate results."""
    results: List[Dict[str, Any]] = []

    source_handlers = {
        "local_llm": _query_local_llm_source,
        SearchSource.LOCAL_LLM.value: _query_local_llm_source,
        "web": _query_web_source,
        SearchSource.WEB.value: _query_web_source,
        "cache": _query_cache_source,
        SearchSource.CACHE.value: _query_cache_source,
    }

    for source in sources:
        handler = source_handlers.get(source)
        if handler:
            source_results = handler(query, config, errors)
            results.extend(source_results)
        else:
            errors.append({
                "source": source,
                "error": f"Unknown source: {source}",
                "type": "invalid_source"
            })

    return results


def _query_local_llm_source(
    query: str,
    config: SearchConfig,
    errors: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Query local LLM models with retry support."""
    results: List[Dict[str, Any]] = []
    search_query = _sanitize_for_privacy(query) if config.privacy_mode else query

    for model in config.local_models:
        model_results = _with_retry(
            func=lambda: _query_local_llm(search_query, model, config.timeout),
            retry_count=config.retry_count,
            on_error=lambda e: errors.append({
                "source": "local_llm",
                "model": model,
                "error": str(e),
                "type": _get_error_type(e)
            })
        )

        for r in (model_results or []):
            if r.get("score", 0) >= config.score_threshold:
                r["source"] = SearchSource.LOCAL_LLM.value
                r["model"] = model
                results.append(r)

    return results


def _query_web_source(
    query: str,
    config: SearchConfig,
    errors: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Query web endpoints with privacy checks and retry support."""
    if config.privacy_mode and not _check_privacy_allowlist(query):
        errors.append({
            "source": "web",
            "error": "Query blocked by privacy mode",
            "type": "privacy"
        })
        return []

    results: List[Dict[str, Any]] = []
    search_query = _anonymize_query(query) if config.privacy_mode else query

    for endpoint in config.web_endpoints:
        endpoint_results = _with_retry(
            func=lambda: _query_web_endpoint(search_query, endpoint, config.timeout),
            retry_count=config.retry_count,
            on_error=lambda e: errors.append({
                "source": "web",
                "endpoint": endpoint,
                "error": str(e),
                "type": _get_error_type(e)
            })
        )

        for r in (endpoint_results or []):
            if r.get("score", 0) >= config.score_threshold:
                r["source"] = SearchSource.WEB.value
                r["endpoint"] = endpoint
                results.append(r)

    return results


def _query_cache_source(
    query: str,
    config: SearchConfig,
    errors: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Search the local cache for matching results."""
    try:
        cache_results = _search_cache(query, config.max_results * 2)
        return [
            {**r, "source": SearchSource.CACHE.value}
            for r in cache_results
            if r.get("score", 0) >= config.score_threshold
        ]
    except Exception as e:
        errors.append({"source": "cache", "error": str(e), "type": "cache_error"})
        return []


# -----------------------------------------------------------------------------
# Result Processing
# -----------------------------------------------------------------------------

def _process_results(results: List[Dict], config: SearchConfig) -> List[Dict]:
    """Apply filters, deduplication, and sorting to results."""
    processed = _apply_filters(results, config.result_filter)

    if config.dedup:
        processed = _deduplicate(processed)

    return _sort_results(processed, config.combine_strategy)


def _apply_filters(
    results: List[Dict[str, Any]],
    result_filter: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Filter results based on metadata criteria."""
    if not result_filter:
        return results

    def matches_filter(result: Dict[str, Any]) -> bool:
        metadata = result.get("metadata", {})
        for key, value in result_filter.items():
            if key not in metadata:
                continue
            actual = metadata[key]
            expected_values = value if isinstance(value, list) else [value]
            if actual not in expected_values:
                return False
        return True

    return [r for r in results if matches_filter(r)]


def _deduplicate(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate results based on content hash."""
    seen: set = set()
    unique: List[Dict[str, Any]] = []

    for result in results:
        content_hash = hashlib.md5(result.get("content", "").encode()).hexdigest()
        if content_hash not in seen:
            seen.add(content_hash)
            unique.append(result)

    return unique


def _sort_results(results: List[Dict[str, Any]], strategy: str) -> List[Dict[str, Any]]:
    """Sort results according to the specified strategy."""
    if strategy == "weighted":
        source_weights = {
            SearchSource.LOCAL_LLM.value: 1.2,
            SearchSource.WEB.value: 1.0,
            SearchSource.CACHE.value: 0.8
        }
        for r in results:
            weight = source_weights.get(r.get("source"), 1.0)
            r["weighted_score"] = r.get("score", 0) * weight
        return sorted(results, key=lambda x: x.get("weighted_score", 0), reverse=True)

    if strategy == "recency":
        return sorted(
            results,
            key=lambda x: x.get("metadata", {}).get("timestamp", 0),
            reverse=True
        )

    # Default: sort by score
    return sorted(results, key=lambda x: x.get("score", 0), reverse=True)


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def _with_retry(
    func: Callable,
    retry_count: int,
    on_error: Callable[[Exception], None]
) -> Optional[List[Dict[str, Any]]]:
    """Execute a function with retry logic. Returns None on complete failure."""
    for attempt in range(retry_count):
        try:
            return func()
        except Exception as e:
            if attempt == retry_count - 1:
                on_error(e)
    return None


def _get_error_type(error: Exception) -> str:
    """Determine error type from exception."""
    if isinstance(error, TimeoutError):
        return "timeout"
    if isinstance(error, ConnectionError):
        return "connection"
    return "unknown"


# -----------------------------------------------------------------------------
# External Dependencies (stubs)
# -----------------------------------------------------------------------------

_cache_store: Dict[str, Any] = {}


def _get_from_cache(key: str) -> Optional[Dict[str, Any]]:
    return _cache_store.get(key)


def _store_in_cache(key: str, data: Dict[str, Any]) -> None:
    _cache_store[key] = data


def _search_cache(query: str, limit: int) -> List[Dict[str, Any]]:
    return []


def _sanitize_for_privacy(query: str) -> str:
    return query


def _anonymize_query(query: str) -> str:
    return query


def _check_privacy_allowlist(query: str) -> bool:
    return True


def _query_local_llm(query: str, model: str, timeout: float) -> List[Dict[str, Any]]:
    return []


def _query_web_endpoint(query: str, endpoint: str, timeout: float) -> List[Dict[str, Any]]:
    return []
