from django.db import connection
from django.db.models import Sum, Count, QuerySet
from django.db.models.functions import Lower

import RestaurantSimulator.models as models


def get_model_name(
    thread: models.SimulatedChatThread, for_role: models.RoleType
) -> str:
    # While it makes sense to store these params with message as they are adjustable per request
    # for now, we assume they are all the same. If that is not the case, the UI has to be updated
    # this assert is to make sure this issues pops up when the time comes
    assert thread.messages.filter(role=for_role).values("model").distinct().count() == 1
    return thread.messages.filter(role=for_role).first().model


def get_model_temperature(
    thread: models.SimulatedChatThread, for_role: models.RoleType
) -> float:
    # While it makes sense to store these params with message as they are adjustable per request
    # for now, we assume they are all the same. If that is not the case, the UI has to be updated
    # this assert is to make sure this issues pops up when the time comes
    assert thread.messages.filter(role=for_role).values("model").distinct().count() == 1
    return thread.messages.filter(role=for_role).first().temperature


def get_total_tokens_used(
    thread: models.SimulatedChatThread, for_role: models.RoleType
) -> int:
    return (
        thread.messages.filter(role=for_role)
        .aggregate(Sum("total_tokens"))
        .get("total_tokens__sum")
    )


def get_diet_distribution() -> dict:
    qs = models.SimulatedChatThread.objects.values(
        diet=Lower("extracted_answers__diet")
    ).annotate(count=Count("id"))
    return {
        row["diet"] if row["diet"] is not None else "Unknown": row["count"]
        for row in qs
    }


def get_all_favorite_foods(on: QuerySet[models.SimulatedChatThread, models.SimulatedChatThread]) -> dict:
    vendor = connection.vendor
    if vendor != "sqlite":
        raise Exception("Only sqlite database is supported for now")

    ids = list(on.values_list("id", flat=True))
    if not ids:
        return {}

    # IDs come from the database so it's 'safe' to embed them directly.
    # Use explicit int conversion to avoid any formatting surprises.
    # In real production app we would definitely use prepared statements,
    # but now I am getting "not all arguments converted during string formatting"
    ids_str = ",".join(str(int(i)) for i in ids)
    sql = f"""
          SELECT lower(trim(json_each.value)) AS food, count(*) AS count
          FROM RestaurantSimulator_simulatedchatthread,
              json_each(RestaurantSimulator_simulatedchatthread.extracted_answers, '$.top3_dishes')
          WHERE RestaurantSimulator_simulatedchatthread.extracted_answers IS NOT NULL
            AND RestaurantSimulator_simulatedchatthread.id IN ({ids_str})
          GROUP BY food
          ORDER BY count DESC
      """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows}
