# https://philvarner.github.io/pages/novice-python3-db-api.html
#

def execute_in_transaction(connection_builder, callback):
    '''

    This is borrowed a bit from the Spring Framework `JdbcTemplate`

    :param connection_builder:
    :param callback:
    :return:
    '''
    with connection_builder() as conn:
        cursor = conn.cursor()
        try:
            result = callback(cursor)
            conn.commit()
            return result
        except BaseException as e:
            print(e)
        finally:
            if cursor:
                cursor.close()
