
class Error:

    def __init__(self, msg, subj):
        self.msg = msg
        self.subj = subj

class ErrorMsg:

    def pne(self, incorrect_pokemon):
        """ error message for when a user submits a pokemon that is
        non-existent
        """
        msg = ("We didn't recognize the following Pokemon: {}. "
               .format(incorrect_pokemon) + "Double check the spelling and " +
               "try again.")
        subj = "Non-existent Pokemon"

        return Error(msg, subj)

    def oor(self, user_lat, user_lon):
        """ error message for when a user enrolls and is not within the
        location designated by their host
        """
        link = "https://github.com/erasaur/pnu/wiki/Location-Restrictions"
        msg = ("We're sorry, it looks like you are outside this regions' " +
               "designated tracking area. More information can be found " +
               "here {}".format(link))
        subj = "Out of Range"

        return Error(msg, subj)
