voicedio
========

this app simply allows a user to listen to a song on rdio by using their voice

however, the first song will be selected at random (one of the top 100), and the app will inform the user that the requested song is not as good.

from there on, the user can either accept a couple of lines of code telling them about how poor their taste in music is, or they can select to play the song they originally requested


Used things
-----------

flask

rdio api

other stuff (nothing big that comes to mind)

fun


Setup
-----
create a file rdio_consumer_credentials.py, with the following information:

RDIO_CONSUMER_KEY = 'foo'
RDIO_CONSUMER_SECRET = 'bar'