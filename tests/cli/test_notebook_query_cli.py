"""Tests for notebook query CLI command with citations flag."""

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from notebooklm_tools.cli.main import app as main_app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_query_environment():
    mock_client = MagicMock()
    mock_client.__enter__ = lambda s: s
    mock_client.__exit__ = MagicMock(return_value=False)

    alias_mgr = MagicMock()
    alias_mgr.resolve.side_effect = lambda x: x

    query_return_value = {
        "answer": "This is the answer.",
        "conversation_id": "conv-123",
        "sources_used": ["source-1"],
        "citations": {1: "source-1"},
        "references": [{"id": "source-1", "title": "Doc 1"}],
    }

    with (
        patch("notebooklm_tools.cli.commands.notebook.get_alias_manager", return_value=alias_mgr),
        patch("notebooklm_tools.cli.commands.notebook.get_client", return_value=mock_client),
        patch(
            "notebooklm_tools.cli.commands.notebook.chat_service.query",
            return_value=dict(query_return_value),
        ) as mock_query,
    ):
        yield mock_query


def test_query_notebook_default_strips_citations(runner, mock_query_environment):
    result = runner.invoke(
        main_app,
        ["notebook", "query", "nb-123", "What is the speed of light?", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    payload = data.get("value", data)
    assert "citations" not in payload
    assert "references" not in payload
    assert payload["answer"] == "This is the answer."


def test_query_notebook_flag_retains_citations(runner, mock_query_environment):
    result = runner.invoke(
        main_app,
        ["notebook", "query", "nb-123", "What is the speed of light?", "--citations", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    payload = data.get("value", data)
    assert "citations" in payload
    assert "references" in payload
    assert payload["citations"] == {"1": "source-1"}
    assert payload["references"] == [{"id": "source-1", "title": "Doc 1"}]


def test_query_notebook_short_flag_retains_citations(runner, mock_query_environment):
    result = runner.invoke(
        main_app,
        ["notebook", "query", "nb-123", "What is the speed of light?", "-C", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    payload = data.get("value", data)
    assert "citations" in payload
    assert "references" in payload


def test_query_notebook_include_citations_alias(runner, mock_query_environment):
    result = runner.invoke(
        main_app,
        ["notebook", "query", "nb-123", "What is the speed of light?", "--include-citations", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    payload = data.get("value", data)
    assert "citations" in payload
    assert "references" in payload


def test_query_verb_notebook_flag_retains_citations(runner, mock_query_environment):
    result = runner.invoke(
        main_app,
        ["query", "notebook", "nb-123", "What is the speed of light?", "--citations", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    payload = data.get("value", data)
    assert "citations" in payload
    assert "references" in payload
