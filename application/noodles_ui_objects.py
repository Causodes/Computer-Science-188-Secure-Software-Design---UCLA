import tkinter as tk
from tkinter import ttk

#LARGE_FONT = ("Verdana", 12)

class NoodlePassword(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        #tk.Tk.iconbitmap(self, default="")
        
        tk.Tk.wm_title(self, "Noodle Password Vault")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for F in (StartPage, InsidePage):
        
            frame = F(container, self)
        
            self.frames[F] = frame
        
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)
        
    def show_frame(self, cont):
        
        frame = self.frames[cont]
        frame.tkraise()

#functions for the buttons
def log_in():
    return
    
def sign_up():
    return
    
def forgot_pw():
    return

class StartPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        #label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        #label.pack(pady=10, padx=10)
        
        name_shown = tk.Label(self, text="Noodle Password Vault", font=("Helvetica", 50))

        username_text = tk.Label(self, text="Username: ", font=("Helvetica", 16))
        username_entry = tk.Entry(self, width=35, borderwidth=5)

        pw_text = tk.Label(self, text="Password: ", font=("Helvetica", 16))
        pw_entry = tk.Entry(self, show="*", width=35, borderwidth=5) #show="*" changes input to *

        log_in_button = tk.Button(self, text="Log in", padx=40, pady=20, 
                                  command=log_in)

        sign_up_button = tk.Button(self, text="Sign Up", padx=10, pady=10, 
                                   command=sign_up)

        forgot_pw_button = tk.Button(self, text="Forgot Password?", padx=10, pady=10, 
                                     command=forgot_pw)

        #testing for multiple pages
        new_page_button = tk.Button(self, text="Load next page", 
                                    command=lambda: controller.show_frame(InsidePage))

        #placing
        name_shown.grid(row=0, column=0, columnspan = 3)

        username_text.grid(row=1, column=0)
        username_entry.grid(row=1, column=1, pady=10)
        
        pw_text.grid(row=2, column=0)
        pw_entry.grid(row=2, column=1, pady=10)
        
        log_in_button.grid(row=3, column=1)
        
        sign_up_button.grid(row=4, column=1)
        
        forgot_pw_button.grid(row=5, column=1)
        
        new_page_button.grid(row=6, column=1)
        
        
class InsidePage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        back_page_button = tk.Button(self, text="Go back to original", 
                                    command=lambda: controller.show_frame(StartPage))
        
        back_page_button.pack()
        
app = NoodlePassword()
app.mainloop()
        