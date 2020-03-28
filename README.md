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
	4. Run tracker_server.py
	    - take IP and port # from terminal after it runs [IP]:[port #]
	5. Manually edit client_server.py
	    - On line 13 -> TRACKER_ADDR = ('192.168.4.53', 5557)
	        -change the IP and Port # to the one you got in tracker_server.py
    5. command prompt: cd to folder where musicparty.py is located
    	-Run musicparty.py ([filepath] python musicparty.py)	

**How to host MusicParty:**

**How to Join MusicParty:**

**Authors:**

	Benjamin Rader:
	    - MusicParty music player GUI

	Braxton Laster:
		- Sockets, servers, and networking

**Posibble upgrades:**

	-port forwarding via. hole punching
	-more gui/fancier gui
	-"scrubber" to scrub through mp3 file
	-metadata processing
	-streaming mp3 capability