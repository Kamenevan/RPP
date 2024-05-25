from flask import Flask, request, jsonify
import asyncpg

app = Flask(__name__)


async def connect_to_db():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port='5432',
        database='tgbot',
        user='postgres',
        password='egor2003'
    )
    return connection
# Проверка наличия валюты в БД
async def check_currency_exist(currency_name):
    connection = await connect_to_db()
    query = 'SELECT COUNT(*) FROM currencies WHERE currency_name = $1'
    result = await connection.fetchval(query, currency_name)
    await connection.close()
    return result > 0

# Загрузка валюты в БД
async def load_currency(currency_name, rate):
    connection = await connect_to_db()
    await connection.execute('''
        INSERT INTO currencies (currency_name, rate)
        VALUES ($1, $2)
    ''', currency_name, rate)
    await connection.close()

@app.route('/load', methods=['POST'])
async def load():
    data = request.get_json()
    currency_name = data['currency_name']
    rate = data['rate']

    currency_exists = check_currency_exist(currency_name)
    try:
        if currency_exists:
            return jsonify({'Ошибка': 'Валюта уже существует'}), 400
        else:
            load_currency(currency_name, rate)
            return jsonify({'Сообщение': 'Валюта загружена успешно'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_currency', methods=['POST'])
async def update_currency():
    data = request.get_json()
    currency_name = data['currency_name']
    new_rate = data['new_rate']


    currency_exists = check_currency_exist(currency_name)
    try:
        if not check_currency_exist:
            return jsonify({'Ошибка': 'Вылюты не существует'}), 400
        else:
            connection = await connect_to_db()
            await connection.execute('''
                UPDATE currencies 
                SET rate = $1 
                WHERE currency_name = $2
            ''', new_rate, currency_name)
            await connection.close()
            return jsonify({'Сообщение': 'Валюта успешно обновлена'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete', methods=['POST'])
async def delete():
    data = request.get_json()
    currency_name = data['currency_name']
    new_rate = data['new_rate']
    try:
        if not check_currency_exist:
            return jsonify({'Ошибка': 'Вылюты не существует'}), 400
        else:
            connection = await connect_to_db()
            await connection.execute('''
                DELETE FROM currencies 
                WHERE currency_name = $1
            ''', new_rate, currency_name)
            await connection.close()
            return jsonify({'Сообщение': 'Валюта успешно удалена'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)

