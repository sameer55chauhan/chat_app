import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msg

from functools import partial

from avatarwindow import AvatarWindow
from chatwindow import ChatWindow
from requester import Requester
from addfriendwindow import AddFriendWindow


class FriendList(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title('Tk Chat App')
        self.geometry('700x500')

        self.requester = Requester()

        self.menu = tk.Menu(self, bg='lightgrey', fg='black', tearoff=0)
        self.friends_menu = tk.Menu(self.menu, fg='black', bg='lightgrey', tearoff=0)
        self.friends_menu.add_command(label='Add Friend', command=self.show_add_friend_window)

        self.menu.add_command(label='Add Friend', command=self.add_friends)
        self.menu.add_cascade(label='Friends', menu=self.friends_menu)
        self.show_login_screen()

        self.avatar_menu = tk.Menu(self.menu, fg='black', bg='lightgrey', tearoff=0)
        self.avatar_menu.add_command(label='Change Avatar', command=self.change_avatar)

    def add_friend(self, username):
        if self.requester.add_friend(self.username, username):
            msg.showinfo('Friend Added', 'Friend Added')
            success = True
            self.reload_friends()
        else:
            msg.showerror('Add Failed', 'Friend was not found')
            success = False

        return success

    def reload_friends(self):
        for child in self.canvas_frame.winfo_children():
            child.pack_forget()
        self.load_friends()

    def show_add_friend_window(self):
        AddFriendWindow(self)

    def change_avatar(self):
        AvatarWindow(self)

    def show_friends(self):
        self.configure(menu=self.menu)
        self.login_frame.pack_forget()

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas_frame = tk.Frame(self.canvas)

        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)

        self.friends_area = self.canvas.create_window((0, 0), window=self.canvas_frame, anchor='nw')

        self.bind_events()

        self.load_friends()

    def show_login_screen(self):
        self.login_frame = ttk.Frame(self)
        username_label = ttk.Label(self.login_frame, text='Username')
        self.username_entry = ttk.Entry(self.login_frame)

        real_name_label = ttk.Label(self.login_frame, text='Real Name')
        self.real_name_entry = ttk.Entry(self.login_frame)

        login_button = ttk.Button(self.login_frame, text='Login', command=self.login)
        create_account_button = ttk.Button(self.login_frame, text='Create Account', command=self.create_account)

        username_label.grid(row=0, column=0, sticky='e')
        self.username_entry.grid(row=0, column=1)

        real_name_label.grid(row=1, column=0, sticky='e')
        self.real_name_entry.grid(row=1, column=1)

        login_button.grid(row=2, column=0, sticky='e')
        create_account_button.grid(row=2, column=1)

        for i in range(3):
            tk.Grid.rowconfigure(self.login_frame, i, weight=1)
            tk.Grid.columnconfigure(self.login_frame, i, weight=1)

        self.login_frame.pack(fill=tk.BOTH, expand=1)

    def login(self):
        username = self.username_entry.get()
        real_name = self.real_name_entry.get()

        if self.requester.login(username, real_name):
            self.username = username
            self.real_name = real_name

            self.show_friends()
        else:
            msg.showerror('Failed', f'Could not log in as {username}')

    def create_account(self):
        username = self.username_entry.get()
        real_name = self.real_name_entry.get()

        if self.requester.create_account(username, real_name):
            self.username = username
            self.real_name = real_name

            self.show_friends()
        else:
            msg.showerror('Failed', 'Account already exists')

    def bind_events(self):
        self.bind('<Configure>', self.on_frame_resized)
        self.canvas.bind('<Configure>', self.friends_width)

    def friends_width(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.friends_area, width=canvas_width)

    def on_frame_resized(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def add_friends(self):
        self.load_friends()

    def open_chat_window(self):
        cw = ChatWindow(self, 'Jarden Corebyn', 'images/avatar.png')

    def load_friends(self):
        my_friends = self.requester.get_friends(self.username)

        for user in my_friends['friends']:
            if user['username'] != self.username:
                friend_frame = ttk.Frame(self.canvas_frame)
                profile_photo = tk.PhotoImage(file='images/avatar.png')
                profile_photo_label = ttk.Label(friend_frame, image=profile_photo)
                profile_photo_label.image = profile_photo
                friend_name = ttk.Label(friend_frame, text=user['real_name'], anchor=tk.W)

                block_this_friend = partial(self.block_friend, username=user['username'])
                block_button = ttk.Button(friend_frame, text='Block', command=block_this_friend)

                message_this_friend = partial(self.open_chat_window, username=user['username'], real_name=user['real_name'])
                message_button = ttk.Button(friend_frame, text='chat', command=message_this_friend)

                profile_photo_label.pack(side=tk.LEFT)
                friend_name.pack(side=tk.LEFT)
                message_button.pack(side=tk.RIGHT)
                block_button.pack(side=tk.RIGHT, padx=(0, 30))

                friend_frame.pack(fill=tk.X, expand=1)

    def block_friend(self, username):
        self.requester.block_friends(self.username, username)
        self.reload_friends()


if __name__ == '__main__':
    obj = FriendList()
    obj.mainloop()
