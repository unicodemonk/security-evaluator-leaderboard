"""
Knowledge Base - Shared memory for agent coordination.

Implements shared knowledge base where agents communicate indirectly
through reading and writing knowledge entries.
"""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from collections import defaultdict
import threading

from .base import KnowledgeBase as KnowledgeBaseInterface, KnowledgeEntry


class InMemoryKnowledgeBase(KnowledgeBaseInterface):
    """
    In-memory implementation of knowledge base.

    Thread-safe implementation for concurrent agent access.
    """

    def __init__(self):
        """Initialize knowledge base."""
        self.entries: List[KnowledgeEntry] = []
        self.entries_by_type: Dict[str, List[KnowledgeEntry]] = defaultdict(list)
        self.entries_by_tag: Dict[str, List[KnowledgeEntry]] = defaultdict(list)
        self.entries_by_source: Dict[str, List[KnowledgeEntry]] = defaultdict(list)

        # Thread safety
        self.lock = threading.RLock()

    def add_entry(self, entry: KnowledgeEntry):
        """
        Add knowledge entry.

        Args:
            entry: Knowledge entry to add
        """
        with self.lock:
            self.entries.append(entry)
            self.entries_by_type[entry.entry_type].append(entry)
            self.entries_by_source[entry.source_agent].append(entry)

            for tag in entry.tags:
                self.entries_by_tag[tag].append(entry)

    def query(
        self,
        entry_type: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        source_agent: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[KnowledgeEntry]:
        """
        Query knowledge base.

        Args:
            entry_type: Filter by entry type
            tags: Filter by tags (returns entries with ANY matching tag)
            source_agent: Filter by source agent
            since: Filter by timestamp (entries after this time)

        Returns:
            List of matching entries
        """
        with self.lock:
            # Start with all entries or filtered by type
            if entry_type:
                candidates = self.entries_by_type.get(entry_type, [])
            else:
                candidates = self.entries

            # Apply filters
            results = []
            for entry in candidates:
                # Filter by tags
                if tags and not any(tag in entry.tags for tag in tags):
                    continue

                # Filter by source agent
                if source_agent and entry.source_agent != source_agent:
                    continue

                # Filter by timestamp
                if since and entry.timestamp < since:
                    continue

                results.append(entry)

            # Sort by timestamp (most recent first)
            results.sort(key=lambda e: e.timestamp, reverse=True)

            return results

    def get_latest(self, entry_type: str, n: int = 10) -> List[KnowledgeEntry]:
        """
        Get latest N entries of a type.

        Args:
            entry_type: Entry type to query
            n: Number of entries to return

        Returns:
            Latest N entries, sorted by timestamp descending
        """
        with self.lock:
            entries = self.entries_by_type.get(entry_type, [])
            # Sort by timestamp descending
            sorted_entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)
            return sorted_entries[:n]

    def clear(self):
        """Clear all knowledge (for testing or reset)."""
        with self.lock:
            self.entries.clear()
            self.entries_by_type.clear()
            self.entries_by_tag.clear()
            self.entries_by_source.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.

        Returns:
            Dictionary with stats
        """
        with self.lock:
            return {
                'total_entries': len(self.entries),
                'entries_by_type': {k: len(v) for k, v in self.entries_by_type.items()},
                'entries_by_tag': {k: len(v) for k, v in self.entries_by_tag.items()},
                'num_sources': len(self.entries_by_source),
                'oldest_entry': min((e.timestamp for e in self.entries), default=None),
                'newest_entry': max((e.timestamp for e in self.entries), default=None)
            }

    def get_entries_by_type(self, entry_type: str) -> List[KnowledgeEntry]:
        """
        Get all entries of a specific type.

        Args:
            entry_type: Entry type

        Returns:
            List of entries
        """
        with self.lock:
            return self.entries_by_type.get(entry_type, []).copy()

    def get_entries_by_tag(self, tag: str) -> List[KnowledgeEntry]:
        """
        Get all entries with a specific tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of entries
        """
        with self.lock:
            return self.entries_by_tag.get(tag, []).copy()


class PersistentKnowledgeBase(KnowledgeBaseInterface):
    """
    Persistent knowledge base with file/database backing.

    TODO: Implement when needed for large-scale evaluations.
    """

    def __init__(self, storage_path: str):
        """
        Initialize persistent knowledge base.

        Args:
            storage_path: Path to storage location
        """
        self.storage_path = storage_path
        self.in_memory = InMemoryKnowledgeBase()
        raise NotImplementedError("PersistentKnowledgeBase not yet implemented")

    def add_entry(self, entry: KnowledgeEntry):
        # Add to in-memory cache
        self.in_memory.add_entry(entry)
        # TODO: Persist to storage
        pass

    def query(
        self,
        entry_type: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        source_agent: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[KnowledgeEntry]:
        # TODO: Query from storage
        return self.in_memory.query(entry_type, tags, source_agent, since)

    def get_latest(self, entry_type: str, n: int = 10) -> List[KnowledgeEntry]:
        # TODO: Query from storage
        return self.in_memory.get_latest(entry_type, n)

    def clear(self):
        self.in_memory.clear()
        # TODO: Clear storage
        pass
