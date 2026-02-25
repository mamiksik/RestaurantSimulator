from django.db.models import Sum

import RestaurantSimulator.models as models

def get_model_name(thread: models.SimulatedChatThread, for_role: models.RoleType) -> str:
    # While it makes sense to store these params with message as they are adjustable per request
    # for now, we assume they are all the same. If that is not the case, the UI has to be updated
    # this assert is to make sure this issues pops up when the time comes
    assert thread.messages.filter(role=for_role).values('model').distinct().count() == 1
    return thread.messages.filter(role=for_role).first().model

def get_model_temperature(thread: models.SimulatedChatThread, for_role: models.RoleType) -> float:
    # While it makes sense to store these params with message as they are adjustable per request
    # for now, we assume they are all the same. If that is not the case, the UI has to be updated
    # this assert is to make sure this issues pops up when the time comes
    assert thread.messages.filter(role=for_role).values('model').distinct().count() == 1
    return thread.messages.filter(role=for_role).first().temperature

def get_total_tokens_used(thread: models.SimulatedChatThread, for_role: models.RoleType) -> int:
    return (
        thread.messages
        .filter(role=for_role)
        .aggregate(Sum('total_tokens'))
        .get('total_tokens__sum')
    )

