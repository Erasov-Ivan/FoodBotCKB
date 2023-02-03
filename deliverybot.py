from telethon import TelegramClient, events
from telethon.tl.custom import Button
import databaseconnection

TOKEN = 'xxx'
API_ID = 'xxx'
API_HASH = 'xxx'

password = 'ЦКБ2О23'
admpassword = 'ЦКБАДМИН'
data = databaseconnection.botdb(f'./deliverydata.db')

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=TOKEN)

capable_of_doing_orders = True

def main():
    bot.run_until_disconnected()

def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)

def return_order(order):
    order_text = ''
    order_sum = 0
    for i in range(len(order)):
        order_text = order_text + order[i][0] + ' ' + order[i][1] + 'p ' + str(order[i][2]) + 'шт \n '
        order_sum = order_sum + int(order[i][1])

    return order_text, order_sum

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    if data.user_exists(sender.id):
        if capable_of_doing_orders:
            match data.get_status(sender.id):
                case 'admin':
                    async with bot.conversation(await event.get_chat()) as conv:
                        await conv.send_message("<b>Список команд:\n</b><p>Получить заказы: /orders\n Заказы выполнены: /done</p>", parse_mode='html')
                case 'user':
                    if data.is_order_in_process(sender.id):
                        prices = data.get_prices()
                        categorys = data.get_categorys()

                        async with bot.conversation(await event.get_chat(), exclusive=True) as conv:
                            await conv.send_message("<b>Список блюд:</b>", parse_mode='html')
                            for c in range(len(categorys)):
                                await conv.send_message(f"<b>{categorys[c][0]}:</b>",parse_mode='html')
                                for i in range(len(prices)):
                                    if prices[i][0] == categorys[c][0]:

                                        dish_text = prices[i][1]
                                        keyboard = [Button.inline('+', '+ ' + dish_text + ' ' + str(prices[i][2])+ 'р'), Button.inline(f"{str(prices[i][2])+ 'р'}", ''),Button.inline('-', '- ' + dish_text + ' ' + str(prices[i][2])+ 'р')]

                                        await conv.send_message(f"{dish_text}", buttons=keyboard)

                            await conv.send_message('Заказ', buttons=([Button.inline('Посмотерть заказ', 'check')], [Button.inline('Завершить', 'end')]))

                            order = [] #[[order, price, amount], ...]
                            while True:
                                press = await conv.wait_event(press_event(sender.id))
                                pre_choice = str(press.data.decode("utf-8")).split()

                                if pre_choice[0] == 'end':
                                    order_text, order_sum = return_order(order)
                                    data.new_order(sender.id, order_text, order_sum)
                                    break

                                elif pre_choice[0] == 'check':
                                    order_text, order_sum = return_order(order)
                                    await conv.send_message(order_text + 'Общая сумма:' + str(order_sum) + 'p')
                                    continue

                                text = ''
                                for i in range(1, len(pre_choice)-1):
                                    text = text + pre_choice[i] + ' '
                                choice = [pre_choice[0], text, pre_choice[-1][:-1]]

                                if choice[1] != '':
                                    a = choice.pop(0)
                                    if a == '+':
                                        choice.append(1)
                                    elif a == '-':
                                        choice.append(-1)

                                    ad = True
                                    for i in range(len(order)):
                                        if order[i][0] == choice[0]:
                                            ad = False
                                            order[i][2] = order[i][2] + choice[2]
                                            if order[i][2] == 0:
                                                order.pop(i)
                                                break
                                    if ad and choice[2] != -1:
                                        order.append(choice)
                    else:
                        async with bot.conversation(await event.get_chat()) as conv:
                            await conv.send_message('Вы не можете сделать новый заказ пока не выполнен предыдущий. \n Ожидайте')
        else:
            async with bot.conversation(await event.get_chat()) as conv:
                await conv.send_message('Функция заказа недоступна: администратор выполняет заказы')
    else:
        async with bot.conversation(await event.get_chat()) as conv:
            await conv.send_message('Введите код')
            pas = await conv.get_response()
            pas = pas.message
            if pas == password or pas == admpassword:
                await conv.send_message('Введите ваши ФИО')
                fio = await conv.get_response()
                fio = fio.message
                data.new_user(sender.id)
                data.set_name(sender.id, fio)
                if pas == admpassword:
                    data.set_status(sender.id, 'admin')
                else:
                    data.set_status(sender.id, 'user')
                await conv.send_message('Вы зарегестрированы! \nДля заказа блюд нажмите /start')

            else:
                await conv.send_message('Неверный код, для повторной попытки нажмите /start')

@bot.on(events.NewMessage(pattern='/orders'))
async def check_orders(event):
    sender = await event.get_sender()
    if data.user_exists(sender.id):
        if data.get_status(sender.id) == 'admin':
            async with bot.conversation(await event.get_chat()) as conv:
                orders_adm = data.get_orders()
                for i in range(len(orders_adm)):
                    j = 0
                    orders_adm_text = orders_adm[i][1]
                    s = 'del'
                    while j < len(orders_adm_text):
                        if (orders_adm_text[j] == 'p' or orders_adm_text[j] == 'р') and s == 'int':
                            orders_adm_text = orders_adm_text[:j] + orders_adm_text[j + 2:]
                            j = j - 1
                            s = 'not_del'
                        if orders_adm_text[j] == 'т' and s == 'not_del':
                            s = 'del'
                        if orders_adm_text[j] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] and (s == 'del' or s == 'int'):
                            orders_adm_text = orders_adm_text[:j] + orders_adm_text[j+1:]
                            s = 'int'
                            j = j - 1
                        j = j + 1

                    await conv.send_message(data.get_name(orders_adm[i][0]) + '\n' + orders_adm_text + 'Итого ' + str(orders_adm[i][2]) + 'p')
                    capable_of_doing_orders = False

@bot.on(events.NewMessage(pattern='/done'))
async def done(event):
    async with bot.conversation(await event.get_chat()) as conv:
        await conv.send_message('Заказы завершены')
        data.clear_orders()
        capable_of_doing_orders = True

if __name__ == '__main__':
    main()
