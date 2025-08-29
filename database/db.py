import asyncpg


class DatabaseConfig:

    def __init__(self, user, password, db_name, port=5432, host='localhost'):
        self.user = user
        self.password = password
        self.db_name = db_name
        self.port = port
        self.host = host
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                database=self.db_name,
                port=self.port,
                host=self.host
            )
        except Exception as e:
            print('Error from connect:', e)

    async def close(self):
        await self.pool.close()

    async def create_tables(self):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                fullname VARCHAR(100),
                created_at DATE DEFAULT CURRENT_DATE,
                is_staff BOOLEAN DEFAULT false
            );

            CREATE TABLE IF NOT EXISTS queue_entries (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
                service VARCHAR(200) NOT NULL,
                scheduled_time DATE,
                status VARCHAR(20) DEFAULT 'ожидает',
                created_at DATE DEFAULT CURRENT_DATE,
                position INT
            );

            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                duration INT,
                price INT,
                created_at DATE DEFAULT CURRENT_DATE
            );
            """)
        except Exception as e:
            print('Error from tables:', e)
