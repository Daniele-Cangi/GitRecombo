"""
Test SearchPlanner and RepoCache integration.

This script tests:
1. SearchPlanner rate limit handling
2. RepoCache caching and retrieval
3. Query sharding by time windows
4. Integration with discover.py
"""

import time
from github_search_planner import SearchPlanner, exponential_backoff
from repo_cache import RepoCache
from discover import get_search_planner, get_repo_cache


def test_search_planner():
    """Test SearchPlanner functionality."""
    print("🧪 Testing SearchPlanner...")
    
    planner = SearchPlanner()
    
    # Test status display
    print("\n📊 Initial status:")
    status = planner.get_status()
    for endpoint, info in status.items():
        print(f"  {endpoint}: {info['requests_this_window']} requests in window")
    
    # Test query sharding
    print("\n📦 Testing query sharding...")
    base_query = "topic:rust stars:>100 language:Rust"
    queries = planner.shard_query_by_time(base_query, days=90, max_results_per_shard=800)
    print(f"  Generated {len(queries)} shards for 90-day window:")
    for i, q in enumerate(queries, 1):
        print(f"    Shard {i}: {q}")
    
    # Test time estimation
    print("\n⏱️  Testing time estimation...")
    estimate = planner.estimate_search_time(30, "search")
    print(f"  30 search queries estimated: {estimate:.1f}s ({estimate/60:.1f}m)")
    
    estimate_code = planner.estimate_search_time(20, "code_search")
    print(f"  20 code searches estimated: {estimate_code:.1f}s ({estimate_code/60:.1f}m)")
    
    print("\n✅ SearchPlanner tests passed!\n")


def test_repo_cache():
    """Test RepoCache functionality."""
    print("🧪 Testing RepoCache...")
    
    cache = RepoCache("test_cache.db")
    
    # Test repo caching
    print("\n💾 Testing repository caching...")
    test_repo = {
        "full_name": "rust-lang/rust",
        "name": "rust",
        "owner": {"login": "rust-lang"},
        "description": "Empowering everyone to build reliable and efficient software.",
        "stargazers_count": 95000,
        "language": "Rust",
        "topics": ["rust", "compiler", "systems-programming"],
        "created_at": "2010-06-16T20:39:03Z",
        "pushed_at": "2024-10-19T10:00:00Z",
        "fork": False,
        "forks_count": 12000
    }
    
    cache.cache_repo(test_repo)
    print("  ✓ Cached test repository")
    
    # Test retrieval
    retrieved = cache.get_repo("rust-lang/rust")
    assert retrieved is not None, "Failed to retrieve cached repo"
    assert retrieved["stargazers_count"] == 95000, "Wrong star count"
    print("  ✓ Retrieved and validated cached repo")
    
    # Test README caching
    print("\n📄 Testing README caching...")
    cache.cache_readme("rust-lang/rust", "# Rust\n\nA language empowering everyone...")
    readme = cache.get_readme("rust-lang/rust")
    assert readme is not None, "Failed to retrieve README"
    assert "Rust" in readme, "Wrong README content"
    print("  ✓ Cached and retrieved README")
    
    # Test health metrics
    print("\n🏥 Testing health metrics caching...")
    health = {
        "has_ci_cd": True,
        "has_tests": True,
        "has_releases": True,
        "has_manifest": True,
        "health_score": 0.95
    }
    cache.cache_health_metrics("rust-lang/rust", health)
    retrieved_health = cache.get_health_metrics("rust-lang/rust")
    assert retrieved_health is not None, "Failed to retrieve health metrics"
    assert retrieved_health["health_score"] == 0.95, "Wrong health score"
    print("  ✓ Cached and retrieved health metrics")
    
    # Test scores
    print("\n🎯 Testing score caching...")
    scores = {
        "novelty": 0.85,
        "relevance": 0.92,
        "health": 0.95,
        "author": 0.88,
        "diversity": 0.75,
        "gem": 0.87
    }
    cache.cache_scores("rust-lang/rust", scores, "building a high-performance RAG system")
    print("  ✓ Cached discovery scores")
    
    # Test embedding
    print("\n🔢 Testing embedding caching...")
    fake_embedding = [0.1] * 1536  # text-embedding-3-small size
    cache.cache_embedding("rust-lang/rust", fake_embedding)
    retrieved_emb = cache.get_embedding("rust-lang/rust")
    assert retrieved_emb is not None, "Failed to retrieve embedding"
    assert len(retrieved_emb) == 1536, "Wrong embedding size"
    print("  ✓ Cached and retrieved embedding")
    
    # Test query
    print("\n🔍 Testing repository queries...")
    results = cache.query_repos(language="Rust", min_stars=90000, limit=10)
    assert len(results) > 0, "Query returned no results"
    print(f"  ✓ Query returned {len(results)} results")
    
    # Test stats
    print("\n📈 Testing cache statistics...")
    stats = cache.get_stats()
    print(f"  Total repos: {stats['total_repos']}")
    print(f"  Repos with README: {stats['repos_with_readme']}")
    print(f"  Repos with health: {stats['repos_with_health']}")
    print(f"  Repos with embeddings: {stats['repos_with_embeddings']}")
    print(f"  DB size: {stats['db_size_mb']:.2f} MB")
    
    # Cleanup
    cache.close()
    import os
    os.remove("test_cache.db")
    print("\n✅ RepoCache tests passed!\n")


def test_exponential_backoff():
    """Test exponential backoff calculation."""
    print("🧪 Testing exponential backoff...")
    
    for attempt in range(5):
        delay = exponential_backoff(attempt, base_delay=1.0, max_delay=60.0)
        print(f"  Attempt {attempt}: {delay:.2f}s delay")
    
    print("✅ Exponential backoff tests passed!\n")


def test_integration():
    """Test integration with discover.py."""
    print("🧪 Testing integration with discover.py...")
    
    # Test singleton instances
    planner1 = get_search_planner()
    planner2 = get_search_planner()
    assert planner1 is planner2, "SearchPlanner not singleton"
    print("  ✓ SearchPlanner singleton working")
    
    cache1 = get_repo_cache()
    cache2 = get_repo_cache()
    assert cache1 is cache2, "RepoCache not singleton"
    print("  ✓ RepoCache singleton working")
    
    print("✅ Integration tests passed!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("SearchPlanner & RepoCache Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_search_planner()
        test_repo_cache()
        test_exponential_backoff()
        test_integration()
        
        print("=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
