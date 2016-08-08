Pokemon Near You (pnu, pronounced "new")
=======================

# How to become a Champion for your location #
1. Register for a Pokemon Trainer Club account (preferably not your personal one)
2. Register an email address for your city. A good format would be pnuYourCity@gmail.com. ex. pnuSanFrancisco@gmail.com. If an email address is already taken, adding numbers at the end, such as pnuSanFrancisco1@gmail.com is the next best option. **Note:** This service is only tested for and currently works for gmail addresses. 
2. Clone this repo onto a server of some sort (EC2, Digital Ocean, your laptop, etc.). Currently this works for unix based OS's only with Python3.5.
3. Try running `setup_prod.sh` from the root of this project to get some things set up. There will likely be errors or problems during this, as every system is different, so feel free to reach out to us here.
4. Test your server is up and running by sending your location to your pnu email address and wait for a response. If there is a response, send a few common pokemon near you to see that you get notified. This make take a while if those pokemon do not appear very often.
5. Once it is confirmed that the service is running, you can update your pokemon wanted to your actual list of pokemon you are interested in.
6. Contact us by copy pasting this form below and sending it to pokemonnearyou+champs@gmail.com. Your latitude and longitude can be found using https://google.com/maps and clicking near your location.
    ```
    Your Name: REPLACE_WITH_YOUR_NAME
    
    Your City: REPLACE_WITH_YOUR_CITY
    
    Personal email: REPLACE_WITH_YOUR_EMAIL
    
    pnu email: REPLACE_WITH_RECENTLY_REGISTERED_EMAIL
    
    Your Lat: REPLACE_WITH_YOUR_LATITUDE
    
    Your Lon: REPLACE_WITH_YOUR_LONGITUDE
    
    Any other information you think we should know: REPLACE_WITH_MISC_INFO
    ```


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
