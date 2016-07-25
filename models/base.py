class Base ():
    def __init__ (self, *args, **kwargs):
        if len(args) > 0:
            self.load_json(args[0])
        else:
            self.load_json(kwargs)

    def load_json (self, data):
        try:
            for key, value in data.iteritems():
                self[key] = value
        except:
            raise Exception('trying to load invalid data')
