Pokemon Near You (pnu, pronounced "new")
=======================

[ [Website](https://pnu.space) | [Wiki](https://github.com/erasaur/pnu/wiki) ]

## How to enroll
Detailed instructions [here](https://pnu.space).

## How to become a Champion for your location
Please refer to the [wiki](https://github.com/erasaur/pnu/wiki/Enroll-to-be-a-Champion).

# For devs

## Setup
```bash
git clone git://github.com/erasaur/pnu.git
cd pnu
source setup_dev.sh # for local testing
source setup_prod.sh # for production deployment
```

## Running and monitoring
```bash
./run.sh # run the app
./check_status.sh # see whether redis and main app are running
./kill_all.sh # shut down redis and main app
./tail.sh # tail app logs
```
