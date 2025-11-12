"""
Repository Cache - Persistent SQLite cache for discovered repositories.

Stores:
- Repository metadata (name, stars, created_at, etc.)
- README content
- Health metrics (CI/CD, tests, releases)
- Discovery scores (novelty, relevance, health, GEM)
- Embeddings for similarity calculations

Features:
- TTL-based expiration (default 24h for metadata, 7d for READMEs)
- Incremental updates (update only changed repos)
- Query interface for cached repos
- Cache statistics and cleanup
"""

import sqlite3
import json
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib


class RepoCache:
    """SQLite-based cache for discovered repositories."""
    
    def __init__(self, db_path: str = "repo_cache.db"):
        """Initialize cache with SQLite database."""
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        cursor = self.conn.cursor()
        
        # Main repositories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                repo_full_name TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner TEXT NOT NULL,
                description TEXT,
                stars INTEGER,
                language TEXT,
                topics TEXT,  -- JSON array
                created_at TEXT,
                pushed_at TEXT,
                
                -- Metadata
                cached_at REAL NOT NULL,
                ttl_hours INTEGER DEFAULT 24,
                
                -- Raw data
                raw_data TEXT  -- Full JSON from GitHub API
            )
        """)
        
        # README content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readmes (
                repo_full_name TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                cached_at REAL NOT NULL,
                ttl_hours INTEGER DEFAULT 168,  -- 7 days
                
                FOREIGN KEY (repo_full_name) REFERENCES repositories(repo_full_name)
            )
        """)
        
        # Health metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_metrics (
                repo_full_name TEXT PRIMARY KEY,
                has_ci_cd BOOLEAN,
                has_tests BOOLEAN,
                has_releases BOOLEAN,
                has_manifest BOOLEAN,
                health_score REAL,
                
                cached_at REAL NOT NULL,
                ttl_hours INTEGER DEFAULT 24,
                
                FOREIGN KEY (repo_full_name) REFERENCES repositories(repo_full_name)
            )
        """)
        
        # Discovery scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovery_scores (
                repo_full_name TEXT PRIMARY KEY,
                novelty_score REAL,
                relevance_score REAL,
                health_score REAL,
                author_score REAL,
                diversity_score REAL,
                gem_score REAL,
                
                -- Context for score calculation
                goal_hash TEXT,  -- Hash of goal used for relevance
                discovered_at REAL NOT NULL,
                
                FOREIGN KEY (repo_full_name) REFERENCES repositories(repo_full_name)
            )
        """)
        
        # Embeddings table (for diversity calculations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                repo_full_name TEXT PRIMARY KEY,
                embedding_model TEXT NOT NULL,
                embedding BLOB NOT NULL,  -- Serialized numpy array or JSON
                cached_at REAL NOT NULL,
                ttl_hours INTEGER DEFAULT 168,  -- 7 days
                
                FOREIGN KEY (repo_full_name) REFERENCES repositories(repo_full_name)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_cached_at ON repositories(cached_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_stars ON repositories(stars)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_language ON repositories(language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_gem ON discovery_scores(gem_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_goal ON discovery_scores(goal_hash)")
        
        self.conn.commit()

        # Processed repositories (keep track of repos that have been used in a run)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_repos (
                repo_full_name TEXT PRIMARY KEY,
                processed_at REAL NOT NULL,
                info TEXT,  -- optional JSON with run_id or metadata
                FOREIGN KEY (repo_full_name) REFERENCES repositories(repo_full_name)
            )
        """)
        self.conn.commit()
    
    def cache_repo(self, repo: Dict, ttl_hours: int = 24):
        """Cache a repository's metadata."""
        cursor = self.conn.cursor()
        
        full_name = repo['full_name']
        
        cursor.execute("""
            INSERT OR REPLACE INTO repositories
            (repo_full_name, name, owner, description, stars, language, topics,
             created_at, pushed_at, cached_at, ttl_hours, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name,
            repo.get('name', ''),
            repo.get('owner', {}).get('login', ''),
            repo.get('description', ''),
            repo.get('stargazers_count', 0),
            repo.get('language', ''),
            json.dumps(repo.get('topics', [])),
            repo.get('created_at', ''),
            repo.get('pushed_at', ''),
            time.time(),
            ttl_hours,
            json.dumps(repo)
        ))
        
        self.conn.commit()
    
    def cache_readme(self, repo_full_name: str, content: str, ttl_hours: int = 168):
        """Cache README content."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO readmes
            (repo_full_name, content, cached_at, ttl_hours)
            VALUES (?, ?, ?, ?)
        """, (repo_full_name, content, time.time(), ttl_hours))
        
        self.conn.commit()
    
    def cache_health_metrics(self, repo_full_name: str, metrics: Dict, ttl_hours: int = 24):
        """Cache health metrics."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO health_metrics
            (repo_full_name, has_ci_cd, has_tests, has_releases, has_manifest,
             health_score, cached_at, ttl_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            repo_full_name,
            metrics.get('has_ci_cd', False),
            metrics.get('has_tests', False),
            metrics.get('has_releases', False),
            metrics.get('has_manifest', False),
            metrics.get('health_score', 0.0),
            time.time(),
            ttl_hours
        ))
        
        self.conn.commit()
    
    def cache_scores(self, repo_full_name: str, scores: Dict, goal: str):
        """Cache discovery scores."""
        cursor = self.conn.cursor()
        
        goal_hash = hashlib.md5(goal.encode()).hexdigest()
        
        cursor.execute("""
            INSERT OR REPLACE INTO discovery_scores
            (repo_full_name, novelty_score, relevance_score, health_score,
             author_score, diversity_score, gem_score, goal_hash, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            repo_full_name,
            scores.get('novelty', 0.0),
            scores.get('relevance', 0.0),
            scores.get('health', 0.0),
            scores.get('author', 0.0),
            scores.get('diversity', 0.0),
            scores.get('gem', 0.0),
            goal_hash,
            time.time()
        ))
        
        self.conn.commit()
    
    def cache_embedding(self, repo_full_name: str, embedding: List[float], 
                       model: str = "thenlper/gte-small", ttl_hours: int = 168):
        """Cache embedding vector."""
        cursor = self.conn.cursor()
        
        # Serialize embedding as JSON (simpler than numpy for now)
        embedding_json = json.dumps(embedding)
        
        cursor.execute("""
            INSERT OR REPLACE INTO embeddings
            (repo_full_name, embedding_model, embedding, cached_at, ttl_hours)
            VALUES (?, ?, ?, ?, ?)
        """, (repo_full_name, model, embedding_json, time.time(), ttl_hours))
        
        self.conn.commit()
    
    def get_repo(self, repo_full_name: str, check_ttl: bool = True) -> Optional[Dict]:
        """Retrieve cached repository metadata."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM repositories WHERE repo_full_name = ?
        """, (repo_full_name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check TTL
        if check_ttl:
            cached_at = row['cached_at']
            ttl_hours = row['ttl_hours']
            if time.time() - cached_at > ttl_hours * 3600:
                return None  # Expired
        
        # Return as dict
        return json.loads(row['raw_data'])
    
    def get_readme(self, repo_full_name: str, check_ttl: bool = True) -> Optional[str]:
        """Retrieve cached README content."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT content, cached_at, ttl_hours FROM readmes
            WHERE repo_full_name = ?
        """, (repo_full_name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check TTL
        if check_ttl:
            cached_at = row['cached_at']
            ttl_hours = row['ttl_hours']
            if time.time() - cached_at > ttl_hours * 3600:
                return None  # Expired
        
        return row['content']
    
    def get_health_metrics(self, repo_full_name: str, check_ttl: bool = True) -> Optional[Dict]:
        """Retrieve cached health metrics."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM health_metrics WHERE repo_full_name = ?
        """, (repo_full_name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check TTL
        if check_ttl:
            cached_at = row['cached_at']
            ttl_hours = row['ttl_hours']
            if time.time() - cached_at > ttl_hours * 3600:
                return None  # Expired
        
        return {
            'has_ci_cd': bool(row['has_ci_cd']),
            'has_tests': bool(row['has_tests']),
            'has_releases': bool(row['has_releases']),
            'has_manifest': bool(row['has_manifest']),
            'health_score': row['health_score']
        }
    
    def get_embedding(self, repo_full_name: str, check_ttl: bool = True) -> Optional[List[float]]:
        """Retrieve cached embedding."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT embedding, cached_at, ttl_hours FROM embeddings
            WHERE repo_full_name = ?
        """, (repo_full_name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check TTL
        if check_ttl:
            cached_at = row['cached_at']
            ttl_hours = row['ttl_hours']
            if time.time() - cached_at > ttl_hours * 3600:
                return None  # Expired
        
        return json.loads(row['embedding'])

    # ---- Processed repos helpers ----
    def mark_processed(self, repo_full_name: str, info: Optional[Dict] = None):
        """Mark a repository as processed by a run."""
        cursor = self.conn.cursor()
        info_json = json.dumps(info) if info is not None else None
        cursor.execute("""
            INSERT OR REPLACE INTO processed_repos
            (repo_full_name, processed_at, info)
            VALUES (?, ?, ?)
        """, (repo_full_name, time.time(), info_json))
        self.conn.commit()

    def is_processed(self, repo_full_name: str) -> bool:
        """Return True if the repo was previously marked processed."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT processed_at FROM processed_repos WHERE repo_full_name = ?", (repo_full_name,))
        row = cursor.fetchone()
        return bool(row)

    def get_processed(self, limit: int = 100) -> List[str]:
        """Return list of processed repo_full_name values (most recent first)."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT repo_full_name FROM processed_repos ORDER BY processed_at DESC LIMIT ?", (limit,))
        return [r[0] for r in cursor.fetchall()]

    def purge_processed_older_than(self, days: int = 90) -> int:
        """Purge processed markers older than `days`. Returns number deleted."""
        cutoff = time.time() - days * 24 * 3600
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM processed_repos WHERE processed_at < ?", (cutoff,))
        deleted = cursor.rowcount
        self.conn.commit()
        return deleted
    
    def query_repos(self, language: Optional[str] = None, 
                   min_stars: int = 0,
                   min_gem_score: float = 0.0,
                   goal: Optional[str] = None,
                   limit: int = 100) -> List[Dict]:
        """Query cached repositories with filters."""
        cursor = self.conn.cursor()
        
        query = """
            SELECT r.*, s.gem_score
            FROM repositories r
            LEFT JOIN discovery_scores s ON r.repo_full_name = s.repo_full_name
            WHERE 1=1
        """
        params = []
        
        if language:
            query += " AND r.language = ?"
            params.append(language)
        
        if min_stars > 0:
            query += " AND r.stars >= ?"
            params.append(min_stars)
        
        if min_gem_score > 0.0:
            query += " AND s.gem_score >= ?"
            params.append(min_gem_score)
        
        if goal:
            goal_hash = hashlib.md5(goal.encode()).hexdigest()
            query += " AND s.goal_hash = ?"
            params.append(goal_hash)
        
        query += " ORDER BY s.gem_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            repo = json.loads(row['raw_data'])
            repo['cached_gem_score'] = row['gem_score']
            results.append(repo)
        
        return results
    
    def cleanup_expired(self) -> Tuple[int, int, int, int]:
        """Remove expired entries from all tables."""
        cursor = self.conn.cursor()
        now = time.time()
        
        # Cleanup repositories
        cursor.execute("""
            DELETE FROM repositories
            WHERE ? - cached_at > ttl_hours * 3600
        """, (now,))
        repos_deleted = cursor.rowcount
        
        # Cleanup readmes
        cursor.execute("""
            DELETE FROM readmes
            WHERE ? - cached_at > ttl_hours * 3600
        """, (now,))
        readmes_deleted = cursor.rowcount
        
        # Cleanup health metrics
        cursor.execute("""
            DELETE FROM health_metrics
            WHERE ? - cached_at > ttl_hours * 3600
        """, (now,))
        health_deleted = cursor.rowcount
        
        # Cleanup embeddings
        cursor.execute("""
            DELETE FROM embeddings
            WHERE ? - cached_at > ttl_hours * 3600
        """, (now,))
        embeddings_deleted = cursor.rowcount
        
        self.conn.commit()
        
        return repos_deleted, readmes_deleted, health_deleted, embeddings_deleted
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total repos
        cursor.execute("SELECT COUNT(*) FROM repositories")
        stats['total_repos'] = cursor.fetchone()[0]
        
        # Repos with README
        cursor.execute("SELECT COUNT(*) FROM readmes")
        stats['repos_with_readme'] = cursor.fetchone()[0]
        
        # Repos with health metrics
        cursor.execute("SELECT COUNT(*) FROM health_metrics")
        stats['repos_with_health'] = cursor.fetchone()[0]
        
        # Repos with embeddings
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        stats['repos_with_embeddings'] = cursor.fetchone()[0]
        
        # Cache size
        db_size = Path(self.db_path).stat().st_size
        stats['db_size_mb'] = db_size / (1024 * 1024)
        
        # Most common languages
        cursor.execute("""
            SELECT language, COUNT(*) as count
            FROM repositories
            WHERE language IS NOT NULL AND language != ''
            GROUP BY language
            ORDER BY count DESC
            LIMIT 5
        """)
        stats['top_languages'] = [
            {'language': row[0], 'count': row[1]}
            for row in cursor.fetchall()
        ]
        
        return stats
    
    def get_repo_count(self):
        """Get total number of cached repositories."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM repositories")
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            return 0

    def clear_all(self):
        """Clear all cached data from database."""
        try:
            cursor = self.conn.cursor()
            # Delete from all tables in reverse dependency order
            cursor.execute("DELETE FROM discovery_scores")
            cursor.execute("DELETE FROM health_metrics")
            cursor.execute("DELETE FROM readmes")
            cursor.execute("DELETE FROM repositories")
            cursor.execute("DELETE FROM processed_repos")
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
