"""Moss-based skill routing engine for active skill discovery."""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING

from moss import DocumentInfo, MossClient, QueryOptions

if TYPE_CHECKING:
    from google.adk.skills.models import Skill

logger = logging.getLogger(__name__)


class SkillRouter:
    """Routes capability requests to skills using Moss semantic search.

    Uses Moss (moss-minilm) for embeddings and similarity with two-stage
    hierarchical matching following the MCP-Zero pattern:

    - Stage 1 (Domain): Query skill names via the domain index
    - Stage 2 (Capability): Query skill descriptions via the capability index
    - Scoring: (domain_sim × cap_sim) × max(domain_sim, cap_sim)

    Two separate Moss indexes ensure each stage searches a different
    semantic space, making the MCP-Zero cubic scoring formula work
    correctly without overlap penalty adjustments.
    """

    _DOMAIN_INDEX = "skills-domain"
    _CAPABILITY_INDEX = "skills-capability"
    _MODEL_ID = "moss-minilm"
    _TOP_K_CANDIDATES = 5
    _SMALL_SKILL_SET_THRESHOLD = 20

    def __init__(
        self,
        skills: dict[str, Skill],
        client: MossClient | None = None,
    ):
        """Initialize the router with skills and optional MossClient.

        Args:
            skills: Dictionary mapping skill names to Skill objects
            client: MossClient instance. If None, creates one from
                MOSS_PROJECT_ID / MOSS_PROJECT_KEY env vars.
        """
        self._skills = skills
        self._client = client or MossClient(
            os.getenv("MOSS_PROJECT_ID"),
            os.getenv("MOSS_PROJECT_KEY"),
        )
        self._initialized = False

        # Metrics tracking
        self._total_routes = 0
        self._total_route_time = 0.0

    async def initialize(self) -> None:
        """Build and load Moss indexes for domain and capability matching.

        Creates two separate indexes:
        - Domain index: skill names for coarse-grained domain matching
        - Capability index: skill descriptions for fine-grained capability
          matching

        Call this once before using route().
        """
        if self._initialized:
            return

        start_time = time.time()
        logger.info(
            f"Initializing SkillRouter with {len(self._skills)} skills..."
        )

        # Build domain index: skill names for Stage 1 matching
        domain_docs = [
            DocumentInfo(id=name, text=name, metadata={"name": name})
            for name in self._skills
        ]
        await self._client.create_index(
            self._DOMAIN_INDEX, domain_docs, model_id=self._MODEL_ID
        )
        await self._client.load_index(self._DOMAIN_INDEX)

        # Build capability index: skill descriptions for Stage 2 matching
        capability_docs = [
            DocumentInfo(
                id=name,
                text=skill.description,
                metadata={"name": name},
            )
            for name, skill in self._skills.items()
        ]
        await self._client.create_index(
            self._CAPABILITY_INDEX, capability_docs, model_id=self._MODEL_ID
        )
        await self._client.load_index(self._CAPABILITY_INDEX)

        elapsed = time.time() - start_time
        logger.info(
            f"SkillRouter initialized in {elapsed:.2f}s "
            f"with {len(self._skills)} skills via Moss."
        )

        self._initialized = True

    def _ensure_initialized(self) -> None:
        """Raise if not initialized."""
        if not self._initialized:
            raise RuntimeError(
                "SkillRouter not initialized. Call initialize() first."
            )

    async def route(
        self,
        domain: str,
        capability: str,
        threshold: float = 0.6,
        top_k: int = 3,
    ) -> list[tuple[str, float]]:
        """Route a capability request to top-K matching skills.

        Implements two-stage hierarchical matching (MCP-Zero pattern):
        1. Query domain against skill names (domain index) → top candidates
        2. Query capability against skill descriptions (capability index)
        3. Score = (domain_sim × cap_sim) × max(domain_sim, cap_sim)

        Because each stage queries a different index (different semantic
        space), the MCP-Zero cubic scoring formula works correctly without
        overlap penalty adjustments.

        For small skill sets (≤ 20), the capability query fetches enough
        results to cover all skills, ensuring nothing is missed.

        Args:
            domain: The operational domain (e.g., "discord")
            capability: The specific capability needed (e.g., "send message")
            threshold: Minimum score to return a match (default 0.6)
            top_k: Maximum number of results to return (default 3)

        Returns:
            List of (skill_name, score) tuples, sorted by score descending.
            Empty list if no match exceeds threshold.
        """
        self._ensure_initialized()

        if not self._skills:
            return []

        start_time = time.time()
        self._total_routes += 1

        # Stage 1: Match domain against skill names
        domain_results = await self._client.query(
            self._DOMAIN_INDEX,
            domain,
            QueryOptions(top_k=self._TOP_K_CANDIDATES, alpha=1.0),
        )
        domain_scores = {doc.id: doc.score for doc in domain_results.docs}

        # Stage 2: Match capability against skill descriptions
        cap_top_k = max(top_k, self._TOP_K_CANDIDATES)
        if len(self._skills) <= self._SMALL_SKILL_SET_THRESHOLD:
            cap_top_k = len(self._skills)

        cap_results = await self._client.query(
            self._CAPABILITY_INDEX,
            capability,
            QueryOptions(top_k=cap_top_k, alpha=1.0),
        )
        cap_scores = {doc.id: doc.score for doc in cap_results.docs}

        # MCP-Zero scoring: combine domain and capability scores
        # Only score skills that appear in Stage 1 results
        scored_candidates = []
        for name, domain_sim in domain_scores.items():
            cap_sim = cap_scores.get(name, 0.0)
            final_score = (domain_sim * cap_sim) * max(domain_sim, cap_sim)
            scored_candidates.append((name, final_score))

        # Filter by threshold and sort by score
        filtered = [
            (name, score)
            for name, score in scored_candidates
            if score >= threshold
        ]
        results = sorted(filtered, key=lambda x: x[1], reverse=True)[:top_k]

        elapsed = time.time() - start_time
        self._total_route_time += elapsed

        if results:
            best_name = results[0][0]
            best_score = results[0][1]
            logger.debug(
                f"Route: '{domain}' + '{capability}' -> {len(results)} matches "
                f"(best: {best_name}@{best_score:.3f}, "
                f"time: {elapsed * 1000:.1f}ms)"
            )
        else:
            logger.debug(
                f"Route: '{domain}' + '{capability}' -> None "
                f"(time: {elapsed * 1000:.1f}ms)"
            )

        return results

    async def route_single_stage(
        self, query: str, threshold: float = 0.6
    ) -> str | None:
        """Single-stage routing for simple queries (fallback).

        Uses only the capability index for a single semantic search.
        Use this when you don't have separate domain/capability, just a
        single unified query string.

        Args:
            query: The query text to match
            threshold: Minimum similarity to return a match

        Returns:
            Best matching skill name, or None if no match exceeds threshold
        """
        self._ensure_initialized()

        if not self._skills:
            return None

        result = await self._client.query(
            self._CAPABILITY_INDEX,
            query,
            QueryOptions(top_k=1, alpha=1.0),
        )

        if not result.docs or result.docs[0].score < threshold:
            return None

        return result.docs[0].id

    def get_metrics(self) -> dict[str, float | int]:
        """Return routing metrics for monitoring.

        Returns:
            Dictionary with routing performance metrics.
        """
        avg_route_time = (
            self._total_route_time / self._total_routes
            if self._total_routes > 0
            else 0
        )

        return {
            "total_routes": self._total_routes,
            "total_route_time": self._total_route_time,
            "avg_route_time_ms": avg_route_time * 1000,
            "num_skills": len(self._skills),
        }
