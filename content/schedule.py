from .location import OPEN_AIR_EVENT, OPEN_AIR_TOILET_EVENT, PARTY_EVENT
from .states import States
from .main_menu import menu_button
from utils import Event, Image, Button, Text

daily_button = Button(text="Расписание по дням", source=States.SCHEDULE)


SCHEDULE_MESSAGES = {
    States.SCHEDULE: Event(
        Image(path="schedule.jpg"),
        Image(
            path="details.png",
            caption="Выбери день, по которому тебе интересны детали и информация",
            keyboard=[
                [Button(text="22 августа, пятница", source=States.FIRST_DAY)],
                [Button(text="23 августа, суббота", source=States.SECOND_DAY)],
                [Button(text="24 августа, воскресенье", source=States.THIRD_DAY)],
                [menu_button],
            ],
        ),
    ),
    States.FIRST_DAY: Event(
        Text(
            text="<b>22 августа, ПЯТНИЦА</b>\n\n "
            "<i>16:00-19:00</i>\n\n "
            "Нижегородская ярмарка, ул. Совнаркомовская, д. 13\n "
            "Как же мы рады, что звёзды сошлись, и мы будем танцевать в одном из самых красивых мест города 😍\n\n "
            "Будем плясать под отборные треки от нашего главного диджея - Dj Миши♥ \n\n "
            "По вопросу участия в опене, если вы не являетесь обладателем пасса фестиваля, можно писать Маше.\n\n "
            "Регистрироваться на фестиваль можно будет уже на open-air`e! :)",
            keyboard=[
                [Button(text="Про open`air", source=States.SCHEDULE_OPENAIR)],
                [
                    Button(
                        text="О месте вечеринки", source=States.SCHEDULE_PARTY_FIRST_DAY
                    )
                ],
                [Button(text="Назад  ↩️", source=States.SCHEDULE)],
                [menu_button],
            ],
        ),
        Text(
            text="<i>21:00-02:00</i>\n "
            "<b>Расписание вечеринки</b>\n"
            "ул. Нижневолжская Набережная, 17б\n\n "
            "20:30-22:00 Dj кто-то\n "
            "22:00-23:00 Dj кто-то\n "
            "23:00-00:00 Dj кто-то",
        ),
    ),
    States.SCHEDULE_OPENAIR: OPEN_AIR_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [Button(text="Туалеты рядом", source=States.SCHEDULE_OPENAIR_TOILET)],
            [daily_button],
            [Button(text="Назад  ↩️", source=States.FIRST_DAY)],
            [menu_button],
        ],
    ),
    States.SCHEDULE_OPENAIR_TOILET: OPEN_AIR_TOILET_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [Button(text="Назад  ↩️", source=States.SCHEDULE_OPENAIR)],
            [daily_button],
            [menu_button],
        ],
    ),
    States.SCHEDULE_PARTY_FIRST_DAY: PARTY_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [Button(text="Назад  ↩️", source=States.FIRST_DAY)],
            [daily_button],
            [menu_button],
        ],
    ),
    States.SECOND_DAY: Event(
        Text(
            text="<b>23 августа, СУББОТА</b> \n"
            "Студия Social Dance Studio, ул. Б.Покровская, д.7, 2 этаж.\n\n "
            "<i>9:00-10:00</i> регистрация участников и выдача конвертов\n\n "
            "<i>10:00-17:00</i> Мастер-классы\n\n "
            "<i>19:00-03:00</i> Вечеринка с живой музыкой от группы The Lowcosters – главная вечеринка и соревнования\n\n "
            "______________________________________\n "
            "Все занятия будут в 2-х залах: \n "
            "NY — New-York\n "
            "BH — Big Hall\n\n "
            "На залах будут листы с обозначениями, на входе будет расписание, а администратор всегда готов вам помочь.",
            keyboard=[
                [Button(text="Занятие 1. 10:00 - 11:00", source="")],
                [Button(text="Занятие 2. 11:00 - 12:00", source="")],
                [Button(text="Бонус 1. 12:00 - 13:00", source="")],
                [
                    Button(
                        text="Main party 19:00 - 03:00",
                        source=States.SCHEDULE_PARTY_SECOND_DAY,
                    )
                ],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.SCHEDULE_PARTY_SECOND_DAY: Event(
        Image(
            path="location-party.jpeg",
            caption="<i>19:00-03:00</i>\n"
            "<b>Main party. ул. Нижневолжская Набережная, 17б</b>\n\n "
            'Как найти? Подробнее про это можно почитать в разделе главного меню "Локации"',
            keyboard=[
                [Button(text="Назад  ↩️", source=States.SECOND_DAY)],
                [daily_button],
                [menu_button],
            ],
        ),
        Image(
            path="details.png",
            caption="<b>Расписание вечеринки и диджеев</b>\n "
            "18:30-19:00 начало сбора гостей и участников соревнований.\n "
            "19:00-20:00 отборы JnJ\n "
            "20:00-20:30 Dj Игорь Кузнецов\n "
            "20:30-21:15 первый сет музыкантов\n\n "
            "__________________________\n "
            "<b>Что будет 23 августа?</b>\n "
            "♥Соревнования\n "
            "♥Классные диджеи\n "
            "♥Зажигательные The Lowcosters\n "
            "♥JnJ Invit\n "
            "♥Фотограф\n "
            "♥Видеограф\n "
            "♥Конкурс зрительских симпатий\n ",
        ),
        Image(
            path="schedule-group-first.jpg",
            caption="Для вас будет играть московская классная команда The Lowcosters – яркие представители бугерского "
            "движения. Рок-н-ролл у этих ребят в крови, всё своё свободное время они проводят среди "
            "друзей на концертах и танцевальных вечеринках.\n\n "
            "В репертуаре группы – известные композиции в стиле нео-свинг, рок-н-ролл, блюз, "
            "рокабилли – всё, что нужно для танцев буги-вуги и рокабилли-джайв.\n "
            "Команда часто выступает в клубах и на танцевальных вечеринках, "
            "они всегда с теплом и радостью встречаются танцорами.\n\n "
            "The Lowcosters всегда готовы зажигать и дарить радость своим слушателям. "
            "В этом году мы сможем с вами в этом убедиться 😉",
        ),
        Image(
            path="schedule-mix-match.jpg",
            caption="<b>Соревнования</b>\n\b "
            "В соревнованиях формата Mix&Match или Jack’n’Jill танцевальные пары совпадают "
            "случайным образом. На них вы сможете показать своё классное ведение-следование, "
            "умение понимать партнёра или качественно и понятно вести партнёршу.\n\n "
            "На нашем фестивале в соревнованиях будет три уровня: New Comers, Open и Advance. "
            "По умолчанию при регистрации вы попадаете в категорию Open. \n\n "
            "Если вы зарегистрировались, но желаете выступать в Advance, пожалуйста, сообщите об этом. "
            "Помимо этого в JnJ Advance мы лично приглашаем топовых танцоров со всей страны 😎\n\n "
            "Очень надеемся, что соревнования выйдут классными, душевными и зрелищными.\n "
            "А ещё не забывайте – финалы соревнований будут проходить под живую музыку!",
        ),
    ),
    States.THIRD_DAY: Event(
        Text(
            text="<b>25 августа, ВОСКРЕСЕНЬЕ</b> \n "
            "Студия Social Dance Studio, ул. Б.Покровская, д.7, 2 этаж.\n\n "
            "<i>10:00-17:00</i> Мастер-классы\n\n "
            "<i>20:00-00:00</i> Вечеринка с живой музыкой от группы ММВ\n\n "
            "_____________________________________\n "
            "Все занятия будут в 2-х залах: \n "
            "NY — New-York \n"
            "BH — Big Hall\n\n "
            "На залах будут листы с обозначениями, на входе будет расписание, а администратор всегда готов вам помочь.",
            keyboard=[
                [Button(text="Занятие 1. 10:00 - 11:00", source="")],
                [Button(text="Занятие 2. 11:00 - 12:00", source="")],
                [Button(text="Бонус 1. 12:00 - 13:00", source="")],
                [
                    Button(
                        text="Main party 18:30 - 00:00",
                        source=States.SCHEDULE_PARTY_THIRD_DAY,
                    )
                ],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.SCHEDULE_PARTY_THIRD_DAY: Event(
        Image(
            path="location-party.jpeg",
            caption="<i>19:00-03:00</i>\n"
            "<b>Main party. ул. Нижневолжская Набережная, 17б</b>\n\n "
            'Как найти? Подробнее про это можно почитать в разделе главного меню "Локации"',
            keyboard=[
                [Button(text="Назад  ↩️", source=States.THIRD_DAY)],
                [daily_button],
                [menu_button],
            ],
        ),
        Image(
            path="schedule-party-second.jpg",
            caption="<i>19:00-00:00</i>\n "
            "<b>Тематическая вечеринка</b>\n\n "
            "Тема вечеринки: пижама party 😴 🌒 \n\n "
            "У вас есть время выбрать или найти самую любимую пижаму 😏",
        ),
        Image(
            path="details.png",
            caption="<b>Расписание вечеринки и диджеев</b>\n\n "
            "20:00-21:00 Dj Роман Андреев\n "
            "21:00-21:45 первый сет музыкантов\n "
            "21:45-22:15 Dj Ксения Кирсанова\n "
            "22:15-23:00 второй сет музыкантов\n "
            "23:00-23:15 Dj Ксения Кирсанова\n "
            "23:15-23:40 третий сет музыкантов\n "
            "23:40-00:00 Dj Ксения Кирсанова\n",
        ),
        Image(
            path="schedule-group-second.jpg",
            caption="Заряжать нас энергией и рок-н-ролльным настроением будет классное трио ММБ 😎🔥\n\n "
            "«Мастера безумных танцев: Малкин, Базунов, Медянцев».\n "
            "«Рвём струны, расщепляем палки: Базунов, Медянцев, Малкин».\n "
            "«Когда от звука гнутся балки: Базунов, Медянцев, Малкин».\n\n "
            "Заинтриговали?\n "
            "Нижегородцы уже знакомы с ММБ и частенько кайфуют на концертах этой группы, "
            "пришло время познакомиться с ней бугерам со всей страны 😉",
        ),
    ),
}
