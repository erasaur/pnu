# TODO
# dispatcher should be responsible for batch-sending alerts to a list of phone
# numbers

from pnu.outbound.alerter import smtp

class PnuAlertDispatcher (PnuHTTPClient):
    def dispatch (self, data):
        # for each number in data, dispatch data[number]
        for poke_list, phone_num_list in data.iteritems():
            smtp.send_message({
                "phone_number": phone_num_list,
                "pokemon_wanted": poke_list,
                "link": "example.com"
            })
