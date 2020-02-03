from tkinter import *
from PIL import ImageTk, Image


window = Tk()
window.title("Noodles Password Vault")

#style for buttons?
style = Style() 
style.configure('TButton', font = ('calibri', 20, 'bold'))


#functions for the buttons
def log_in():
    return

def sign_up():
    return

def forgot_pw():
    return


#creating widgets
name_shown = Label(window, text="Noodle Password Vault", font=("Helvetica", 50))

username_text = Label(window, text="Username: ", font=("Helvetica", 16))
username_entry = Entry(window, width=35, borderwidth=5)

pw_text = Label(window, text="Password: ", font=("Helvetica", 16))
pw_entry = Entry(window, show="*", width=35, borderwidth=5) #show="*" changes input to *

log_in_button = Button(window, text="Log in", padx=40, pady=20, command=log_in)

sign_up_button = Button(window, text="Sign Up", padx=10, pady=10, command=sign_up)

forgot_pw_button = Button(window, text="Forgot Password?", padx=10, pady=10, command=forgot_pw)


#placing
name_shown.grid(row=0, column=0, columnspan = 3)

username_text.grid(row=1, column=0)
username_entry.grid(row=1, column=1, pady=10)

pw_text.grid(row=2, column=0)
pw_entry.grid(row=2, column=1, pady=10)

log_in_button.grid(row=3, column=1)

sign_up_button.grid(row=4, column=1)

forgot_pw_button.grid(row=5, column=1)


window.mainloop()