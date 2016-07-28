Pokemon Near You (pnu, pronounced "new")
=======================
# Style #
Run `install_style.sh` located in the root of the project to install a local git hook that runs a pep8 check against any newly committed files.

# Logging #
At the top of each file put
```python
import logging
logging = logging.getLogger(__name__)
```

If the file has an `if __name__ == "__main__":` line, add:
```python
import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(filename='../etc/logs/FILENAME.out',
        level=logging.DEBUG)

logging.info("Beginning " + __file__)
```
**Just make sure you update the relative path to where the logging file should
be sent to**
