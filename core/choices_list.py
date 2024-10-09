RUN_STATE_WAITING = 'waiting'
RUN_STATE_STARTED = 'started'
RUN_STATE_FINISHED = 'finished'
RUN_STATE_ERROR = 'error'

RUN_STATES = (
    (RUN_STATE_WAITING, "En attente"),
    (RUN_STATE_STARTED, "Démarré"),
    (RUN_STATE_FINISHED, "Finalisé"),
    (RUN_STATE_ERROR, "En erreur")
)

RUN_NAME_TO_KEY = dict([(value, key) for key, value in RUN_STATES])
