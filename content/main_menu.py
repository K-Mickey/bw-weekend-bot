from .states import States
from utils import Event, Button, Text, Image


menu_button = Button(text="Главное меню 🏠", source=States.START)


MENU_MESSAGES = {
    States.DEFAULT: Event(
        Text(
            text="Что-то пошло не так, давай попробуем ещё раз",
            keyboard=[[menu_button]],
        )
    ),
    States.START: Event(
        Image(
            path="header.jpg",
            caption="Привет, дорогой друг!👋\n"
            "Здесь много интересного о фестивале BW weekend, который будет проходить 22-24 августа 2025 года "
            "в Нижнем Новгороде!💃🕺",
            keyboard=[
                [
                    Button(text="Расписание", source=States.SCHEDULE),
                    Button(text="Цены", source=States.PRICE),
                ],
                [
                    Button(text="Регистрация участников", source=States.REGISTRATION),
                    Button(text="Обеды", source=States.DINNER),
                ],
                [
                    Button(text="Локации", source=States.LOCATION),
                    Button(text="Новости", source=States.NEWS),
                ],
                [
                    Button(text="Чат-болталка", source=States.CHAT),
                    Button(text="Связаться с организаторами", source=States.CONTACTS),
                ],
            ],
        )
    ),
    States.PRICE: Event(
        Image(
            path="price.jpg",
            caption="Те, кто ранее не покупал абонемент, может приобрести разовое участие в мероприятиях.\n\n"
            "Купить участие в вечеринке или на занятие можно: \n"
            "1. на стойке регистрации, \n"
            "2. во время регистрации участников \n"
            "3. дистанционно у Маши Романовой\n\n"
            "Контакты Маши: \n"
            "- телефон и telegram: +79101463516 \n"
            "- vk: https://vk.com/id81150340",
            keyboard=[[menu_button]],
        )
    ),
    States.REGISTRATION: Event(
        Text(
            text="Регистрация участников и получение номеров на соревнования: \n"
            "\n"
            "- <b>Пятница 16:00-17:00</b> во время open-air`а на площади около Ярмарки, ул.Совнаркомовская, д.13\n"
            "- <b>Суббота 9:30-11:30</b> до начала занятий в студии SDS, ул.Б.Покровская, д.7\n"
            "\n"
            "<i>Если Вы не приобрели абонементы, то можете приобрести разовое "
            "участие на вечеринки, занятия, соревнования или на день</i>",
            keyboard=[
                [Button(text="Цены", source=States.PRICE)],
                [menu_button],
            ],
        )
    ),
    States.DINNER: Event(
        Image(
            path="dinner.jpg",
            caption="Те, кто заказал готовые обеды, их нужно будет забрать самостоятельно в кафе NOOT "
            "по адресу: ул. Б.Покровская, д. 15 - от школы SDS это буквально 2 минуты пешком! \n\n"
            "<b>В субботу и воскресенье перерыв 13:15-14:00.</b> \n\n"
            "На Ваш выбор: вы можете либо поесть обед в кафе, либо взять с собой.",
        ),
        Image(path="dinner-cafe.jpeg"),
        Image(path="dinner-location.jpeg"),
        Text(
            text="Для тех, кто решил питаться самостоятельно, есть множество кафе и ресторанов по близости.\n\n"
            'Рядом со студией есть продуктовый магазин "Spar", ул.Б.Покровская 15.\n\n'
            'Между домами 10 и 12 находится вход на фудкорт "ЛЕТО", где также много вариантов быстрого перекуса.'
        ),
        Text(
            text="В студии предусмотрен  бесплатный чай и платный кофе в чайной зоне, "
            "есть микроволновка, но холодильника нет.\n\n"
            "Для тех, у кого еда с собой, или если вы хотите перекусить "
            "в кафе рядом, учитывайте, пожалуйста, время перерывов на обед.\n\n"
            "График у нас с вами плотный, но и планов масса!😅😎",
            keyboard=[[menu_button]],
        ),
    ),
    States.NEWS: Event(
        Text(
            text="Всё штатно. Всё по расписанию!😜",
            keyboard=[
                [Button(text="Расписание", source=States.SCHEDULE)],
                [menu_button],
            ],
        )
    ),
    States.CHAT: Event(
        Image(
            path="qr-chat.jpg",
            caption="Присоединяйтесь к нашему чату-болталке, чтобы делиться актуальным, "
            "узнавать интересное от других и просто ради классной компании!\n\n"
            "Чат болталка: https://t.me/+yh3kFrgAXe05NGYy",
            keyboard=[[menu_button]],
        )
    ),
    States.CONTACTS: Event(
        Text(
            text="Если нужно решить какой-то срочный вопрос - звони:\n\n"
            "+79101463516 - <b>Маша</b>\n"
            "+79991370059 - <b>Вова</b>\n"
            "+79506036231 - <b>Лариса</b>\n"
            "\n"
            "Группа в ВК: https://vk.com/bwweekend",
            keyboard=[[menu_button]],
        )
    ),
}
