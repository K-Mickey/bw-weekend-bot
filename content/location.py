from .states import States
from .main_menu import menu_button
from utils import Event, Button, Text, Video, Image

OPEN_AIR_EVENT = Event(
    Image(
        path="location-open-air.webp",
        caption="<b>Open-air, 22 августа</b>\n\n"
        "Open-air будет на площади рядом с Нижегородской Ярмаркой на Совнаркомовской, д. 13\n\n"
        "Регистрация будет там же!\n\n"
        "<b>Как найти? См. фото и видео ниже👇</b>",
    ),
    Image(path="location-open-air-map.png"),
    Video(path="location-openair.MOV"),
)


PARTY_EVENT = Event(
    Text(
        text="<b>Все вечеринки: пт, сб, вс</b>\n"
        "Адрес: улица Нижневолжская Набережная, 17Б, 2 этаж.\n\n"
        "<b>Как найти? См. фото и видео ниже👇</b>",
    ),
    Image(path="location-party-map.jpeg"),
    Video(path="location-party.mp4"),
    Image(
        path="location-party-room.jpeg",
        caption="Покрытие в помещении - паркет.\n\n"
        "Переодеться можно будет в 3-х отдельных индивидуальных раздевалках, а вещи оставить в гардеробе.\n\n"
        "В самом помещении бара нет. С собой можно брать еду и напитки, соблюдая при этом чистоту помещения. "
        "\n\nБудет вода в кулере в холле.",
    ),
)


LOCATION_MESSAGES = {
    States.LOCATION: Event(
        Text(
            text="Выбери место из списка ниже👇",
            keyboard=[
                [Button(text='МК - Студия "Social Dance Studio"', source=States.SDS)],
                [Button(text="Open-air, 22 августа", source=States.LOCATION_OPENAIR)],
                [Button(text="Вечеринки", source=States.PARTY)],
                [menu_button],
            ],
        )
    ),
    States.SDS: Event(
        Image(
            path="location-sds.png",
            caption='<b>Студия "Social Dance Studio"</b>\n\n'
            "Адрес: ул. Б.Покровская, д. 7, 2 этаж\n\n"
            "<b>Как найти? См. фото и видео ниже👇</b>",
            keyboard=[
                [Button(text="Назад  ↩️", source=States.LOCATION)],
                [menu_button],
            ],
        ),
        Image(path="location-sds-map.jpg"),
        Video(path="location-sds.mp4"),
        Text(
            text="Занятия будут проходить в 2-х залах:\n"
            "ЗАЛ BH - Big Hall\n"
            "ЗАЛ NY - Нью-Йорк\n\n"
            "В студии есть отдельные мужская и женская раздевалки.\n\n"
            "Есть кулер напротив стойки администратора, а фонтанчик напротив женской раздевалки с питьевой водой.\n\n"
            "Также при входе в студию с левой стороны есть зона бесплатного чая и платного кофе.",
        ),
        Image(
            path="location-sds-coffee.jpg",
            caption="На мастер-классах нашего фестиваля можно приносить воду/чай/кофе/лимонад только в "
            "<b>закрытой</b> таре – бутылках, термокружках и кружках с крышками 🙏",
        ),
    ),
    States.LOCATION_OPENAIR: OPEN_AIR_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [Button(text="Назад  ↩️", source=States.LOCATION)],
            [menu_button],
        ],
    ),
    States.PARTY: PARTY_EVENT.copy_and_set_kb(
        number_message=0,
        keyboard=[
            [Button(text="Назад  ↩️", source=States.LOCATION)],
            [menu_button],
        ],
    ),
}
