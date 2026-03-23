"""SQLite persistence for spend records, sync metadata, and snapshots."""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Sequence
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Final

from api_spend.config import resolve_store_path
from api_spend.exceptions import StoreError
from api_spend.models import SpendRecord

logger = logging.getLogger(__name__)

DB_FILENAME: Final[str] = "spend.sqlite"

_SCHEMA: Final[str] = """
CREATE TABLE IF NOT EXISTS spend_records (
    provider    TEXT NOT NULL,
    service     TEXT NOT NULL,
    date        TEXT NOT NULL,
    amount      TEXT NOT NULL,
    currency    TEXT NOT NULL,
    UNIQUE(provider, service, date)
);

CREATE TABLE IF NOT EXISTS sync_metadata (
    provider      TEXT PRIMARY KEY,
    last_synced   TEXT NOT NULL,
    latest_date   TEXT
);

CREATE TABLE IF NOT EXISTS snapshots (
    provider       TEXT NOT NULL,
    recorded_at    TEXT NOT NULL,
    counter_value  INTEGER NOT NULL,
    quota_period   TEXT,
    UNIQUE(provider, recorded_at)
);
"""


def default_database_path() -> Path:
    """On-disk SQLite file path under ``resolve_store_path()`` (``IMPLEMENTATION_PLAN.md`` section 3)."""
    return resolve_store_path() / DB_FILENAME


def _date_iso(d: date) -> str:
    return d.isoformat()


def _dt_utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


