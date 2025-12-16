from database.migration import Migration

class InitialTables(Migration):
    def __init__(self):
        super().__init__(1, "Create initial database tables")
    
    async def apply(self, connection) -> bool:
        """Create all initial tables"""
        async with connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    moderator_id BIGINT NOT NULL,
                    reason TEXT,
                    timestamp DATETIME NOT NULL,
                    INDEX idx_guild_user (guild_id, user_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB
            """)
            
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS mod_actions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    user_id BIGINT NOT NULL,
                    moderator_id BIGINT NOT NULL,
                    reason TEXT,
                    duration INT,
                    timestamp DATETIME NOT NULL,
                    INDEX idx_guild_user (guild_id, user_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB
            """)
            
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS mod_config (
                    guild_id BIGINT PRIMARY KEY,
                    log_channel_id BIGINT
                ) ENGINE=InnoDB
            """)
        
        return True
    
    async def rollback(self, connection) -> bool:
        """Drop initial tables"""
        async with connection.cursor() as cursor:
            await cursor.execute("DROP TABLE IF EXISTS mod_config")
            await cursor.execute("DROP TABLE IF EXISTS mod_actions")
            await cursor.execute("DROP TABLE IF EXISTS warnings")
        return True