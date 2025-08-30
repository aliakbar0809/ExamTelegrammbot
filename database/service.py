from database.db import DatabaseConfig


class Service:
    def __init__(self, name, duration, price, db: DatabaseConfig):
        self.name = name
        self.duration = duration
        self.price = price
        self.db = db

    async def save(self):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO services (name, duration, price)
                    VALUES ($1, $2, $3)
                """, self.name, self.duration, self.price)
        except Exception as e:
            print('Error from save:', e)

    @classmethod
    async def get_all_service(cls,db):
        try:
            async with db.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM services ORDER BY id
                """)
                return rows
        except Exception as e:
            print('Error from get_all_products:', e)

    async def get_by_id(self, service_id):
        try:
            async with self.db.pool.acquire() as conn:
                return await conn.fetchrow("SELECT * FROM services WHERE id = $1", service_id)
        except Exception as e:
            print('Error from get_by_id:', e)

    async def update(self, service_id):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE services
                    SET name = $1, duration = $2, price = $3
                    WHERE id = $4
                """, self.name, self.duration, self.price, service_id)
        except Exception as e:
            print('Error from update:', e)

    async def delete_service(self, service_id):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute("DELETE FROM services WHERE id = $1", service_id)
        except Exception as e:
            print('Error from delete:', e)
