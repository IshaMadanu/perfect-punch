from typing import Any, Optional

from psycopg.types.json import Jsonb

from perfectpunch_backend.db.connection import get_connection


def save_game_session(data: dict[str, Any]) -> dict[str, Any]:
    """Persist a game session in PostgreSQL."""
    session_id = data.get("session_id")
    if not session_id:
        raise ValueError("A session_id is required to save a game session.")

    with get_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO game_sessions (session_id, user_id, end_time, session_data)
            VALUES (%s, %s, %s::timestamptz, %s)
            RETURNING session_data
            """,
            (
                session_id,
                data.get("user_id") or "anonymous",
                data.get("end_time"),
                Jsonb(data),
            ),
        ).fetchone()

    return row[0]


def get_game_session(session_id: str) -> Optional[dict[str, Any]]:
    """Get the most recent stored record for a session ID."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT session_data
            FROM game_sessions
            WHERE session_id = %s
            ORDER BY end_time DESC NULLS LAST, created_at DESC
            LIMIT 1
            """,
            (session_id,),
        ).fetchone()

    return row[0] if row else None


def get_latest_session(user_id: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Get the latest stored game session, optionally filtered by user."""
    query = """
        SELECT session_data
        FROM game_sessions
    """
    params: tuple[str, ...] = ()

    if user_id:
        query += " WHERE user_id = %s"
        params = (user_id,)

    query += " ORDER BY end_time DESC NULLS LAST, created_at DESC LIMIT 1"

    with get_connection() as connection:
        row = connection.execute(query, params).fetchone()

    return row[0] if row else None


def get_latest_session_record(user_id: str) -> Optional[dict[str, Any]]:
    """Get the latest session and timestamp for an authenticated user."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT session_id, session_data, created_at
            FROM game_sessions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    if not row:
        return None

    return {
        "session_id": row[0],
        "data": row[1].get("session_data", row[1]),
        "timestamp": row[2].isoformat(),
    }


def get_game_sessions() -> list[dict[str, Any]]:
    """Get stored game sessions in creation order, newest first."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT session_data
            FROM game_sessions
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [row[0] for row in rows]
