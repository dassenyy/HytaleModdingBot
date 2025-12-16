from database.migration import Migration

class TicketsSystem(Migration):
    def __init__(self):
        super().__init__(4, "Create tickets and ticket participants tables")
    
    async def apply(self, connection) -> bool:
        """Create tickets tables"""
        async with connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    created_at DATETIME NOT NULL,
                    closed_at DATETIME NULL,
                    closed_by BIGINT NULL,
                    status VARCHAR(20) DEFAULT 'open',
                    transcript_url TEXT,
                    INDEX idx_guild (guild_id),
                    INDEX idx_status (status),
                    INDEX idx_user (user_id)
                ) ENGINE=InnoDB
            """)
            
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS ticket_participants (
                    ticket_id INT NOT NULL,
                    user_id BIGINT NOT NULL,
                    added_by BIGINT NOT NULL,
                    added_at DATETIME NOT NULL,
                    PRIMARY KEY (ticket_id, user_id),
                    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)
        return True
    
    async def rollback(self, connection) -> bool:
        """Drop tickets tables"""
        async with connection.cursor() as cursor:
            await cursor.execute("DROP TABLE IF EXISTS ticket_participants")
            await cursor.execute("DROP TABLE IF EXISTS tickets")
        return True