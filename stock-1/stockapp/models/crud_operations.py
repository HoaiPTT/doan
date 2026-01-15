import threading
from cassandra.cluster import Cluster,NoHostAvailable
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
import ssl

session = None
cluster = None
start_cassandra=False
lock = threading.Lock() 


def get_session():
    global session, cluster,start_cassandra
    with lock: 
        if not start_cassandra:
            try:
                cluster = Cluster(['localhost'])
                session = cluster.connect()
                session.set_keyspace('stock_data')
                print('✅ Kết nối thành công keyspace stock_data')
            except NoHostAvailable as e:
                print("❌ Không thể kết nối Cassandra:")
                for host, error in e.errors.items():
                    print(f"  - Host: {host} | Error: {error}")
            except Exception as e:
                print("❌ Lỗi khác:", e)
    return session

def close_connection():
    global cluster
    if cluster:
        cluster.shutdown()
        cluster = None
        session = None
        print("🛑 Cassandra cluster disconnected.")

# CREATE: Thêm mới bản ghi vào bảng
def create_record(model_class, **kwargs):
   
    if session is None:
        print("Unable to proceed. Exiting program.")
        exit(1)
    query = f"INSERT INTO {model_class.__table__} ({', '.join(kwargs.keys())}) VALUES ({', '.join(['%s'] * len(kwargs))})"
    statement = SimpleStatement(query)
    session.execute(statement, tuple(kwargs.values()))
    print(f"✅ Record inserted into {model_class.__table__}")

# READ: Lấy thông tin bản ghi theo các điều kiện
def read_record(model_class, **conditions):
    if session is None:
        print("Unable to proceed. Exiting program.")
        exit(1)

    query = f"SELECT * FROM {model_class.__table__}"
    values = []
    if conditions:
        where_clauses = []
        for key, value in conditions.items():
            if isinstance(value, tuple) and len(value) == 2:  # (operator, real_value)
                op, val = value
                where_clauses.append(f"{key} {op} %s")
                values.append(val)
            else:
                where_clauses.append(f"{key}=%s")
                values.append(value)
        query += " WHERE " + " AND ".join(where_clauses) + " ALLOW FILTERING"

    statement = SimpleStatement(query)
    result = session.execute(statement, tuple(values))
    return result.all()


# UPDATE: Cập nhật bản ghi theo các điều kiện
def update_record(model_class, update_values, **conditions):
   
    if session is None:
        print("Unable to proceed. Exiting program.")
        exit(1)
    set_clause = ", ".join([f"{key}=%s" for key in update_values.keys()])
    where_clause = " AND ".join([f"{key}=%s" for key in conditions.keys()])
    query = f"UPDATE {model_class.__table__} SET {set_clause} WHERE {where_clause}"
    statement = SimpleStatement(query)
    session.execute(statement, tuple(update_values.values()) + tuple(conditions.values()))
    print(f"✅ Record(s) updated in {model_class.__table__}")

# DELETE: Xóa bản ghi theo các điều kiện
def delete_record(model_class, **conditions):
    if session is None:
        print("Unable to proceed. Exiting program.")
        exit(1)
    query = f"DELETE FROM {model_class.__table__} WHERE " + " AND ".join([f"{key}=%s" for key in conditions.keys()])
    statement = SimpleStatement(query, consistency_level=ConsistencyLevel.QUORUM)
    session.execute(statement, tuple(conditions.values()))
    print(f"✅ Record(s) deleted from {model_class.__table__}")