class SpendStore:
    """SQLite store; use ``:memory:`` or a file path. Call ``close()`` when done."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    @classmethod
    def open(cls, path: str | Path) -> SpendStore:
        """
        Open or create the database. Creates parent directories for file paths.
        Use ``\":memory:\"`` for tests.
        """
        raw = str(path)
        try:
            if raw == ":memory:":
                conn = sqlite3.connect(raw)
            else:
                p = Path(path).expanduser().resolve()
                p.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(str(p))
                try:
                    conn.execute("PRAGMA journal_mode = WAL")
                except sqlite3.Error:
                    pass
        except (OSError, sqlite3.Error) as exc:
            raise StoreError(f"cannot open store at {path!r}: {exc}") from exc

        conn.execute("PRAGMA foreign_keys = ON")
        store = cls(conn)
        store._init_schema()
        logger.info("opened spend store path=%s", raw if raw == ":memory:" else str(Path(raw).resolve()))
        return store

    def _init_schema(self) -> None:
        self._conn.executescript(_SCHEMA)
        self._migrate_snapshots_quota_period()

    def _migrate_snapshots_quota_period(self) -> None:
        cur = self._conn.execute("PRAGMA table_info(snapshots)")
        cols = {row[1] for row in cur.fetchall()}
        if "quota_period" not in cols:
            self._conn.execute("ALTER TABLE snapshots ADD COLUMN quota_period TEXT")
            self._conn.commit()

    def close(self) -> None:
        logger.debug("closing spend store")
        self._conn.close()

    def upsert_spend_records(self, records: Sequence[SpendRecord]) -> None:
        if not records:
            return
        logger.debug("upsert_spend_records count=%d", len(records))
        rows = [
            (r.provider, r.service, _date_iso(r.date), str(r.amount), r.currency)
            for r in records
        ]
        self._conn.executemany(
            """
            INSERT OR REPLACE INTO spend_records (provider, service, date, amount, currency)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )
        self._conn.commit()

    def query_spend_records(
        self,
        start: date,
        end: date,
        providers: list[str] | None = None,
    ) -> list[SpendRecord]:
        """Return records with ``date`` in ``[start, end)``."""
        sql = """
            SELECT provider, service, date, amount, currency
            FROM spend_records
            WHERE date >= ? AND date < ?
        """
        params: list[Any] = [_date_iso(start), _date_iso(end)]
        if providers:
            placeholders = ",".join("?" * len(providers))
            sql += f" AND provider IN ({placeholders})"
            params.extend(providers)
        sql += " ORDER BY date, provider, service"
        cur = self._conn.execute(sql, params)
        out: list[SpendRecord] = []
        for provider, service, d, amount, currency in cur.fetchall():
            out.append(
                SpendRecord(
                    provider=provider,
                    service=service,
                    date=_parse_date(d),
                    amount=Decimal(amount),
                    currency=currency,
                )
            )
        return out

    def set_sync_metadata(
        self,
        provider: str,
        last_synced: datetime,
        latest_date: date | None,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO sync_metadata (provider, last_synced, latest_date)
            VALUES (?, ?, ?)
            ON CONFLICT(provider) DO UPDATE SET
                last_synced = excluded.last_synced,
                latest_date = excluded.latest_date
            """,
            (
                provider,
                _dt_utc_iso(last_synced),
                _date_iso(latest_date) if latest_date is not None else None,
            ),
        )
        self._conn.commit()

    def get_sync_metadata(self, provider: str) -> tuple[datetime, date | None] | None:
        row = self._conn.execute(
            "SELECT last_synced, latest_date FROM sync_metadata WHERE provider = ?",
            (provider,),
        ).fetchone()
        if row is None:
            return None
        last_synced, latest_date = row
        return (
            _parse_dt(last_synced),
            _parse_date(latest_date) if latest_date else None,
        )

    def provider_spend_date_bounds(self, provider: str) -> tuple[date | None, date | None]:
        """``(min_date, max_date)`` over ``spend_records`` for ``provider``; ``(None, None)`` if none."""
        row = self._conn.execute(
            "SELECT MIN(date), MAX(date) FROM spend_records WHERE provider = ?",
            (provider,),
        ).fetchone()
        if not row or row[0] is None:
            return None, None
        return _parse_date(row[0]), _parse_date(row[1])

    def is_memory_database(self) -> bool:
        """True when opened with ``:memory:`` (used for ``Status.store_size_bytes``)."""
        row = self._conn.execute("PRAGMA database_list").fetchone()
        if row is None:
            return False
        # row: dbid, name, file — in-memory main DB has empty file path
        return str(row[2] if len(row) > 2 else "") == ""

    def insert_snapshot(
        self,
        provider: str,
        recorded_at: datetime,
        counter_value: int,
        quota_period: str | None = None,
    ) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO snapshots (provider, recorded_at, counter_value, quota_period)
            VALUES (?, ?, ?, ?)
            """,
            (provider, _dt_utc_iso(recorded_at), counter_value, quota_period),
        )
        self._conn.commit()

    def get_latest_snapshot(self, provider: str) -> tuple[datetime, int, str | None] | None:
        row = self._conn.execute(
            """
            SELECT recorded_at, counter_value, quota_period
            FROM snapshots
            WHERE provider = ?
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            (provider,),
        ).fetchone()
        if row is None:
            return None
        recorded_at, counter_value, quota_period = row
        return (_parse_dt(recorded_at), int(counter_value), quota_period)

    def reset(self, providers: list[str] | None = None) -> None:
        """Delete stored data; ``None`` clears all providers."""
        logger.info(
            "store reset %s",
            "all providers" if not providers else f"providers={providers!r}",
        )
        if not providers:
            self._conn.execute("DELETE FROM spend_records")
            self._conn.execute("DELETE FROM sync_metadata")
            self._conn.execute("DELETE FROM snapshots")
        else:
            ph = ",".join("?" * len(providers))
            self._conn.execute(f"DELETE FROM spend_records WHERE provider IN ({ph})", providers)
            self._conn.execute(f"DELETE FROM sync_metadata WHERE provider IN ({ph})", providers)
            self._conn.execute(f"DELETE FROM snapshots WHERE provider IN ({ph})", providers)
        self._conn.commit()

    def approximate_size_bytes(self) -> int:
        """SQLite file logical size from page stats (works for ``:memory:`` too)."""
        page_count = self._conn.execute("PRAGMA page_count").fetchone()[0]
        page_size = self._conn.execute("PRAGMA page_size").fetchone()[0]
        return int(page_count * page_size)
