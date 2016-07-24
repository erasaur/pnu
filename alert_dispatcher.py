# TODO
# dispatcher should be responsible for batch-sending alerts to a list of phone
# numbers

class PnuAlertDispatcher (PnuHTTPClient):
    def dispatch (self, data):
        # for each number in data, dispatch data[number]
        pass
