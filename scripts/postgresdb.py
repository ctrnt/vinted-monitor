import psycopg2
from config.logging_config import setup_logging

class PostgresConnector():
    def __init__(self):
        self.DB_HOST = "postgres"
        self.DB_PORT = "5432"
        self.DB_NAME = "dbvinted"
        self.DB_USER = "admin"
        self.DB_PASS = "admin"

        self.logger = setup_logging()

        self.connect_to_db()
        
    def connect_to_db(self):
        self.conn = psycopg2.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            dbname=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASS
        )

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            price DECIMAL(10,2),
            url VARCHAR(255),
            src VARCHAR(255),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cur = self.conn.cursor()
        cur.execute(query)

        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
        cur.execute("CREATE INDEX IF NOT EXISTS idx_articles_title_trgm ON articles USING GIN (title gin_trgm_ops);")
    
        self.conn.commit()

    def offer_history(self, subject):
        query = """
            SELECT * FROM articles
            WHERE title ILIKE %s
            ORDER BY date DESC
            LIMIT 5;
        """

        try:
            cur = self.conn.cursor()
            cur.execute(query, (f"%{subject}%",))
            self.conn.commit()

        except Exception as e:
            self.logger.error(f"Error detected: {e}")

        return cur.fetchall()
    
    def inject_offer(self, title, price, url, src):
        query = """
            INSERT INTO articles (title, price, url, src) 
            VALUES (%s, %s, %s, %s);
        """
        
        try:
            cur = self.conn.cursor()
            cur.execute(query, (title, price, url, src))
            self.conn.commit()

        except Exception as e:
            self.logger.error(f"Error detected: {e}")