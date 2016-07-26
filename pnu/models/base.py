class Base ():
    def __init__ (self, *args, **kwargs):
        if len(args) > 0:
            # loading by json as first arg
            if isinstance(args[0], dict):
                self.load_json(args[0])
            # loading by positional args
            else:
                self.load_args(*args, **kwargs)
        # loading by kwargs
        else:
            self.load_json(kwargs)

    def load_args (self, *args, **kwargs):
        # by default, just load kwargs as json
        self.load_json(kwargs)

    def load_json (self, data):
        try:
            for key, value in data.items():
                setattr(self, key, value)
        except:
            raise Exception('trying to load invalid data')
