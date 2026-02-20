#!/usr/bin/env python3
"""
Database Query and Analysis Script
Connects to a MySQL database and checks for log inconsistencies.
"""

import pymysql
import sys

# --- Database Configuration ---
DB_CONFIG = {
    'host': "localhost",
    'port': 7891,
    'user': "root",
    'password': "ineedyou",
    'database': "db_data",
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

QUERY = """
SELECT 
    u.user_id, 
    l.log_content, 
    l.method, 
    l.id AS log_id, 
    u.group_id, 
    a.api_id, 
    a.api_path
FROM table_log l
JOIN table_users u ON l.user_id = u.user_id
JOIN table_groups g ON u.group_id = g.group_id
JOIN table_api a ON a.api_id = g.api_id;
"""

def main():
    try:
        # 使用 with 语句自动管理连接关闭
        # Connect to the database
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            print("[*] Executing analysis query...")
            cursor.execute(QUERY)
            
            # 获取所有结果
            # Fetch all rows
            results = cursor.fetchall()
            
            print("[!] Found inconsistencies:")
            print(f"{'UserID':<10} | {'GroupID':<10} | {'APIID':<10} | {'LogID':<10}")
            print("-" * 50)
            
            count = 0
            for row in results:
                # 检查 api_path 是否在 log_content 中
                # Check if the allowed API path is present in the log content
                if row['api_path'] not in row['log_content']:
                    print(f"{row['user_id']:<10} | {row['group_id']:<10} | "
                          f"{row['api_id']:<10} | {row['log_id']:<10}")
                    count += 1
            
            print("-" * 50)
            print(f"[*] Total inconsistencies found: {count}")

    except pymysql.MySQLError as e:
        print(f"[!] Database error: {e}")
    except Exception as e:
        print(f"[!] An error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            print("[*] Database connection closed.")

if __name__ == "__main__":
    main()
