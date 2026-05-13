from .location import OPEN_AIR_EVENT, PARTY_EVENT
from .states import States
from .main_menu import menu_button
from utils import Event, Image, Button, Text

daily_button = Button(text="Расписание по дням", source=States.SCHEDULE)
day_2nd_button = Button(text="Другие занятия", source=States.DAY_2ND)
day_3nd_button = Button(text="Другие занятия", source=States.DAY_3ND)
back_to_day_2nd = Button(text="Назад  ↩️", source=States.DAY_2ND)
back_to_day_3nd = Button(text="Назад  ↩️", source=States.DAY_3ND)


SCHEDULE_MESSAGES = {
    States.SCHEDULE: Event(
        Image(
            path="schedule.jpg",
            caption="Выбери день, по которому тебе интересны детали и информация",
            keyboard=[
                [Button(text="22 августа, пятница", source=States.DAY_1ND)],
                [Button(text="23 августа, суббота", source=States.DAY_2ND)],
                [Button(text="24 августа, воскресенье", source=States.DAY_3ND)],
                [menu_button],
            ],
        ),
    ),
    States.DAY_1ND: Event(
        Text(
            text="<b>22 августа, ПЯТНИЦА</b>\n\n"
            "<i>16:00-19:00</i>\n"
            "<b>Open-air</b>\n\n"
            "Нижегородская ярмарка, ул. Совнаркомовская, д. 13\n\n"
            "Как же мы рады, что звёзды сошлись, и мы будем танцевать в одном из самых красивых мест города 😍\n"
            "Будем плясать под отборные треки от Кокуева Михаила и Кирсановой Ксении ♥ \n\n"
            "<i>21:00-01:00</i>\n"
            "<b>Вечеринка</b>\n\n"
            "ул. Нижневолжская Набережная, 17б\n\n"
            "<b>Расписание вечеринки и диджеев</b>:\n"
            "21:00-22:20 Dj Петренко Максим\n"
            "22:20-23:40 Dj Матвеев Антон\n"
            "23:40-01:00 Dj Хохлова Анна\n\n"
            "По вопросу участия в мероприятии, если вы не являетесь обладателем пасса фестиваля, можно писать Маше.\n\n"
            "Регистрироваться на фестиваль можно будет на месте вечеринок! :)",
            keyboard=[
                [Button(text="О месте open-air`а", source=States.DAY_1ND_OPEN_AIR)],
                [
                    Button(
                        text="О месте вечеринки",
                        source=States.DAY_1ND_LOC_PARTY,
                    )
                ],
                [Button(text="Назад  ↩️", source=States.SCHEDULE)],
                [menu_button],
            ],
        )
    ),
    States.DAY_1ND_OPEN_AIR: OPEN_AIR_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [daily_button],
            [Button(text="Назад  ↩️", source=States.DAY_1ND)],
            [menu_button],
        ],
    ),
    States.DAY_1ND_LOC_PARTY: PARTY_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [Button(text="Назад  ↩️", source=States.DAY_1ND)],
            [daily_button],
            [menu_button],
        ],
    ),
    States.DAY_2ND: Event(
        Image(
            path="schedule-second-day.jpg",
            caption="<b>23 августа, СУББОТА</b> \n"
            "Студия Social Dance Studio, ул. Б.Покровская, д.7, 2 этаж.\n\n"
            "<i>9:30-10:00</i> - регистрация участников и выдача конвертов\n\n"
            "<i>10:00-17:00</i> - Мастер-классы\n\n"
            "<i>19:00-02:00</i> - Главная вечеринка с живой музыкой от группы The Lowcosters\n\n"
            "______________________________________\n"
            "Все занятия будут в 2-х залах: \n"
            "NY — New-York\n"
            "BH — Big Hall\n\n"
            "На залах будут листы с обозначениями, на входе будет расписание, а администратор всегда готов вам помочь.",
            keyboard=[
                [Button(text="Занятие 1. 10:00 - 11:30", source=States.DAY_2ND_1_LES)],
                [Button(text="Занятие 2. 11:45 - 13:15", source=States.DAY_2ND_2_LES)],
                [Button(text="Занятие 3. 14:00 - 15:30", source=States.DAY_2ND_3_LES)],
                [Button(text="Бонус. 15:45 - 17:00", source=States.DAY_2ND_4_LES)],
                [Button(text="Main party 19:00 - 02:00", source=States.DAY_2ND_PARTY)],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_1_LES: Event(
        Text(
            text="<b>Занятие 1. 10:00 - 11:30</b>\n\nВыбери уровень 👇",
            keyboard=[
                [Button(text="Beginner", source=States.DAY_2ND_1_LES_BEG)],
                [Button(text="Intermediate", source=States.DAY_2ND_1_LES_INT)],
                [back_to_day_2nd],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_1_LES_BEG: Event(
        Image(
            path="schedule-anton-katya.jpg",
            caption="<b>Антон Матвеев и Екатерина Громова</b>\n"
            "<i>Суббота, 23 августа, 10:00-11:30</i>\n\n"
            "Уровень: Beginner\n"
            "Зал: BH - Big Hall\n"
            "Тема: Вариации основного хода",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_2ND_1_LES)],
                [day_2nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_1_LES_INT: Event(
        Image(
            path="schedule-igor-olya.jpg",
            caption="<b>Игорь и Ольга Кузнецовы</b>\n"
            "<i>Суббота, 23 августа, 10:00-11:30</i>\n\n"
            "Уровень: Intermediate\n"
            "Зал: NY - New York\n"
            "Тема: Фигуры на 8-10-бесконечность",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_2ND_1_LES)],
                [day_2nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_2_LES: Event(
        Text(
            text="<b>Занятие 2. 11:45 - 13:15</b>\n\nВыбери уровень 👇",
            keyboard=[
                [Button(text="Intermediate", source=States.DAY_2ND_2_LES_INT)],
                [Button(text="Advanced", source=States.DAY_2ND_2_LES_ADV)],
                [back_to_day_2nd],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_2_LES_INT: Event(
        Image(
            path="schedule-lenya-liza.jpg",
            caption="<b>Леонид Несов и Елизавета Козуб</b>\n"
            "<i>Суббота, 23 августа, 11:45-13:15</i>\n\n"
            "Уровень: Intermediate\n"
            "Зал: BH - Big Hall\n"
            "Тема: Микромузыкальность и вариации основного хода",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_2ND_2_LES)],
                [day_2nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_2_LES_ADV: Event(
        Image(
            path="schedule-anton-katya.jpg",
            caption="<b>Антон Матвеев и Екатерина Громова</b>\n"
            "<i>Суббота, 23 августа, 11:45-13:15</i>\n\n"
            "Уровень: Advanced\n"
            "Зал: NY - New York\n"
            "Тема: Импровизация и музыкальность",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_2ND_2_LES)],
                [day_2nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_3_LES: Event(
        Text(
            text="<b>Занятие 3. 14:00 - 15:30</b>\n\nВыбери уровень 👇",
            keyboard=[
                [Button(text="Beginner", source=States.DAY_2ND_3_LES_BEG)],
                [Button(text="Advanced", source=States.DAY_2ND_3_LES_ADV)],
                [back_to_day_2nd],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_3_LES_BEG: Event(
        Image(
            path="schedule-igor-olya.jpg",
            caption="<b>Игорь и Ольга Кузнецовы</b>\n"
            "<i>Суббота, 23 августа, 14:00-15:30</i>\n\n"
            "Уровень: Beginner\n"
            "Зал: BH - Big Hall\n"
            "Тема: Танец как диалог",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_2ND_3_LES)],
                [day_2nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_3_LES_ADV: Event(
        Image(
            path="schedule-roma-sasha.jpg",
            caption="<b>Роман Андреев и Александра Метелькова</b>\n"
            "<i>Суббота, 23 августа, 14:00-15:30</i>\n\n"
            "Уровень: Advanced\n"
            "Зал: NY - New York\n"
            "Тема: Как быть удобными партнёрами и научиться слушать друг друга в танце.",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_2ND_3_LES)],
                [day_2nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_4_LES: Event(
        Text(
            text="<b>Бонус. 15:45 - 17:00</b>\n\nВыберите занятие 👇",
            keyboard=[
                [Button(text="Бонус: Поддержки", source=States.DAY_2ND_4_LES_1)],
                [Button(text="Бонус: Соло", source=States.DAY_2ND_4_LES_2)],
                [back_to_day_2nd],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_4_LES_1: Event(
        Image(
            path="schedule-roma-sasha.jpg",
            caption="<b>Роман Андреев и Александра Метелькова</b>\n"
            "<i>Суббота, 23 августа, 15:45-17:00</i>\n\n"
            "Уровень: Любой\n"
            "Зал: BH - Big Hall\n"
            "Тема: Поддержки и трюки",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_2ND_4_LES)],
                [day_2nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_4_LES_2: Event(
        Image(
            path="schedule-lenya-liza.jpg",
            caption="<b>Леонид Несов и Елизавета Козуб</b>\n"
            "<i>Суббота, 23 августа, 15:45-17:00</i>\n\n"
            "Уровень: Любой\n"
            "Зал: NY - New York\n"
            "Тема: Соло",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_2ND_4_LES)],
                [day_2nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_2ND_PARTY: Event(
        Image(
            path="schedule-dj.jpg",
            caption="<i>19:00-02:00</i>\n"
            "<b>Main party. ул. Нижневолжская Набережная, 17б</b>\n\n"
            "<b>Расписание вечеринки и диджеев</b>\n"
            "19:00-20:00 - Dj Кузнецов Игорь\n"
            "20:00-20:30 - Отборы M&M Open\n"
            "20:30-21:00 - Dj Громова Екатерина\n"
            "21:00-21:45 - Первый сет The Lowcosters\n"
            "21:45-22:00 - Полуфинал M&M Open\n"
            "22:00-22:45 - Второй сет The Lowcosters\n"
            "22:45-23:00 - Финал M&M New Comers\n"
            "23:00-23:20 - Финал M&M Open и Advanced под живую музыку\n"
            "23:20-23:45 - Третий сет The Lowcosters\n"
            "23:45-01:00 - Dj Матвеев Антон\n"
            "01:00-02:00 - Dj Кокуев Михаил\n\n"
            "__________________________\n"
            "<b>Что будет 23 августа?</b>\n"
            "♥Соревнования\n"
            "♥Классные диджеи\n"
            "♥Зажигательные The Lowcosters\n"
            "♥JnJ Invit\n"
            "♥Фотограф\n"
            "♥Видеограф\n"
            "♥Конкурс зрительских симпатий\n",
            keyboard=[
                [back_to_day_2nd],
                [Button(text="О месте вечеринки", source=States.DAY_2ND_LOC_PARTY)],
                [daily_button],
                [menu_button],
            ],
        ),
        Image(
            path="schedule-group-first.jpg",
            caption="Для вас будет играть московская классная команда The Lowcosters – яркие представители бугерского "
            "движения. Рок-н-ролл у этих ребят в крови, всё своё свободное время они проводят среди "
            "друзей на концертах и танцевальных вечеринках.\n\n"
            "В репертуаре группы – известные композиции в стиле нео-свинг, рок-н-ролл, блюз, "
            "рокабилли – всё, что нужно для танцев буги-вуги и рокабилли-джайв.\n"
            "Команда часто выступает в клубах и на танцевальных вечеринках, "
            "они всегда с теплом и радостью встречаются танцорами.\n\n"
            "The Lowcosters всегда готовы зажигать и дарить радость своим слушателям. "
            "В этом году мы сможем с вами в этом убедиться 😉",
        ),
        Image(
            path="schedule-mix-match.jpg",
            caption="<b>Соревнования</b>\n\n"
            "В соревнованиях формата Mix&Match или Jack’n’Jill танцевальные пары совпадают "
            "случайным образом. На них вы сможете показать своё классное ведение-следование, "
            "умение понимать партнёра или качественно и понятно вести партнёршу.\n\n"
            "На нашем фестивале в соревнованиях будет три уровня: New Comers, Open и Advance. "
            "По умолчанию при регистрации вы попадаете в категорию Open. \n\n"
            "Если вы зарегистрировались, но желаете выступать в Advance, пожалуйста, сообщите об этом. "
            "Помимо этого в JnJ Advance мы лично приглашаем топовых танцоров со всей страны 😎\n\n"
            "Очень надеемся, что соревнования выйдут классными, душевными и зрелищными.\n"
            "А ещё не забывайте – финалы соревнований будут проходить под живую музыку!",
        ),
    ),
    States.DAY_2ND_LOC_PARTY: PARTY_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [Button(text="Назад  ↩️", source=States.DAY_2ND_PARTY)],
            [daily_button],
            [menu_button],
        ],
    ),
    States.DAY_3ND: Event(
        Text(
            text="<b>25 августа, ВОСКРЕСЕНЬЕ</b> \n"
            "Студия Social Dance Studio, ул. Б.Покровская, д.7, 2 этаж.\n\n"
            "<i>10:00-17:00</i> - Мастер-классы\n\n"
            "<i>20:00-00:00</i> - Вечеринка с живой музыкой от группы ММВ\n\n"
            "_____________________________________\n"
            "Все занятия будут в 2-х залах: \n"
            "NY — New-York \n"
            "BH — Big Hall\n\n"
            "На залах будут листы с обозначениями, на входе будет расписание, а администратор всегда готов вам помочь.",
            keyboard=[
                [Button(text="Йога. 10:00 - 11:30", source=States.DAY_3ND_1_LES)],
                [Button(text="Занятие 1. 11:45 - 13:15", source=States.DAY_3ND_2_LES)],
                [Button(text="Занятие 2. 14:00 - 15:30", source=States.DAY_3ND_3_LES)],
                [Button(text="Бонус. 15:45 - 17:00", source=States.DAY_3ND_4_LES)],
                [Button(text="Вечеринка 20:00 - 00:00", source=States.DAY_3ND_PARTY)],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_1_LES: Event(
        Image(
            path="schedule-yoga.jpg",
            caption="Йога с Леонидом Несовым \n"
            "<i>Воскресенье, 10:00-11:30</i>\n\n"
            "Зал: BH - Big Hall \n"
            "Приходите, разомнемся после бодрой субботы и подготовимся к насыщенному воскресенью!",
            keyboard=[
                [back_to_day_3nd],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_2_LES: Event(
        Text(
            text="<b>Занятие 2. 11:45-13:15</b>\n\nВыбери уровень 👇",
            keyboard=[
                [Button(text="Beginner", source=States.DAY_3ND_2_LES_BEG)],
                [Button(text="Intermediate", source=States.DAY_3ND_2_LES_INT)],
                [back_to_day_3nd],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_2_LES_BEG: Event(
        Image(
            path="schedule-roma-sasha.jpg",
            caption="<b>Роман Андреев и Александра Метелькова</b>\n"
            "<i>Воскресенье, 24 августа, 11:45-13:15</i>\n\n"
            "Уровень: Beginner\n"
            "Зал: BH - Big Hall\n"
            "Тема: Отдыхаем в танце: ведомые проходки в паре",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_3ND_2_LES)],
                [day_3nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_2_LES_INT: Event(
        Image(
            path="schedule-igor-olya.jpg",
            caption="<b>Игорь и Ольга Кузнецовы</b>\n"
            "<i>Воскресенье, 24 августа, 11:45-13:15</i>\n\n"
            "Уровень: Intermediate\n"
            "Зал: NY - New York\n"
            "Тема: Минишоукейс",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_3ND_2_LES)],
                [day_3nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_3_LES: Event(
        Text(
            text="<b>Занятие 3. 14:00 - 15:30</b>\n\nВыбери свой уровень 👇",
            keyboard=[
                [Button(text="Intermediate", source=States.DAY_3ND_3_LES_INT)],
                [Button(text="Advanced", source=States.DAY_3ND_3_LES_ADV)],
                [back_to_day_3nd],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_3_LES_INT: Event(
        Image(
            path="schedule-roma-sasha.jpg",
            caption="<b>Роман Андреев и Александра Метелькова</b>\n"
            "<i>Воскресенье, 24 августа, 14:00-15:30</i>\n\n"
            "Уровень: Intermediate\n"
            "Зал: BH - Big Hall\n"
            "Тема: Комфортные переходы между фигурами на примере танцевальной связки",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_3ND_3_LES)],
                [day_3nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_3_LES_ADV: Event(
        Image(
            path="schedule-lenya-liza.jpg",
            caption="<b>Леонид Несов и Елизавета Козуб</b>\n"
            "<i>Воскресенье, 24 августа, 14:00-15:30</i>\n\n"
            "Уровень: Advanced\n"
            "Зал: NY - New York\n"
            "Тема: Вариации на усовершенствование ведения-следования",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_3ND_3_LES)],
                [day_3nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_4_LES: Event(
        Text(
            text="<b>Бонус. 16:30 - 18:00</b>\n\nВыбери занятие 👇",
            keyboard=[
                [Button(text="Бонус: Музыкальность", source=States.DAY_3ND_4_LES_ADV)],
                [Button(text="Бонус: Слоу", source=States.DAY_3ND_4_LES_BONUS)],
                [back_to_day_3nd],
                [daily_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_4_LES_ADV: Event(
        Image(
            path="schedule-roma-sasha.jpg",
            caption="<b>Роман Андреев и Александра Метелькова</b>\n"
            "<i>Воскресенье, 24 августа, 16:30-18:00</i>\n\n"
            "Уровень: Любой\n"
            "Зал: BH - Big Hall\n"
            "Тема: Музыкальность без счетов: что можно услышать в музыке",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_3ND_4_LES)],
                [day_3nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_4_LES_BONUS: Event(
        Image(
            path="schedule-anton-katya.jpg",
            caption="<b>Антон Матвеев и Екатерина Громова</b>\n"
            "<i>Воскресенье, 24 августа, 16:30-18:00</i>\n\n"
            "Уровень: Любой\n"
            "Зал: NY - New York\n"
            "Тема: Слоу",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.DAY_3ND_4_LES)],
                [day_3nd_button],
                [menu_button],
            ],
        )
    ),
    States.DAY_3ND_PARTY: Event(
        Image(
            path="schedule-party-second.jpg",
            caption="<i>20:00-00:00</i>\n"
            "<b>Main party. ул. Нижневолжская Набережная, 17б</b>\n\n"
            "<b>Тематическая вечеринка</b>\n\n"
            "Тема вечеринки: пижама party 😴 🌒. У вас есть время выбрать или найти самую любимую пижаму 😏\n\n"
            "<b>Расписание вечеринки и диджеев</b>\n\n"
            "20:00-21:00 - Dj Кирсанова Ксения\n"
            "21:00-21:30 - Первый сет ММБ\n"
            "21:30-21:45 - Dj Кирсанова Ксения\n"
            "21:45-22:15 - Второй сет ММБ\n"
            "22:15-22:30 - Dj Кокуев Михаил\n"
            "22:30-23:00 - Третий сет ММБ\n"
            "23:00-00:00 - Dj Кокуев Михаил\n",
            keyboard=[
                [back_to_day_3nd],
                [Button(text="О месте вечеринки", source=States.DAY_3ND_LOC_PARTY)],
                [daily_button],
                [menu_button],
            ],
        ),
        Image(
            path="schedule-group-second.jpg",
            caption="Заряжать нас энергией и рок-н-ролльным настроением будет классное трио ММБ 😎🔥\n\n"
            "«Мастера безумных танцев: Малкин, Базунов, Медянцев».\n"
            "«Рвём струны, расщепляем палки: Базунов, Медянцев, Малкин».\n"
            "«Когда от звука гнутся балки: Базунов, Медянцев, Малкин».\n\n"
            "Заинтриговали?\n"
            "Нижегородцы уже знакомы с ММБ и частенько кайфуют на концертах этой группы, "
            "пришло время познакомиться с ней бугерам со всей страны 😉",
        ),
    ),
    States.DAY_3ND_LOC_PARTY: PARTY_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [Button(text="Назад  ↩️", source=States.DAY_3ND_PARTY)],
            [daily_button],
            [menu_button],
        ],
    ),
}
