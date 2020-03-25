import socket
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading as thread
from pygame import mixer


class MusicParty(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('MusicParty ')
        self.resizable(False, False)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frame_list = [MainMenu, JoinParty, HostParty, Help, PartyScreen]
        self.frames = {}

        for frame in self.frame_list:
            current_frame = frame(container, self)
            self.frames[frame] = current_frame
            current_frame.grid(row=0, column=0, sticky='nsew')

        self.showFrame(MainMenu)

        statusbar = ttk.Label(self, text="Welcome to MusicParty", font='Times 10 italic')
        statusbar.pack(side=tk.BOTTOM)

    def showFrame(self, requested_frame):
        """Takes in a frame class and raises it to the front of the GUI"""
        frame = self.frames[requested_frame]
        frame.tkraise()


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # set some stylistic feautures for the Main Menu frame
        MainMenu.config(self, bg="black")
        label = tk.Label(self, bg="black", fg="#abb0b4", text="MusicParty v1.0.0", font=("Verdana", 48))
        label.pack(pady=10, padx=10)

        # Join Game button - brings JoinGame frame to the front
        join_button = ttk.Button(self, text="Join Party", command=lambda: controller.showFrame(JoinParty))
        join_button.place(height=40, width=300, relx=0.50, rely=0.35, anchor=tk.CENTER)

        # Host Game button - brings HostGame frame to the front
        host_button = ttk.Button(self, text="Host Party",
                                 command=lambda: controller.showFrame(HostParty))
        host_button.place(height=40, width=300, relx=0.50, rely=0.50, anchor=tk.CENTER)

        # Help page button - brings Help frame to the front
        help_button = ttk.Button(self, text="Help", command=lambda: controller.showFrame(Help))
        help_button.place(height=40, width=300, relx=0.50, rely=0.65, anchor=tk.CENTER)


class JoinParty(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        join_button = ttk.Button(self, text="Join Party", command=lambda: controller.showFrame(PartyScreen))
        join_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)


class HostParty(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        host_button = ttk.Button(self, text="Host Party", command=lambda: controller.showFrame(PartyScreen))
        host_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)


class Help(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        text = tk.Text(self, font=("Verdana", 11))
        text.insert(tk.INSERT,
                    '                                                     How To Use \'MusicParty\'                         \n'
                    '_______________________________________________________________________                                \n'
                    '                                                                HOST                                   \n'
                    '1. Press "Host Game" on the Main Menu                                             \n'
                    '2. Give the displayed IP and port number                                          \n'
                    '3. When all players have connected hit start, and type                            \n'
                    '------------------------------------------------------------------------------------------------------\n'
                    '                                                               PLAYER                                 \n'
                    '1. Press "Join Game" on the Main Menu                                             \n'
                    '2. Get the IP number and port number from the Host                                \n'
                    '      -type it in in format [IP #]:[port #]                                       \n'
                    '3. Once the host starts the game, a sentence will popup with the text box below it\n'
                    '4. Once done typing, HIT ENTER                                                    \n'
                    '5. Once all players are finished, score is determined by accuracy and time to     \n'
                    '   answer.  Winner is then displayed along with all of your stats                 \n'
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
        mixer.init()

        play_button = ttk.Button(self, text="Play",
                                 command=lambda: self.play_music('Ember Island - Leaving (Severo Remix).mp3'))
        play_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        browse_button = ttk.Button(self, text="Browse", command=lambda: self.browse_file())
        browse_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        stop_button = ttk.Button(self, text="Stop", command=lambda: self.stop_music())
        stop_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    # functions
    def play_music(self, filename):
        mixer.music.load(filename)
        mixer.music.play()

    def que():
        global x, c
        pos = pygame.mixer.music.get_pos()
        if int(pos) == -1:
            x += 1
            pygame.mixer.music.load(c[x])
            pygame.mixer.music.play(0)

        root.after(1, que)

    def stop_music(self):
        mixer.music.stop()

    def browse_file(self):
        global filename_path
        filename_path = filedialog.askopenfilename()
        add_to_playlist(filename_path)

        mixer.music.queue(filename_path)

    def add_to_playlist(filename):
        filename = os.path.basename(filename)
        index = 0
        playlistbox.insert(index, filename)
        playlist.insert(index, filename_path)
        index += 1

    def pause_music():
        global paused
        paused = TRUE
        mixer.music.pause()
        statusbar['text'] = "Music Paused"

    def rewind_music():
        play_music()
        statusbar['text'] = "Music Rewinded"

    def set_vol(val):
        volume = float(val) / 100
        mixer.music.set_volume(volume)
        # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1

    def mute_music():
        global muted
        if muted:  # Unmute the music
            mixer.music.set_volume(0.7)
            volumeBtn.configure(image=volumePhoto)
            scale.set(70)
            muted = FALSE
        else:  # mute the music
            mixer.music.set_volume(0)
            volumeBtn.configure(image=mutePhoto)
            scale.set(0)
            muted = TRUE


if __name__ == '__main__':
    app = MusicParty()
    app.geometry('720x360')
    # app.iconbitmap()
    app.mainloop()
