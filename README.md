                             **Music Party**
______________________________________________________________________

MusicParty allows for peer-to-peer distribution of mp3 files through
use of a "tracker server." The music player gui uses a combination of 
tkinter and pygame so that peers can play the music via a list.  If a
song is added to a peers list, then all the other peers download that
song immediately, and can play it individually.  
______________________________________________________________________

**How to set up 'Music Party':**

    1. Have some version of Python installed (3.0 or higher probably)
    2. Run these commands in command prompt:
	a. pip install pygame
	b. pip install mutagen.mp3
	c. pip install glob
	4. Run tracker_server.py
	    - take IP and port # from terminal after it runs [IP]:[port #]
	5. Manually edit client_server.py
	    - On line 13 -> TRACKER_ADDR = ('127.0.0.1', 5557)
	        -change the IP and Port # to the one you got from tracker_server.py
    5. command prompt: cd to folder where musicparty.py is located
    	-Run musicparty.py ([filepath] python musicparty.py)	

**How to host MusicParty:**

    Just run musicparty.py and click the host button. When the music playlist screen opens
    The server for that room should be ready, give/use the join key listed in the top right
    to allow other clients to join the server

**How to Join MusicParty:**
    Press the join button and enter the 4 digit key given by the host

**Authors:**

	Benjamin Rader:
	    - MusicParty music player GUI

	Braxton Laster:
		- Sockets, servers, and networking

**Posibble upgrades:**

	-TCP hole punching
	-more gui/fancier gui
	-"scrubber" to scrub through mp3 file
	-metadata processing
	-streaming mp3 capability