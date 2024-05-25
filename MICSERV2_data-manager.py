from flask import Flask, request, jsonify
import asyncpg

app = Flask(__name__)


async def connect_to_db():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port='5432',
        database='tgbot',
        user='postgres',
        password='123'
    )
    return connection
# Проверка наличия валюты в БД
async def check_currency_exist(currency_name):
    connection = await connect_to_db()
    query = 'SELECT COUNT(*) FROM currencies WHERE currency_name = $1'
    result = await connection.fetchval(query, currency_name)
    await connection.close()
    return result > 0

#Получение валюты
async def get_currency_rate(currency_name):
    connection = await connect_to_db()
    query = 'SELECT rate FROM currencies WHERE currency_name = $1'
    result = await connection.fetchval(query, currency_name)
    await connection.close()
    if not result:
        raise ValueError(f'Курс валюты для {currency_name} не найден')
    else:
        return result


@app.route('/convert', methods=['GET'])
async def convert():
    data = request.get_json()
    currency_name = data['currency_name']
    rate = data['rate']

    currency_name = request.args.get('currency_name')
    amount = float(request.args.get('amount'))

    currency_exists = check_currency_exist(currency_name)
    try:
        if not currency_exists:
            return jsonify({'Ошибка': 'Вылюты не существует'}), 400
        else:
            currency_rate = await get_currency_rate(currency_name)
            converted_amount = amount * currency_rate
            return jsonify({currency_rate, currency_name,'будет равняться',converted_amount}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/currencies', methods=['GET'])
async def currencies():
    connection = await connect_to_db()
    query = 'SELECT * FROM currencies'
    result = await connection.fetch(query, currency_name)
    await connection.close()
    try:
        if query:
            currencies_list = [dict(record) for record in result]
            return currencies_list
        else:
            return jsonify({'Ошибка': 'Список валют не найден'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002)




