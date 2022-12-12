FN_STATE = 'state.json' # I need a stateful web server

empty_state = {'evaluator_context_ready': 0,
               'evaluation_complete': 0,
               'current_action':0,
               'pred_fn': 'none'}

REDIS_BROKER_URL = 'redis://localhost:6379/0'
REDIS_RESULT_URL = 'redis://localhost:6379/0'

SEVER_PATH = './'
MODEL_PATH = SEVER_PATH + 'models/'
KEY_PATH = SEVER_PATH + 'serkey/'