"""
Developers: Braxton Laster, Ben Rader
Desc: Main GUI and application of MusicParty
"""

import socket
import os
import time
import sys
import pickle
import glob
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import threading
import pygame
from pygame import mixer
from mutagen.mp3 import MP3
import client_server

HEADER_SIZE = 4096
SEPARATOR = '|'


class MusicParty(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('MusicParty')
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.onClosing)

        self.room_server = None
        self.join_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.join_addr = None
        self.tracker_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.server_thread = None
        self.serverListener_thread = None

        # list of mp3 filepaths
        self.playlist = []

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frame_list = [MainMenu, Help, PartyScreen]
        self.frames = {}

        for frame in self.frame_list:
            current_frame = frame(container, self)
            self.frames[frame] = current_frame
            current_frame.grid(row=0, column=0, sticky='nsew')

        self.showFrame(MainMenu)

        # create and run thread to automate playlist
        self.playlist_autoadd_thread = threading.Thread(target=self.playlist_auto_adder)
        self.playlist_autoadd_thread.start()


    def showFrame(self, requested_frame):
        """Takes in a frame class and raises it to the front of the GUI"""
        print('Frame: {}'.format(requested_frame))
        frame = self.frames[requested_frame]
        frame.tkraise()

    def hostStartup(self):
        self.room_server = client_server.Server()
        self.server_thread = threading.Thread(target=self.room_server.start).start()

        while not self.room_server.join_key:
            pass
        self.findRoomIP(self.room_server.join_key)

    def joinRoom(self):
        popup = tk.Toplevel()
        popup.title('Join a Room')

        label = tk.Label(popup, text='Enter room code to join')
        label.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        join_addr = ttk.Entry(popup)
        join_addr.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

        connect_button = ttk.Button(popup, text='Connect', command=lambda: self.findRoomIP(join_addr.get(), popup))
        connect_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    def findRoomIP(self, join_key, popup=None):
        print('findRoomIP Joinkey: {}'.format(join_key))
        self.tracker_server.sendto(join_key.encode('UTF-8'), client_server.TRACKER_ADDR)
        join_addr, tracker_addr = self.tracker_server.recvfrom(1024)
        self.join_addr = pickle.loads(join_addr)

        print('roomIP addr: {}'.format(self.join_addr))
        self.join_server.connect(self.join_addr)
        print('ip connected...')

        if popup is not None:
            popup.destroy()

        self.showFrame(PartyScreen)
        self.serverListener_thread = threading.Thread(target=self.serverListener).start()

    def serverListener(self):
        print('Server listener started...')
        while True:
            song_header = self.join_server.recv(HEADER_SIZE)

            file_name, file_size = song_header.decode('utf-8').split(SEPARATOR)
            file_size = int(file_size)
            print('RECEIVING - Name: {} Size: {}'.format(file_name, file_size))

            song_file = open(file_name, 'wb')
            song_data = self.join_server.recv(HEADER_SIZE)
            download_progress = HEADER_SIZE
            while download_progress < file_size:
                print('<Client> Receiving chunk... {}/{}'.format(download_progress, file_size))
                song_file.write(song_data)
                song_data = self.join_server.recv(HEADER_SIZE)
                download_progress += HEADER_SIZE

            print('Song <{}> downloaded to client...'.format(file_name))
            song_file.close()

    def shareFile(self, filepath):
        print('Made it to shareFile')
        song_data = open(filepath, 'rb')
        song_name = os.path.basename(filepath)
        song_size = os.path.getsize(filepath)

        song_header = bytes('{}{}{}'.format(song_name, SEPARATOR, song_size), 'utf-8')
        self.join_server.send(song_header)

        chunk = song_data.read(HEADER_SIZE)
        while chunk:
            self.join_server.send(chunk)
            chunk = song_data.read(HEADER_SIZE)

    def playlist_auto_adder(self):
        print('auto adder running...')
        song_found = False
        directory = os.fsencode(os.getcwd())
        while True:
            music_files = [f for f in glob.glob('*.mp3', recursive=True)]
            for song in music_files:
                if song not in filter(lambda song: os.path.basename(song), self.playlist):
                    print('Found: {}'.format(song))
                    self.playlist.insert(0, song)
                    self.frames[PartyScreen].playlist_list.insert(0, song)  # appends to the playlist_list widget
            time.sleep(2)

    # Deals with making sure everything closes properly when closing the window
    def onClosing(self):
        try:
            self.destroy()
            self.server.shutdown()
        except:
            sys.exit(0)



