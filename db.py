
def execute_in_transaction(connection_builder, callback):
    '''

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
