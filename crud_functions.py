import sqlite3


N = 4  # Количество продуктов в магазине - импортируется в основной файл

def initiate_db():
    connection = sqlite3.connect('products_14_4.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL
    );
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON Products (title)')

    for i in range(1, N + 1):
        cursor.execute('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)', (
            f'Продукт {i}',
            f'Описание {i}',
            f'{100 * i} руб.'))

    connection.commit()

def get_all_products():
    connection = sqlite3.connect('products_14_4.db')
    cursor = connection.cursor()
    products_list = cursor.execute('SELECT * FROM Products')
    msg = []
    for product in products_list:
        msg.append(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')
    connection.commit()
    return msg
