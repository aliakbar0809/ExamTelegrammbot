from database.db import DatabaseConfig


class User:

    def __init__(self, telegram_id, username, fullname, db: DatabaseConfig):
        self.telegram_id = telegram_id
        self.username = username
        self.fullname = fullname
        self.db = db

    async def save(self):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (telegram_id, username, fullname)
                    VALUES ($1, $2, $3)
                """, self.telegram_id, self.username, self.fullname)
        except Exception as e:
            print('Error from save:', e)

    async def check_status(self):
        try:
            async with self.db.pool.acquire() as conn:
                is_staff = await conn.fetchrow("""
                    SELECT is_staff FROM users WHERE telegram_id = $1;
                """, self.telegram_id)
                return is_staff['is_staff'] if is_staff else False
        except Exception as e:
            print('Error check status:', e)


    async def get_user(self) -> bool:
        try:
            async with self.db.pool.acquire() as conn:
                user = await conn.fetchrow("""
        SELECT id FROM users WHERE telegram_id = $1
    """,self.telegram_id)
                return True if user else False
        except Exception as e:
            print('Error from get user',e)

