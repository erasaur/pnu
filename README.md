Pokemon Near You (pnu, pronounced "new") http://pnu.space
=======================

# How to become a Champion for your location #
Find the steps now in the Wiki!


# Logging #
At the top of each file put
```python
import logging
logging = logging.getLogger(__name__)
```

If the file has an `if __name__ == "__main__":` line:
```python
if __name__ == "__main__":
    import logging
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(filename='../etc/logs/FILENAME.out',
            level=logging.DEBUG)
    
    logging.info("Beginning " + __file__)
```
**Just make sure you update the relative path to where the logging file should
be sent to**
