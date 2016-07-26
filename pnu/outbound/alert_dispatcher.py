from pnu.outbound.alerter import smtp

class PnuAlertDispatcher ():
    def dispatch (self, data):
        # for each number in data, dispatch data[number]
        for poke_list, phone_num_list in data.items():
            smtp.send_message({
                "phone_number": phone_num_list,
                "pokemon_wanted": poke_list,
                "link": "example.com"
            })
