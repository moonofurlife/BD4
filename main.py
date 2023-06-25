import psycopg2
from psycopg2.sql import SQL, Identifier


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(40) NOT NULL,
            last_name VARCHAR(40) NOT NULL,
            email VARCHAR(40) NOT NULL
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone(
            client INTEGER NOT NULL REFERENCES client(id),
            phone VARCHAR(20)
        );
        """)

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO client(first_name, last_name, email)
                    VALUES (%s, %s, %s) RETURNING id, first_name
                    """, (first_name, last_name, email))
        res = cur.fetchone()
        print (f'Добавлен клиент {res[1]} с идентификатором {res[0]}\n')
        conn.commit()
        cur.execute("""
                        INSERT INTO phone(client, phone)
                        VALUES (%s, %s) RETURNING phone
                        """, (res[0], phones))
        conn.commit()

def add_phone(conn, client, phone):
    with conn.cursor() as cur:
        cur.execute("""
                        INSERT INTO phone(client, phone)
                        VALUES (%s, %s) RETURNING phone
                        """, (client, phone))
        res = cur.fetchone()
        print(f'Добавлен телефон {res[0]}\n')
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        arg_list = {'first_name': first_name, "last_name": last_name, 'email': email}
        for key, arg in arg_list.items():
            if arg:
                cur.execute(SQL("UPDATE client SET {}=%s WHERE id=%s").format(Identifier(key)), (arg, client_id))
            cur.execute("""
                    SELECT * FROM client
                    WHERE id=%s
                    """, client_id)
            return cur.fetchone()
            print("Данные обновлены успешно\n")

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT phone FROM phone
                    WHERE client=%s;
                    """, (client_id, ))
        res = cur.fetchall()
        counter = 1
        for i in res:
            print(f'{counter}. {i[0]}')
            counter+=1
        cur.execute("""
                        DELETE FROM phone
                        WHERE phone=%s;
                    """, (phone,))
        conn.commit()
        print(f'Телефон {phone} успешно удалён\n')


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        client = client_id
        cur.execute("""
                    DELETE FROM phone
                    WHERE client=%s;
                    """, (client,))
        conn.commit()
        cur.execute("""
                            DELETE FROM client
                            WHERE id=%s;
                            """, (client_id,))
        conn.commit()
    print("Пользователь удалён успешно\n")


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    try:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT c.first_name, c.last_name, c.email, p.phone From client c
            LEFT JOIN phone p ON c.id = p.client
            WHERE c.first_name=%s OR c.last_name=%s OR c.email=%s OR p.phone=%s;
            """, (first_name, last_name, email, phone,))
            return cur.fetchone()[0]
    except TypeError:
        return 'Такого клиента нет'


database = input('Введите название базы: ')
user = input("Введите пользователя: ")
password = input("Введите пароль: ")
with psycopg2.connect(database=database, user=user, password=password) as conn:
    create_db(conn)
    print(add_client(conn,'Ann', 'Kulian', 'kulian@gmail.ru'))
    print(add_phone(conn, '2', '89993738234'))
    print(change_client (conn, '1', 'Tim', 'Kulian', 'samual@mail.com'))
    print(delete_phone (conn, '1', '89109467816'))
    print(delete_client(conn, '4'))
    print(find_client(conn, 'Bob'))

conn.close()

