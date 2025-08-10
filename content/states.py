from enum import StrEnum


class States(StrEnum):
    DEFAULT = "default"
    START = "start"
    PRICE = "price"
    REGISTRATION = "registration"
    DINNER = "dinner"
    SCHEDULE = "schedule"

    FIRST_DAY = "schedule-first-day"
    SCHEDULE_OPENAIR = "schedule-openair"
    SCHEDULE_LOCATION_PARTY_FIRST_DAY = "schedule-location-party-first-day"

    SECOND_DAY = "schedule-second-day"
    SCHEDULE_TEMP_SECOND_DAY = "schedule-temp-second-day"
    SCHEDULE_PARTY_SECOND_DAY = "schedule-party-second-day"
    SCHEDULE_LOCATION_PARTY_SECOND_DAY = "schedule-location-party-second-day"

    THIRD_DAY = "schedule-third-day"
    SCHEDULE_PARTY_THIRD_DAY = "schedule-party-third-day"
    SCHEDULE_TEMP_THIRD_DAY = "schedule-temp-third-day"
    SCHEDULE_LOCATION_PARTY_THIRD_DAY = "schedule-location-party-third-day"

    LOCATION = "location"
    SDS = "location-sds"
    PARTY = "location-party"
    LOCATION_OPENAIR = "location-openair"

    LEVELS = "levels"
    CHAT = "chat"
    CONTACTS = "contacts"
