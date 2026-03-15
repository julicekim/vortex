import psycopg2
from psycopg2.extras import execute_values
from loguru import logger
import pandas as pd
from brain.core.config import settings

class PostgresClient:
    """
    Vortex 전용 Postgres 데이터베이스 클라이언트.
    DB에서 프리마켓 데이터를 조회하고 분석 결과를 적재하는 역할을 수행한다.
    """
    def __init__(self):
        self.conn_params = {
            "dbname": settings.DB_NAME,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT
        }

    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def fetch_as_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        """SQL 쿼리 결과를 Pandas DataFrame으로 반환한다."""
        conn = None
        try:
            conn = self.get_connection()
            return pd.read_sql(query, conn, params=params)
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def insert_intelligence(self, records: list[dict]):
        """분석 결과를 v_vortex_intelligence 테이블에 적재한다."""
        if not records:
            return

        columns = [
            "timestamp", "ticker", "vol_surge", "vwap_dist", 
            "mins_open", "atr_comp", "probability", "is_danger"
        ]
        
        # list of dicts -> list of tuples
        data = [tuple(r.get(col) for col in columns) for r in records]
        
        query = f"""
            INSERT INTO v_vortex_intelligence ({", ".join(columns)})
            VALUES %s
        """
        
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                execute_values(cur, query, data)
            conn.commit()
            logger.success(f"Successfully inserted {len(records)} records into v_vortex_intelligence")
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to insert intelligence records: {e}")
            raise
        finally:
            if conn:
                conn.close()
