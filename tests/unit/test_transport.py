"""Unit tests for transport configuration."""

import os
from argparse import Namespace
from unittest.mock import patch

from jellyfin_mcp.transport import (
    create_argument_parser,
    get_transport_config,
    resolve_config,
    resolve_transport,
)


def test_get_transport_config_defaults():
    with patch.dict(os.environ, {}, clear=True):
        config = get_transport_config()
    assert config["transport"] == "stdio"
    assert config["port"] == 10934
    assert config["path"] == "/mcp"


def test_resolve_transport_from_args():
    assert resolve_transport(Namespace(http=True, sse=False, stdio=False)) == "http"
    assert resolve_transport(Namespace(http=False, sse=True, stdio=False)) == "sse"
    assert resolve_transport(Namespace(http=False, sse=False, stdio=True)) == "stdio"


def test_resolve_config_merges_env_and_args():
    args = Namespace(http=True, sse=False, stdio=False, host=None, port=9999, path=None)
    config = resolve_config(args)
    assert config["transport"] == "http"
    assert config["port"] == 9999


def test_argument_parser_has_transport_flags():
    parser = create_argument_parser("jellyfin-mcp")
    args = parser.parse_args(["--http", "--port", "10934"])
    assert args.http is True
    assert args.port == 10934
