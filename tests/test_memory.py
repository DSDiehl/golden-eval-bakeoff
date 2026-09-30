"""Unit tests for context bloat compaction, session state, and async memory (Criteria #6, #7, #8)."""

import asyncio
import tempfile
import pytest
from src.bakeoff.memory import (
    MemoryBankAdapter,
    compact_run_history,
    configure_context_caching,
    summarize_candidate_transcript,
)


def test_sliding_window_compaction() -> None:
    """Criterion #6: History compaction reduces turn count while preserving recent turns."""
    events = [{"turn": i, "content": f"Execution turn {i}"} for i in range(25)]
    compacted = compact_run_history(events, window_size=5)

    assert len(compacted) == 7  # 1 system/head + 1 marker + 5 tail
    assert "HISTORY COMPACTED" in compacted[1]["content"]
    assert compacted[-1]["turn"] == 24


def test_transcript_summarization() -> None:
    """Criterion #6: Long candidate responses are compacted before reaching the judge."""
    long_text = "A" * 3000
    compacted = summarize_candidate_transcript(long_text, max_char_length=500)

    assert len(compacted) <= 600
    assert "TRANSCRIPT COMPACTED" in compacted


def test_vertex_context_caching_config() -> None:
    """Criterion #6: Vertex context caching configuration is emitted properly."""
    cfg = configure_context_caching(
        taxonomy_data=[{"cap": "test"}],
        rubric_text="Evaluate accuracy and safety on 1-5 scale.",
        ttl_minutes=120,
    )
    assert cfg["cache_enabled"] is True
    assert cfg["ttl_minutes"] == 120
    assert "domain_capability_taxonomy" in cfg["cached_components"]


@pytest.mark.asyncio
async def test_async_memory_persistence() -> None:
    """Criteria #7 & #8: Persistent session state and async background task execution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        adapter = MemoryBankAdapter(storage_dir=tmpdir)
        account_id = "test_isv_account"
        state = {"golden_cases": ["CASE_001", "CASE_002"], "version": "v1"}

        # Schedule async save
        task = adapter.save_account_state_async(account_id, state)
        assert isinstance(task, asyncio.Task)

        # Await completion
        await task

        # Verify durable retrieval
        loaded = adapter.load_account_baseline(account_id)
        assert loaded is not None
        assert loaded["account_id"] == account_id
        assert loaded["state"]["version"] == "v1"
