import time

from cassandra.cluster import Cluster,NoHostAvailable

def connect_cassandra():
    try:
        print("✅ Đang kết nối tới Cassandra...")
        cluster = Cluster(['localhost'])
        print("✅ Kết nối thành công đến cluster!")
        session = cluster.connect()
        print("✅ Đã kết nối session!")
        session.set_keyspace('stock_data')
        print('✅ Kết nối thành công Cassandra')
        return session, cluster
    except NoHostAvailable as e:
        print("❌ Không thể kết nối Cassandra:")
        for host, error in e.errors.items():
            print(f"  - Host: {host} | Error: {error}")
    except Exception as e:
        print("❌ Lỗi khác:", e)
        
def close_connection(session, cluster):
    session.shutdown()
    cluster.shutdown()

