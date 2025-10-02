from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Iterable, List


@dataclass(frozen=True, slots=True)
class AttemptRecord:
    id: int
    problem_id: str
    submitted_answer: int
    is_correct: bool
    attempted_at: datetime


class AttemptRepository:
    """SQLite-backed repository for storing problem attempts."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id TEXT NOT NULL,
                    submitted_answer INTEGER NOT NULL,
                    is_correct INTEGER NOT NULL,
                    attempted_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            self.database_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )

    def record_attempt(
        self, *, problem_id: str, submitted_answer: int, is_correct: bool
    ) -> AttemptRecord:
        attempted_at = datetime.now(timezone.utc)
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO attempts (problem_id, submitted_answer, is_correct, attempted_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    problem_id,
                    int(submitted_answer),
                    1 if is_correct else 0,
                    attempted_at.isoformat(),
                ),
            )
            connection.commit()
            attempt_id = int(cursor.lastrowid)
        return AttemptRecord(
            id=attempt_id,
            problem_id=problem_id,
            submitted_answer=int(submitted_answer),
            is_correct=is_correct,
            attempted_at=attempted_at,
        )

    def list_attempts(self, problem_id: str | None = None) -> List[AttemptRecord]:
        query = "SELECT id, problem_id, submitted_answer, is_correct, attempted_at FROM attempts"
        params: tuple[object, ...] = ()
        if problem_id is not None:
            query += " WHERE problem_id = ?"
            params = (problem_id,)
        query += " ORDER BY id ASC"

        with self._lock, self._connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [self._row_to_record(row) for row in rows]

    def clear(self) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM attempts")
            connection.commit()

    def _row_to_record(self, row: Iterable[object]) -> AttemptRecord:
        id_, problem_id, submitted_answer, is_correct, attempted_at = row
        attempted_at_dt = datetime.fromisoformat(str(attempted_at))
        if attempted_at_dt.tzinfo is None:
            attempted_at_dt = attempted_at_dt.replace(tzinfo=timezone.utc)
        return AttemptRecord(
            id=int(id_),
            problem_id=str(problem_id),
            submitted_answer=int(submitted_answer),
            is_correct=bool(is_correct),
            attempted_at=attempted_at_dt,
        )


__all__ = ["AttemptRecord", "AttemptRepository"]

