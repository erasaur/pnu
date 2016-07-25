#! /usr/bin/env python3.5

from pnu import Pnu
from config import pub_config

def main ():
    Pnu().run()

if __name__ == "__main__":
    import logging.config
    logging.config.fileConfig(pub_config['logging']['location'],
            disable_existing_loggers=False)
    main()
