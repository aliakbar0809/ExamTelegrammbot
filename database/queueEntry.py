from database.db import DatabaseConfig


class QueueEntry:
    def __init__(self, user_id=None, service=None, scheduled_time=None, position=None, db: DatabaseConfig = None):
        self.user_id = user_id
        self.service = service
        self.scheduled_time = scheduled_time
        self.position = position
        self.db = db

    async def save(self):
        try:
            async with self.db.pool.acquire() as conn:
                max_pos = await conn.fetchval("SELECT MAX(position) FROM queue_entries")
                next_pos = (max_pos or 0) + 1
                await conn.execute("""
                    INSERT INTO queue_entries (user_id, service, scheduled_time, status, position)
                    VALUES ($1, $2, $3, 'ожидает', $4)
                """, self.user_id, self.service, self.scheduled_time, next_pos)
        except Exception as e:
            print('Error from save queue entry:', e)

    async def get_user_active_entry(self):
        try:
            async with self.db.pool.acquire() as conn:
                return await conn.fetchrow("""
                    SELECT * FROM queue_entries
                    WHERE user_id = $1 AND status = 'ожидает'
                    ORDER BY created_at LIMIT 1
                """, self.user_id)
        except Exception as e:
            print('Error from get_user_active_entry:', e)

    async def get_all(self):
        try:
            async with self.db.pool.acquire() as conn:
                return await conn.fetch("""
                    SELECT qe.*, u.username, u.telegram_id
                    FROM queue_entries qe
                    JOIN users u ON u.id = qe.user_id
                    ORDER BY qe.position
                """)
        except Exception as e:
            print('Error from get_all:', e)

    async def update_status(self, entry_id, status):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE queue_entries
                    SET status = $1
                    WHERE id = $2
                """, status, entry_id)
        except Exception as e:
            print('Error from update_status:', e)

    async def cancel_user_entry(self):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE queue_entries
                    SET status = 'отменено'
                    WHERE user_id = $1 AND status = 'ожидает'
                """, self.user_id)
        except Exception as e:
            print('Error from cancel_user_entry:', e)

    async def swap_positions(self, pos1, pos2):
        try:
            async with self.db.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("UPDATE queue_entries SET position = -1 WHERE position = $1", pos1)
                    await conn.execute("UPDATE queue_entries SET position = $1 WHERE position = $2", pos2, pos1)
                    await conn.execute("UPDATE queue_entries SET position = $1 WHERE position = -1", pos2)
        except Exception as e:
            print('Error from swap_positions:', e)
