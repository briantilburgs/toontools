# toontools

toontools is just a python library for connecting to the Toon API and work with your own data.

Since the people of Toon/ Eneco don't like to give you access to your own information, we need to get it ourselves. 
This library contains a Toon connection (ToonAPIv3) and a toontools script that can be used to access toon data/ settings and 
set values to Toon.

## Create API keys
For toontools to work you'll need an account to access the API, this can be created at: https://developer.toon.eu/

after logging in register your app in 
Go to My Apps:
![alt tag](Toon-API-Registratie-01.png)

Add new App:
![alt tag](Toon-API-Registratie-02.png)

Choose a name and a fake URL:
the URL should be reachable, quick and reply as less info as possible
![alt tag](Toon-API-Registratie-03.png)

Get the Consumer Key & Secret:
![alt tag](Toon-API-Registratie-04.png)


## Configure toontools
The Consumer Key & Secret are needed in the Python program: place the values in conf/toon.json