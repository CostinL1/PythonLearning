def db_connector(host, user, cred, database, logmech='', tmode='TERA'):
    def db_conn(func):
        @wraps(func)
        def db_connection(*args, **kwargs):
            con = td.connect(host=host, user=user, password=cred,
                             database=database, logmech=logmech, tmode=tmode)
            with con.cursor() as cur:
                cur.execute(
                    "{fn teradata_nativesql}{fn teradata_autocommit_off}")
            try:
                result = func(con, *args, **kwargs)
            except Exception:
                con.rollback()
                raise
            else:
                con.commit()
            finally:
                con.close()
            return result
        return db_connection
    return db_conn
   
   
@db_connector(host, user, password, database, logmech)
def check_table(con: 'TeradataConnection', database: str, tablename: str) -> bool:
    sql = f"""  select count(*)
                    from dbc.tablesv
                    where tablename='{tablename}'
                    and databasename='{database}'
                """
    with con.cursor() as cur:
        try:
            row = cur.execute(sql).fetchall()
        except Exception:
            raise
        else:
            return False if int(row[0][0]) == 0 else True
