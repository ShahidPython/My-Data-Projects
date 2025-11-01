# storage.py — Enhanced SQLite database with categories and search

import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional

DB_PATH = Path("data/flashcards.db")

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for better performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_category ON cards(category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_question ON cards(question)")
    
    conn.commit()
    conn.close()

def add_card(question: str, answer: str, category: Optional[str] = None):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cards (question, answer, category) VALUES (?, ?, ?)", 
        (question.strip(), answer.strip(), category.strip() if category else None)
    )
    conn.commit()
    conn.close()

def get_all_cards(category: Optional[str] = None) -> List[Tuple]:
    conn = _connect()
    cur = conn.cursor()
    
    if category:
        cur.execute(
            "SELECT id, question, answer, category FROM cards WHERE category = ? ORDER BY id", 
            (category,)
        )
    else:
        cur.execute("SELECT id, question, answer, category FROM cards ORDER BY id")
    
    rows = cur.fetchall()
    conn.close()
    return rows

def get_card(card_id: int) -> Optional[Tuple]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, question, answer, category FROM cards WHERE id = ?", 
        (card_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row

def update_card(card_id: int, question: str, answer: str, category: Optional[str] = None):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """UPDATE cards 
           SET question = ?, answer = ?, category = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE id = ?""", 
        (question.strip(), answer.strip(), category.strip() if category else None, card_id)
    )
    conn.commit()
    conn.close()

def delete_card(card_id: int) -> bool:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

def get_categories() -> List[str]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM cards WHERE category IS NOT NULL ORDER BY category")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

def search_cards(search_term: str) -> List[Tuple]:
    conn = _connect()
    cur = conn.cursor()
    search_pattern = f"%{search_term}%"
    cur.execute(
        """SELECT id, question, answer, category 
           FROM cards 
           WHERE question LIKE ? OR answer LIKE ? OR category LIKE ?
           ORDER BY id""", 
        (search_pattern, search_pattern, search_pattern)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_stats() -> dict:
    conn = _connect()
    cur = conn.cursor()
    
    # Total cards
    cur.execute("SELECT COUNT(*) FROM cards")
    total = cur.fetchone()[0]
    
    # Total categories
    cur.execute("SELECT COUNT(DISTINCT category) FROM cards WHERE category IS NOT NULL")
    categories = cur.fetchone()[0]
    
    # Cards per category
    cur.execute("""
        SELECT category, COUNT(*) 
        FROM cards 
        WHERE category IS NOT NULL 
        GROUP BY category 
        ORDER BY COUNT(*) DESC
    """)
    by_category = {row[0]: row[1] for row in cur.fetchall()}
    
    conn.close()
    
    return {
        "total": total,
        "categories": categories,
        "by_category": by_category
    }