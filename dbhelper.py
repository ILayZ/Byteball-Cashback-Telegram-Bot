import sqlite3
import logging

# Enable logging
logging.basicConfig(#format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG
                    #,filename = u'cashbot.log'
                    )
logger     = logging.getLogger(__name__)


class DBHelper:

    def __init__(self, dbname="cashback.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS orders (customer text, address text, currency_amount int)"
        uidx = "CREATE UNIQUE INDEX IF NOT EXISTS uidx ON orders (customer, address)"
        #ownidx  = "CREATE INDEX IF NOT EXISTS ownIndex  ON items (owner ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(uidx)
        #self.conn.execute(ownidx)
        self.conn.commit()

    def add(self, user_data):
        logger.warning(str(user_data))
        stmt = "INSERT INTO orders (customer, address, currency_amount) VALUES (?, ?, ?)"
        args = (user_data['customer'], user_data['address'], user_data['currency_amount'])
        self.conn.execute(stmt, args)
        self.conn.commit()

    def rm(self, user_data):
        stmt = "DELETE FROM orders WHERE customer = (?) AND address = (?)"
        args = (user_data['customer'], user_data['address'])
        self.conn.execute(stmt, args)
        self.conn.commit()


    def get(self, user_data):
        stmt = "SELECT * FROM orders WHERE customer = (?)"
        args = (user_data['customer'])
        return [x[0] for x in self.conn.execute(stmt, args)]
