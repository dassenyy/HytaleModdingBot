from database.migration import Migration

class UpvotesTable(Migration):
    def __init__(self):
        super().__init__(2, "Create upvotes table with count-based schema")
    
    async def apply(self, connection) -> bool:
        """Create upvotes table"""
        async with connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS upvotes (
                    showcase_id BIGINT NOT NULL PRIMARY KEY,
                    count INT NOT NULL DEFAULT 0
                ) ENGINE=InnoDB
            """)
        return True
    
    async def rollback(self, connection) -> bool:
        """Drop upvotes table"""
        async with connection.cursor() as cursor:
            await cursor.execute("DROP TABLE IF EXISTS upvotes")
        return True