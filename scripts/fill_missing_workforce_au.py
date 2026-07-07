"""补齐 AU 11 条缺失的 workforce_size（LLM 估计口径，量级参考）。
幂等：按 (country_code='AU', occ_code) 精确更新，仅当 workforce_size 为空时写入。
"""
import os
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass
import pymysql

# occ_code -> 澳洲从业人数估计
VALUES = {
    "211411":  6000,   # Painter (Visual Arts)
    "211213":  8000,   # Musician (Instrumental)
    "211214":  3000,   # Singer
    "249212":  6000,   # Dance Teacher (Private Tuition)
    "452111": 30000,   # Fitness Instructor
    "452111Y":10000,   # Yoga Instructor
    "452316":  8000,   # Swimming Coach or Instructor
    "452317": 25000,   # Sports Coach or Instructor
    "451511": 12000,   # Driving Instructor
    "452413":  4000,   # Outdoor Adventure Instructor
    "251112":  5000,   # Nutritionist
}


def main():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"), port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"), password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"), charset="utf8mb4",
    )
    updated = 0
    try:
        with conn.cursor() as cur:
            for code, size in VALUES.items():
                cur.execute(
                    "UPDATE occupations SET workforce_size=%s "
                    "WHERE country_code='AU' AND occ_code=%s AND workforce_size IS NULL",
                    (size, code),
                )
                if cur.rowcount:
                    updated += cur.rowcount
                    print(f"  {code:<8} -> {size}")
        conn.commit()
        # 复核
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM occupations WHERE country_code='AU' AND workforce_size IS NULL")
            remaining = cur.fetchone()[0]
        print(f"updated={updated}  AU still-null={remaining}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