class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # set some stylistic feautures for the Main Menu frame
        MainMenu.config(self, bg="black")
        label = tk.Label(self, bg="black", fg="#abb0b4", text="MusicParty v1.0.0", font=("Verdana", 48))
        label.pack(pady=10, padx=10)

        # Join Game button - brings JoinGame frame to the front
        join_button = ttk.Button(self, text="Join Party", command=lambda: controller.joinRoom())
        join_button.place(height=40, width=300, relx=0.50, rely=0.35, anchor=tk.CENTER)

        # Host Game button - brings HostGame frame to the front
        host_button = ttk.Button(self, text="Host Party",
                                 command=lambda: controller.hostStartup())
        host_button.place(height=40, width=300, relx=0.50, rely=0.50, anchor=tk.CENTER)

        # Help page button - brings Help frame to the front
        help_button = ttk.Button(self, text="Help", command=lambda: controller.showFrame(Help))
        help_button.place(height=40, width=300, relx=0.50, rely=0.65, anchor=tk.CENTER)

        music_player = ttk.Button(self, text="Music Player GUI", command=lambda: controller.showFrame(PartyScreen))
        music_player.place(height=40, width=300, relx=0.50, rely=0.80, anchor=tk.CENTER)


class Help(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        text = tk.Text(self, font=("Verdana", 11))
        text.insert(tk.INSERT,
                    '                                                     How To Use \'MusicParty\'                         \n'
                    '_______________________________________________________________________                                \n'
                    '                                                                HOST                                   \n'
                    '1. Press "Host Party" on the Main Menu                                             \n'
                    '2. Give the displayed IP and port number                                          \n'
                    '3. When all players have connected hit start, and type                            \n'
                    '------------------------------------------------------------------------------------------------------\n'
                    '                                                               PLAYER                                 \n'
                    '1. Press "Join Party" on the Main Menu                                             \n'
                    '2. Get the IP number and port number from the Host                                \n'
                    '      -type it in in format [IP #]:[port #]                                       \n'
                    '3. Once the host starts the game, a sentence will popup with the text box below it\n'
                    '4. Once done typing, HIT ENTER                                                    \n'
                    '                                                                                  \n'
                    '_______________________________________________________________________\n'
                    )
        text.configure(state='disable')
        text.pack()

        temp_button = ttk.Button(self,
                                 text='Main Menu',
                                 command=lambda: controller.showFrame(MainMenu))
        temp_button.place(relx=0.50, rely=0.9, anchor=tk.CENTER)


class PartyScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # allows for connection and more interaction with other classes
        mixer.init()
        pygame.init()

        self.MUSIC_ENDED = pygame.USEREVENT + 1
        mixer.music.set_endevent(self.MUSIC_ENDED)

        self.current_song = 0
        self.stopped = False
        self.paused = False
        self.playing = False
        self.current_song_playing = 'None'

        # button to play selected music - runs play_music()
        self.play_button = ttk.Button(self, text="Play",
                                      command=lambda: self.play_music())
        self.play_button.place(relx=0.73, rely=0.4, anchor=tk.CENTER)

        # button - pulls up file directory for choosing mp3 file to be added to playlist - runs browse_file()
        self.browse_button = ttk.Button(self, text="+ Add Files +", command=lambda: self.browse_file())
        self.browse_button.place(relx=0.73, rely=0.6, anchor=tk.CENTER)

        # button to stop music from playing - runs stop_music()
        self.stop_button = ttk.Button(self, text="Stop", command=lambda: self.stop_music())
        self.stop_button.place(relx=0.73, rely=0.8, anchor=tk.CENTER)

        # slider for controlling volume - runs set_vol()
        self.volume_button = ttk.Scale(self, from_=0, to=100, command=self.set_vol,
                                       length=150)
        self.volume_button.set(100)  # implement the default value of scale when music player starts
        mixer.music.set_volume(1.0)  # sets default volume to max
        self.volume_button.place(relx=0.73, rely=0.9, anchor=tk.CENTER)

        # display for list of mp3 names as they are added
        # allows for song to be selected via cursor press
        self.playlist_frame = ttk.LabelFrame(self, text="Song List")
        self.playlist_frame.place(x=30, y=30, width=300, height=300)
        self.playlist_scroll = ttk.Scrollbar(self.playlist_frame, orient=tk.VERTICAL)
        self.playlist_list = tk.Listbox(self.playlist_frame, yscrollcommand=self.playlist_scroll.set,
                                        selectmode=tk.SINGLE, relief=tk.GROOVE)
        self.playlist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_scroll.config(command=self.playlist_list.yview())
        self.playlist_list.pack(fill=tk.BOTH)
        self.playlist_list.config(width=300, height=300)

        # display for status of what is playing (filename) or if music is stopped - bottom of screen display
        self.statusbar = ttk.Label(self, text="MusicParty - No Song Chosen", relief=tk.SUNKEN, anchor=tk.W,
                                   font='Times 10 italic')
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # time display for song that is playing
        self.time_elapsed = ttk.Label(self, text="0:00:00", font=("Verdana", 20))
        self.time_elapsed.place(relx=0.638, rely=0.15, anchor=tk.CENTER)
        self.time_divider_slashes = ttk.Label(self, text="/", font=("Verdana", 20))
        self.time_divider_slashes.place(relx=0.73, rely=0.15, anchor=tk.CENTER)
        self.lengthlabel = ttk.Label(self, text="0:00:00", font=("Verdana", 20))
        self.lengthlabel.place(relx=0.819, rely=0.15, anchor=tk.CENTER)

        '''
        self.timeslider = ttk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, command=self.song_scrubber)
        self.timeslider.place(relx=0.6, rely=0.1, anchor=tk.CENTER)
        self.timeslider.set(0)
        self.after_id = None
        '''

        # create and run thread to automate playlist
        self.run_playlist_thread = threading.Thread(target=self.run_playlist_auto)
        self.run_playlist_thread.start()

    # checks for music_ended event in pygame event queue
    # if music has ended run play_next_song()
    def run_playlist_auto(self):
        while not self.stopped:
            for event in pygame.event.get():
                if event.type == self.MUSIC_ENDED:
                    self.play_next_song()

    # use filedialog from tkinter to choose file from file directory
    # adds mp3 to global playlist list
    def browse_file(self):
        global filename_path
        filename_path = filedialog.askopenfilename()

        if filename_path:
            self.add_to_playlist(filename_path)
            threading.Thread(target=self.controller.shareFile, args=[filename_path]).start()

    # plays selected music and runs related functions
    def play_music(self):
        self.get_time_elapsed()  # resets time display for song
        if self.stopped:  # if stopped make global stopped variable false - needed for other functions
            self.stopped = False
        if self.paused:  # if paused unpause music and make global paused variable false- needed for other functions
            mixer.music.unpause()  # unpauses music
            self.paused = False
        else:
            try:
                self.stop_music()  # stops any music that may have already been playing
                time.sleep(1)
                selected_song = self.playlist_list.curselection()  # gets tuple from playlist list tkinter widget
                selected_song = int(selected_song[0])  # takes first value of tuple (song filepath)
                song_to_play = self.controller.playlist[selected_song]
                mixer.music.load(song_to_play)  # loads mp3 or wav file based on song_to_play (filepath)
                mixer.music.play()  # plays loaded music
            except:
                try:
                    selected_song = self.controller.playlist[0]  # helps with variables in next try-except block
                    song_to_play = self.controller.playlist[0]
                    mixer.music.load(song_to_play)
                    mixer.music.play()
                except:
                    messagebox.showerror('Error playing song',
                                         'No song given or not .mp3 file')  # pop-up box with error
        try:
            # self.update_timeslider()
            self.current_song = selected_song
            self.show_details(song_to_play)  # updates total song length on time display and other stuff
            self.statusbar['text'] = "Playing music - " + os.path.basename(song_to_play)  # updates status bar
            self.stopped = False  # needed because complicated logic - self.stop music in first try block
            self.playing = True
            self.current_song_playing = song_to_play

        except:
            pass  # for the scenario where the play button is pressed with no songs in list

    # ran by check_music_thread when song ends
    def play_next_song(self):
        if len(self.controller.playlist) == 1:  # 1. if only one song in list
            song_to_play = self.controller.playlist[0]  # then replay that song
        elif self.controller.playlist.index(self.current_song) < len(self.controller.playlist):  # 2. if not last song
            song_to_play = self.controller.playlist[self.controller.playlist.index(self.current_song + 1)]
        else:
            song_to_play = self.controller.playlist[0]  # 3. if last song in playlist then go back to first song
        mixer.music.load(song_to_play)  # load what was assigned to song_to_play in one of
        mixer.music.play()  # the 3 scenarios above
        self.current_song = song_to_play  # assign song_to_play to current_song global variable

    # adds filename to the playlist by adding the file path
    def add_to_playlist(self, filename):
        filename = os.path.basename(filename)
        index = 0  # beginning of playlist
        # self.playlist_list.insert(index, filename)  # appends to the playlist_list widget
        self.controller.playlist.insert(index, filename_path)  # appends to actual playlist list variable
        # self.index+=
        self.current_song = filename_path  # assign filename_path of selected song to current_song global variable
        self.get_time_elapsed()  # update the total_length timer display
        # self.update_timeslider()
        self.statusbar['text'] = "Added to playlist - " + os.path.basename(filename_path)  # updates status bar when song is added
        self.add_to_playlist_status_thread = threading.Thread(target=self.add_to_playlist_status, args= [self.current_song_playing])
        self.add_to_playlist_status_thread.start()

    '''
    def pause_music(self):
        if self.paused == True:
            mixer.music.unpause()
            self.paused = False
        elif self.paused == False:
            mixer.music.pause()
            self.paused = True
    '''

    # sets volume using inputted value (val) - comes from scale widget (volume_button)
    def set_vol(self, val):
        volume = float(val) / 100
        mixer.music.set_volume(volume)
        # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1

    # stops music that is playing
    def stop_music(self):
        mixer.music.stop()
        self.stopped = True  # makes global stopped variable true - useful for other functions
        self.statusbar['text'] = "Music Stopped"  # update the status to show that music has stopped

    # returns the length in seconds using the current_song global variable to get data from mp3 file
    def getsonglen(self):
        s = mixer.Sound(self.controller.playlist[self.current_song])
        songlength = s.get_length()
        return songlength

    '''
    def set_timescale(self):
        songlength = self.getsonglen()
        # self.timeslider.config(to=songlength)
    '''

    # takes time that has passed from song that is playing - uses pygame.mixer
    def get_time_elapsed(self):
        time = int(mixer.music.get_pos() / 1000)  # divides seconds into sec,min,hour variables
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        clock = "%d:%02d:%02d" % (h, m, s)  # sets clock string variable based on inputted h,m,s variables
        self.time_elapsed.configure(text=clock)
        self.after(100, self.get_time_elapsed)  # sets clock display every second

    def add_to_playlist_status(self, current_song_playing):
        if self.stopped:
            time.sleep(2.5)
            self.song_selected_status(self.current_song)
        else:
            try:
                time.sleep(2.5)
                self.song_selected_status(current_song_playing)
            except:
                time.sleep(2.5)
                self.song_selected_status(self.current_song)

    #
    def song_selected_status(self, songname):
        if self.playing:
            self.song_selected_thread = threading.Thread(target=self.timeout_song_selected_status,
                                                                  args=[self.current_song])
            self.song_selected_thread.start()
        else:
            self.statusbar['text'] = "Song selected" + ' : ' + os.path.basename(songname)  # updates status bar

    #
    def timeout_song_selected_status(self, songname):
        try:
            selected_song = self.playlist_list.curselection()  # gets tuple from playlist list tkinter widget
            selected_song = int(selected_song[0])  # takes first value of tuple (song filepath)
            selected_song = self.controller.playlist[selected_song]
            self.statusbar['text'] = "Song selected" + ' : ' + os.path.basename(selected_song)  # updates status bar
            time.sleep(5)
            self.statusbar['text'] = "Playing music - " + os.path.basename(
                self.current_song_playing)  # updates status bar
        except:
            self.statusbar['text'] = "Song selected" + ' : ' + os.path.basename(songname)  # updates status bar
            time.sleep(5)
            self.statusbar['text'] = "Playing music - " + os.path.basename(self.current_song_playing)  # updates status bar
    #
    def show_details(self, play_song):
        file_data = os.path.splitext(play_song)
        if file_data[1] == '.mp3':  # if input is mp3 file get the total
            audio = MP3(play_song)  # length of it from metadata using
            total_length = audio.info.length  # mutagen.mp3 module
        else:
            a = mixer.Sound(play_song)
            total_length = a.get_length()

        # div - total_length/60, mod - total_length % 60
        mins, secs = divmod(total_length, 60)  # divides seconds into sec,min,hour variables
        hours, mins = divmod(mins, 60)
        hours = round(hours)
        mins = round(mins)
        secs = round(secs)
        timeformat = '{:d}:{:02d}:{:02d}'.format(hours, mins, secs)  # sets timeformat string variable based on input
        self.lengthlabel['text'] = timeformat  # updates total length time display


if __name__ == '__main__':
    app = MusicParty()
    app.geometry('720x360')
    pygame.init()
    app.mainloop()
