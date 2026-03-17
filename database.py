import aiosqlite
from datetime import datetime

DB_PATH = "scammers.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS scammers (
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                group_id INTEGER,
                date_added TEXT,
                PRIMARY KEY (user_id, group_id)
            )
        ''')
        await db.commit()

async def add_scammer(user_id, username, first_name, group_id):
    async with aiosqlite.connect(DB_PATH) as db:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.execute('''
            INSERT OR REPLACE INTO scammers (user_id, username, first_name, group_id, date_added)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, group_id, date_str))
        await db.commit()

async def remove_scammer(user_id, group_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM scammers WHERE user_id = ? AND group_id = ?', (user_id, group_id))
        await db.commit()

async def is_scammer(user_id, group_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT 1 FROM scammers WHERE user_id = ? AND group_id = ?', (user_id, group_id)) as cursor:
            return await cursor.fetchone() is not None

async def get_scammers(group_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT username, first_name FROM scammers WHERE group_id = ?', (group_id,)) as cursor:
            return await cursor.fetchall()
