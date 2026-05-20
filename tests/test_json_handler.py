import asyncio
import json
from types import SimpleNamespace

from handlers import json_handler


class _FakeAttachment:
    def __init__(self, filename: str, payload: dict):
        self.filename = filename
        self._payload = payload

    async def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _build_message(attachment: _FakeAttachment):
    return SimpleNamespace(
        guild=SimpleNamespace(id=111),
        channel=SimpleNamespace(id=222),
        attachments=[attachment],
        embeds=[],
        created_at=SimpleNamespace(
            replace=lambda **kwargs: SimpleNamespace(isoformat=lambda: "2026-05-12T22:00:00+00:00")
        ),
        id=999,
    )


def test_json_handler_falls_back_to_filename_uid(monkeypatch):
    attachment = _FakeAttachment(
        "match_GF-1234.json",
        {
            "producer": "GodForge",
            "games": [
                {
                    "blue_picks": ["Athena"],
                    "red_picks": ["Thor"],
                }
            ]
        },
    )
    message = _build_message(attachment)
    appended_rows = []

    async def immediate_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    async def ignore_admin(message, text):
        return None

    monkeypatch.setattr(json_handler.asyncio, "to_thread", immediate_to_thread)
    monkeypatch.setattr(json_handler, "_admin", ignore_admin)
    monkeypatch.setattr(json_handler.sheets_service, "evidence_exists", lambda *args, **kwargs: False)
    monkeypatch.setattr(json_handler.sheets_service, "get_active_sheet_id", lambda guild_id: "sheet-1")
    monkeypatch.setattr(json_handler.sheets_service, "append_evidence", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        json_handler.match_service,
        "import_godforge_draft",
        lambda *args, **kwargs: {"linked_match_id": "GF-1234"},
    )
    monkeypatch.setattr(
        json_handler.sheets_service,
        "append_match_log",
        lambda sheet_id, row: appended_rows.append(row),
    )

    asyncio.run(json_handler.handle_json_message(message))

    assert len(appended_rows) == 1
    assert appended_rows[0]["draft_id"] == "GF-1234"
    assert appended_rows[0]["blue_picks"] == "Athena"
    assert appended_rows[0]["red_picks"] == "Thor"


def test_json_handler_supports_nested_godforge_export(monkeypatch):
    attachment = _FakeAttachment(
        "godforge-export.json",
        {
            "producer": "GodForge",
            "match_id": "GF-0001",
            "teams": {
                "blue": {"captain": {"name": "BlueCap"}},
                "red": {"captain": {"name": "RedCap"}},
            },
            "fearless_pool": ["Bellona", "Sobek"],
            "games": [
                {
                    "game_number": 2,
                    "picks": {"blue": ["Athena"], "red": ["Thor"]},
                    "bans": {"blue": ["Hades"], "red": ["Loki"]},
                    "status": "Complete",
                }
            ],
        },
    )
    message = _build_message(attachment)
    appended_rows = []

    async def immediate_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    async def ignore_admin(message, text):
        return None

    monkeypatch.setattr(json_handler.asyncio, "to_thread", immediate_to_thread)
    monkeypatch.setattr(json_handler, "_admin", ignore_admin)
    monkeypatch.setattr(json_handler.sheets_service, "evidence_exists", lambda *args, **kwargs: False)
    monkeypatch.setattr(json_handler.sheets_service, "get_active_sheet_id", lambda guild_id: "sheet-1")
    monkeypatch.setattr(json_handler.sheets_service, "append_evidence", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        json_handler.match_service,
        "import_godforge_draft",
        lambda *args, **kwargs: {"linked_match_id": "GF-0001"},
    )
    monkeypatch.setattr(
        json_handler.sheets_service,
        "append_match_log",
        lambda sheet_id, row: appended_rows.append(row),
    )

    asyncio.run(json_handler.handle_json_message(message))

    assert len(appended_rows) == 1
    assert appended_rows[0]["draft_id"] == "GF-0001"
    assert appended_rows[0]["game_number"] == 2
    assert appended_rows[0]["blue_captain"] == "BlueCap"
    assert appended_rows[0]["red_captain"] == "RedCap"
    assert appended_rows[0]["blue_picks"] == "Athena"
    assert appended_rows[0]["red_picks"] == "Thor"
    assert appended_rows[0]["blue_bans"] == "Hades"
    assert appended_rows[0]["red_bans"] == "Loki"
    assert appended_rows[0]["fearless_pool"] == "Bellona, Sobek"
    assert appended_rows[0]["game_status"] == "Complete"
