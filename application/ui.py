import tkinter as tk
from tkinter import TkVersion, PhotoImage, Tk, messagebox, Canvas
from PIL import ImageTk, Image  
import sys, os, platform
#import tkFont

#LARGE_FONT = ("Verdana", 12)
TRUE_FONT = "Arial"
assetdir = os.path.join(os.path.dirname(__file__), 'assets')

# Utility functions
def _log_in():
    raise NotImplementedError
    
def _clear_entry(username_entry, pw_entry, pw_confirm_entry):
    raise NotImplementedError

def _combine_funcs(*funcs):
    def _combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return _combined_func
    
def _quit():  
    #if messagebox.askokcancel("Quit", "Do you want to quit?"):
    application_process.quit()

# highlight on hover
class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.defaultForeground = self["foreground"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']
        self['foreground'] = self['activeforeground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
        self['foreground'] = self.defaultForeground

class NoodlePasswordVault(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self, "Noodle Password Vault")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for F in (StartPage, InsidePage, ForgotPassword, SignUp):
        
            frame = F(container, self)
        
            self.frames[F] = frame
        
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]   
        frame.tkraise()
    
    
class StartPage(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        # set background color
        self.config(bg='#FFFFFF')
        
        # import logo 
        iconfile = os.path.join(assetdir, 'black_noodles_black.png')
        image = Image.open(iconfile)
        logo_resized = image.resize((200, 200), Image.ANTIALIAS)     
        img = ImageTk.PhotoImage(logo_resized)
        logo = tk.Label(self, image=img, background = '#FFFFFF')
        logo.image = img # prevent garbage collection
        logo.pack()
        
        # import entryline image
        entryline_file = os.path.join(assetdir, 'entryline.png')
        entryline_image = Image.open(entryline_file)
        entryline_resized = entryline_image.resize((250, 26), Image.ANTIALIAS)
        entryline_final = ImageTk.PhotoImage(entryline_resized)
        
        # username entry
        username_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        username_entryline.image = entryline_final
        username_entryline.pack()
        username_entry = tk.Entry(self, width=40, borderwidth=0, background='#FFFFFF', foreground='#757575', insertbackground='#757575')
        username_entry.pack()
        username_text = tk.Label(self, text="Username", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        username_text.pack()
        
        # password entry
        pw_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_entryline.image = entryline_final
        pw_entryline.pack()
        pw_entry = tk.Entry(self, borderwidth=0, show="◕", width=40, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        pw_entry.pack()
        pw_text = tk.Label(self, text="Password", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        pw_text.pack()
        
        # forgot password button
        forgot_pw_button = HoverButton(self, text="Forgot Password?", padx=10, pady=10, command=lambda: controller.show_frame(ForgotPassword), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', borderwidth=0)
        forgot_pw_button.pack()
        
        # login button
        log_in_button_path = os.path.join(assetdir, 'log_in.png')
        log_in_button_image = Image.open(log_in_button_path)
        log_in_button_resized = log_in_button_image.resize((250, 47), Image.ANTIALIAS)
        log_in_button_final = ImageTk.PhotoImage(log_in_button_resized)
        log_in_button = tk.Button(self, image=log_in_button_final, padx=20, pady=10, borderwidth=0, background='#FFFFFF', command=_log_in)
        log_in_button.image = log_in_button_final # prevent garbage collection
        log_in_button.pack()

        # signup button
        sign_up_button_path = os.path.join(assetdir, 'sign_up_home_page.png')
        sign_up_button_image = Image.open(sign_up_button_path)
        sign_up_button_resized = sign_up_button_image.resize((250, 47), Image.ANTIALIAS)
        sign_up_button_final = ImageTk.PhotoImage(sign_up_button_resized)
        sign_up_button = tk.Button(self, image=sign_up_button_final, padx=10, pady=10, command=lambda: controller.show_frame(SignUp), background='#FFFFFF', borderwidth=0)
        sign_up_button.image = sign_up_button_final # prevent garbage collection
        sign_up_button.pack()

        # page transition testing
        new_page_button = HoverButton(self, text="Load next page", command=lambda: controller.show_frame(InsidePage), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', borderwidth=0)
        #new_page_button.pack()
        
        # placement       
        logo.place(x=300, y=10)
        
        username_text.place(x=277, y=220)
        username_entry.place(x=277, y=240)
        username_entryline.place(x=272, y=230)
        
        pw_text.place(x=277, y=265)
        pw_entry.place(x=277, y=285)
        pw_entryline.place(x=272, y=275)
        
        log_in_button.place(x=273, y=320)
        
        sign_up_button.place(x=273, y=365)
        
        forgot_pw_button.place(x=343, y=410)

        #new_page_button.place(x=355, y=450)


class InsidePage(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        self.web_column_title = tk.Label(self, text="Website", background='#23272A', foreground='#99AAB5')
        buttons = []
        for i in range(6):
            buttons.append(tk.Button(self, text="Button %s" % (i+1,), background='#2C2F33', foreground='#99AAB5'))
        other1 = tk.Label(self, text="Password Info")
        main = tk.Frame(self, background='#2C2F33') 
        self.config(bg='#2C2F33')
        
        self.web_column_title.grid(row=0, column=0, rowspan=2, sticky="nsew")
        other1.grid(row=0, column=1, columnspan=2, sticky="nsew")
        buttons[0].grid(row=2, column=0, sticky="nsew")
        buttons[1].grid(row=3, column=0, sticky="nsew")
        buttons[2].grid(row=4, column=0, sticky="nsew")
        buttons[3].grid(row=5, column=0, sticky="nsew")
        buttons[4].grid(row=6, column=0, sticky="nsew")
        buttons[5].grid(row=7, column=0, sticky="nsew")
        main.grid(row=2, column=2, columnspan=2, rowspan=6)

        for row in range(8):
            self.grid_rowconfigure(row, weight=1)
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)
        
        self.back_page_button = tk.Button(self, text="Go back to original", 
                                    command=lambda: controller.show_frame(StartPage))
        
        self.back_page_button.grid(row=8, column=2)


class ForgotPassword(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        forgot_pw_title = tk.Label(self, text="Forgot Password?", font=(TRUE_FONT, 50))

        username_text = tk.Label(self, text="Username: ", font=(TRUE_FONT, 16))
        username_entry = tk.Entry(self, width=35, borderwidth=5)

        username_confirm = tk.Label(self, text="Confirm Username: ", font=(TRUE_FONT, 16))
        username_confirm_entry = tk.Entry(self, width=35, borderwidth=5)

        submit_button = tk.Button(self, text="Submit", padx=40, pady=20, 
                                  command=_log_in)
        
        back_button = tk.Button(self, text="Nvm", padx=10, pady=10,
                                    command=lambda: controller.show_frame(StartPage))
        
        
        #placing
        forgot_pw_title.grid(row=0, column=0, columnspan = 3)

        username_text.grid(row=1, column=0)
        username_entry.grid(row=1, column=1, pady=10)
        
        username_confirm.grid(row=2, column=0)
        username_confirm_entry.grid(row=2, column=1, pady=10)
        
        submit_button.grid(row=3, column=1)
        
        back_button.grid(row=4, column=1)


class SignUp(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        # set background color
        self.config(bg='#FFFFFF')
        
        # import logo 
        iconfile = os.path.join(assetdir, 'black_noodles_black.png')
        image = Image.open(iconfile)
        logo_resized = image.resize((100, 100), Image.ANTIALIAS)     
        img = ImageTk.PhotoImage(logo_resized)
        logo = tk.Label(self, image=img, background = '#FFFFFF')
        logo.image = img # prevent garbage collection
        logo.pack()
        
        # banner
        banner_file = os.path.join(assetdir, 'sign_up_banner.png')
        banner_image = Image.open(banner_file)
        banner_resized = banner_image.resize((543, 540), Image.ANTIALIAS)
        banner_final = ImageTk.PhotoImage(banner_resized)
        banner = tk.Canvas(self, width=1024, height=540, background = '#000000')
        banner.create_image(0, 0, image=banner_final, anchor=tk.NW)
        banner.image = banner_final
        banner.create_text(200, 150, fill='#FFFFFF', font=(TRUE_FONT, 18, "bold"), text="Protect Yourself. \nSecure your future.")
        banner.create_text(205, 210, fill='#FFFFFF', font=(TRUE_FONT, 8), text="Insert here some inspirational text about \nwhy its a good idea to protect your passwords.")
        banner.pack()
        
        # sign up button
        sign_up_button_path = os.path.join(assetdir, 'get_started.png')
        sign_up_button_image = Image.open(sign_up_button_path)
        sign_up_button_resized = sign_up_button_image.resize((250, 47), Image.ANTIALIAS)
        sign_up_button_final = ImageTk.PhotoImage(sign_up_button_resized)
        sign_up_button = tk.Button(self, image=sign_up_button_final, padx=10, pady=10, command=_log_in, background='#FFFFFF', borderwidth=0)
        sign_up_button.image = sign_up_button_final # prevent garbage collection
        sign_up_button.pack()
        
        # title and subtitle
        title = tk.Label(self, text="Black Noodle Password Vault", font=(TRUE_FONT, 16), foreground='#000000', background='#FFFFFF')
        subtitle = tk.Label(self, text="Create an account", font=(TRUE_FONT, 8), foreground='#757575', background='#FFFFFF')
        
        # import entryline image
        entryline_file = os.path.join(assetdir, 'entryline.png')
        entryline_image = Image.open(entryline_file)
        entryline_resized = entryline_image.resize((250, 26), Image.ANTIALIAS)
        entryline_final = ImageTk.PhotoImage(entryline_resized)
        
        # username entry
        username_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        username_entryline.image = entryline_final
        username_entryline.pack()
        username_entry = tk.Entry(self, width=40, borderwidth=0, background='#FFFFFF', foreground='#757575', insertbackground='#757575')
        username_entry.pack()
        username_text = tk.Label(self, text="Username", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        username_text.pack()
        
        # password entry
        pw_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_entryline.image = entryline_final
        pw_entryline.pack()
        pw_entry = tk.Entry(self, borderwidth=0, show="◕", width=40, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        pw_entry.pack()
        pw_text = tk.Label(self, text="Password", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        pw_text.pack()
        
        # confirmation entry
        pw_confirm_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_confirm_entryline.image = entryline_final
        pw_confirm_entryline.pack()
        pw_confirm_entry = tk.Entry(self, borderwidth=0, show="◕", width=40, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        pw_confirm_entry.pack()
        pw_confirm_text = tk.Label(self, text="Confirm Password", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        pw_confirm_text.pack()
        
        # log in text
        back_button = HoverButton(self, text="Log in.", font=(TRUE_FONT, 8, "bold"), command=lambda: _combine_funcs(controller.show_frame(StartPage), _clear_entry(username_entry, pw_entry, pw_confirm_entry)), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', borderwidth=0)
        log_in_text = tk.Label(self, text="Already have an account?", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        
        #placing
        logo.place(x=145, y=30)
        
        banner.place(x=400)
        
        title.place(x=55, y=130)
        subtitle.place(x=145, y=160)
        
        username_text.place(x=75, y=200)
        username_entry.place(x=77, y=220)
        username_entryline.place(x=70, y=210)
        
        pw_text.place(x=75, y=250)
        pw_entry.place(x=77, y=270)
        pw_entryline.place(x=70, y=260)
        
        pw_confirm_text.place(x=75, y=300)
        pw_confirm_entry.place(x=77, y=320)
        pw_confirm_entryline.place(x=70, y=310)
        
        sign_up_button.place(x=70, y=370)
        
        back_button.place(x=235, y=430)
        log_in_text.place(x=105, y=430)


if __name__ == "__main__":
    application_process = NoodlePasswordVault()
    
    # set icon
    if platform.system() == 'Windows':
        iconfile = os.path.join(assetdir, 'black_noodles_white_Xbg_icon.ico')
        application_process.wm_iconbitmap(default=iconfile)
    else:
        ext = '.png' if tk.TkVersion >= 8.6 else '.gif'
        iconfiles = [os.path.join(assetdir, 'black_noodles_white_Xbg_icon%s' % (ext))]
        icons = [tk.PhotoImage(master=application_process, file=iconfile) for iconfile in iconfiles]
        application_process.wm_iconphoto(True, *icons)

    # set window size
    application_process.geometry("800x500+0+0")
    application_process.resizable(False, False)
    
    application_process.protocol("WM_DELETE_WINDOW", _quit)
    application_process.mainloop()