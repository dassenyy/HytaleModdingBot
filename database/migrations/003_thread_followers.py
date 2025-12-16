from database.migration import Migration

class ThreadFollowers(Migration):
    def __init__(self):
        super().__init__(3, "Create thread followers table")
    
    async def apply(self, connection) -> bool:
        """Create thread_followers table"""
        async with connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS thread_followers (
                    thread_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    PRIMARY KEY (thread_id, user_id)
                ) ENGINE=InnoDB
            """)
        return True
    
    async def rollback(self, connection) -> bool:
        """Drop thread_followers table"""
        async with connection.cursor() as cursor:
            await cursor.execute("DROP TABLE IF EXISTS thread_followers")
        return True