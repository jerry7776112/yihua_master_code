import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json


class DBM:
    _conn = None
    _curs = None

    def __init__(self, host='', port='', user='', password='', database=''):
        # 初始化參數
        self.host = host  
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.backup_path = ""
        self.backup_nameFormat = "{filename}-{strftime}.backup"
        self.backup_filename = ""
        # 連線到資料庫
        self._connectDB()

    # TODO 連線到 postgres 資料庫伺服器建立會話，返回connect實例
    def _connectDB(self):
        try:
            self._conn = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port)
            # 自動commit or rollback
            self._conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            # 創建SQL語句操作游標
            # 連線狀態 conn.status
            self._curs = self._conn.cursor()
        except psycopg2.Error as e:
            print('DB connect failed: ' + str(e))
            self._conn = None
        return self._conn



    # TODO 執行SQL語句
    def execute(self, sql, var=None):
        if self._operatingDB():
            try:
                self._curs.execute(sql, var)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print("ERROR SQL", sql)
                # Log.e('Execute failed:' + str(traceback.format_exc()))
                return False
                # return self._curs
        else:
            print("Execute failed: DB is busy or diconnect ! ")
            #Log.e("Execute failed: DB is busy or diconnect ! ")
            return False
        return self._curs



    # TODO 插入表內容
    # Data need dictionary (key-value) ex. {'custom_name': 'test', 'cost': 123}
    def insert(self, table, data, returning=None):
        try:
            if isinstance(data, str):  # Json str形態轉成Dict
                data = json.loads(data)

            cols, vals = self._format_insert(data)
            sql = "INSERT INTO %s (%s) VALUES(%s)" % (table, cols, vals)
            sql += self._returning(returning)
            cur = self.execute(sql, list(data.values()))  # data.values()  list(data.values())
            # if cur.statusmessage: Log.i('Insert Data in "%s" is OK\n%s' % (table, sql))
            return cur.fetchone() if returning else cur.rowcount
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

    def _format_insert(self, data):
        """格式化 insert dictionary 為SQL字串"""
        cols = ",".join(data.keys())
        vals = ",".join(["'%s'" % data[k] for k in data])
        return cols, vals

    def _returning(self, returning):
        if returning:
            return ' RETURNING %s' % returning
        return ''

    def _operatingDB(self):
        if self._conn is None or self._curs is None:
            return False
        if self._conn.closed == 0:  # 資料庫連線中
            if self._conn.status == psycopg2.extensions.STATUS_READY:  # 連結建立，可以操作
                return True
            elif self._conn.status == psycopg2.extensions.STATUS_BEGIN:  # 連結建立，目前忙碌中
                return False
            elif self._conn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:  # 連結建立，目前忙碌中(等價 STATUS_BEGIN )
                return False
            elif self._conn.status == psycopg2.extensions.STATUS_PREPARED:  # 連結建立，目前忙碌中
                return False
            else:  # 連結失敗
                return False
        else:  # 資料庫斷線
            return False