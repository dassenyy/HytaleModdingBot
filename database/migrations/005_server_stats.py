from database.migration import Migration

class ServerStats(Migration):
    def __init__(self):
        super().__init__(5, "Create server statistics tables for Grafana")
    
    async def apply(self, connection) -> bool:
        """Create server stats tables"""
        async with connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS server_stats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    total_members INT NOT NULL,
                    online_members INT NOT NULL,
                    idle_members INT NOT NULL,
                    dnd_members INT NOT NULL,
                    offline_members INT NOT NULL,
                    INDEX idx_guild_time (guild_id, timestamp)
                ) ENGINE=InnoDB
            """)

            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    guild_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    last_message DATETIME NOT NULL,
                    PRIMARY KEY (guild_id, user_id),
                    INDEX idx_last_message (last_message)
                ) ENGINE=InnoDB
            """)
        return True
    
    async def rollback(self, connection) -> bool:
        """Drop server stats tables"""
        async with connection.cursor() as cursor:
            await cursor.execute("DROP TABLE IF EXISTS user_activity")
            await cursor.execute("DROP TABLE IF EXISTS server_stats")
        return True