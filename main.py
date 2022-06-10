
import email
from kivy.uix.screenmanager import ScreenManager, TransitionBase
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivy_garden.mapview import MapView, MapMarkerPopup, MapMarker
from kivy.utils import get_color_from_hex, platform
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import ObjectProperty
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Window
from tkinter import Button, dialog
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.metrics import dp
from turtle import color
import sqlite3

#Window/Display size
Window.size=(360,650)

class MainApp(MDApp):
    dialog = None
    def build(self):
        global sm
        self.theme_cls.primary_palette = "Orange"

        #create connection to user_data database
        con = sqlite3.connect('user_data.db')
        cur = con.cursor()

        #create database table
        cur.execute("""CREATE TABLE if not exists users(
            full_name text, bday text, email text, phone text, car text, passwd text, acct text)
        """)
        con.commit()
        con.close()

        #insert .kv files
        sm = ScreenManager()
        sm.add_widget(Builder.load_file("splash.kv"))
        sm.add_widget(Builder.load_file("login.kv"))
        sm.add_widget(Builder.load_file("forgot.kv"))
        sm.add_widget(Builder.load_file("forgot_reset.kv"))
        sm.add_widget(Builder.load_file("register.kv"))
        sm.add_widget(Builder.load_file("home.kv"))
        sm.add_widget(Builder.load_file("profile.kv"))
        sm.add_widget(Builder.load_file("settings.kv"))
        sm.add_widget(Builder.load_file("map_one.kv"))
        sm.add_widget(Builder.load_file("map_two.kv"))
        sm.add_widget(Builder.load_file("planner.kv"))
        sm.add_widget(Builder.load_file("promo.kv"))
        sm.add_widget(Builder.load_file("autoshop.kv"))
        sm.add_widget(Builder.load_file("history.kv"))
        sm.add_widget(Builder.load_file("home_business.kv"))
        return sm
    
    #timer to transition to login upon opening
    def on_start(self):
        Clock.schedule_once(self.login, 3.5)
    
    #close dialog if it exist otherwise open login
    def login(self, *args):
        if self.dialog:
            self.dialog.dismiss()
            sm.current = "login"
        else:
            sm.current = "login"

    #display register data into terminal
    def submit_reg(self):
        con = sqlite3.connect('user_data.db')
        cur = con.cursor()

        #insert data into database
        cur.execute("""INSERT INTO users (full_name, bday, email, phone, car, passwd, acct) VALUES (:first,:second,:third,:fourth,:fifth,:sixth,:seventh)""",
            {
                'first': self.root.get_screen('register').ids.full_name.text,
                'second': self.root.get_screen('register').ids.bday.text,
                'third': self.root.get_screen('register').ids.email.text,
                'fourth': self.root.get_screen('register').ids.phone.text,
                'fifth': self.root.get_screen('register').ids.car.text,
                'sixth': self.root.get_screen('register').ids.passwd.text,
                'seventh': self.root.get_screen('register').ids.acct.text,
            })
        con.commit()
        con.close()
        print("Submitted Succesfully")
        self.reg_success_dialog()
        sm.current = "login"
        sm.transition.direction = 'right'
    
    #submit login credentials
    def submit_login(self):
        con = sqlite3.connect('user_data.db')
        cur = con.cursor()

        #search login credentials from the database
        cur.execute("""SELECT * FROM users where email=? AND passwd=?""",
            (self.root.get_screen('login').ids.login_email.text, self.root.get_screen('login').ids.login_passwd.text
        ))
        row = cur.fetchone()
        if row:
            #check if the login credentials belongs to
            #a customer account or business account
            if row[6] == "Customer":
                print("login success customer")
                sm.current = "home"
                sm.transition.direction = 'left'
            elif row[6] == "Business":
                print("login success business owner")
                sm.current = "home_business"
                sm.transition.direction = 'left'
            else:
                pass
        else:
            print("login failed")
            self.root.get_screen('login').ids.login_email.text = ""
            self.root.get_screen('login').ids.login_passwd.text = ""
            self.login_incorrect_dialog()
        con.commit()
        con.close()
        self.disp_profile()
    
    #search email from the database
    def submit_forgot(self):
        global email_forg
        con = sqlite3.connect('user_data.db')
        cur = con.cursor()

        #search login credentials from the database
        cur.execute("""SELECT * FROM users where email=?""",
            (self.root.get_screen('forgot').ids.forg_email.text,))
        row = cur.fetchone()
        email_forg = row
        if row:
            sm.current = "forgot_reset"
            sm.transition.direction = 'left'
            self.root.get_screen('forgot').ids.forg_email.text = ""
        else:
            self.root.get_screen('forgot').ids.forg_email.text = ""
            self.for_no_email_dialog()
        con.commit()
        con.close()

    #reset password
    def reset_passwd(self):
        con = sqlite3.connect('user_data.db')
        cur = con.cursor()
        if self.root.get_screen('forgot_reset').ids.forg_reset_passwd.text == self.root.get_screen('forgot_reset').ids.forg_reset_cnfrm.text:
            cur.execute("""UPDATE users SET passwd=? where email=?""",
            (self.root.get_screen('forgot_reset').ids.forg_reset_passwd.text, email_forg[2],
            ))
            self.passwd_changed()
            sm.current = "login"
            sm.transition.direction = 'right'
        else:
            self.passwd_mismatch_dialog()
        con.commit()
        con.close()


    #show/hide password
    def show_pass(self, widget, shwpss):
        if widget.state == "normal":
            shwpss.password = True
        else:
            shwpss.password = False

    #register warning for incomplete data dialog
    def reg_warning_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Error!",
                text = "Complete all the missing fields.\nPlease try again",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title = "Error!",
                text = "Complete all the missing fields.\nPlease try again",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        self.dialog.open()

    #registration success dialog
    def reg_success_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Success!",
                text = "Your account has been created successfully!",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title = "Success!",
                text = "Your account has been created successfully!",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        self.dialog.open()

    #Wrong email/password dialog
    def login_incorrect_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Login Failed",
                text = "Your email or password is incorrect.\nPlease try again",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title = "Login Failed",
                text = "Your email or password is incorrect.\nPlease try again",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        self.dialog.open()
    
    #no existing email dialog
    def for_no_email_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Error!",
                text = "Email doesn't exist!",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title = "Error!",
                text = "Email doesn't exist!",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        self.dialog.open()
    
    #password not matching dialog
    def passwd_mismatch_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Error!",
                text = "Password do not match.\nPlease try again.",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title = "Error!",
                text = "Password do not match.\nPlease try again",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        self.dialog.open()
    
    #successfully change password dialog
    def passwd_changed(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Success!",
                text = "Password successfully changed!",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title = "Success!",
                text = "Password successfully changed!",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        self.dialog.open()

    #planner submitted dialog
    def planner_success_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Success!",
                text = "Planner submitted successfuly!",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title = "Success!",
                text = "Planner submitted successfuly!",
                buttons = [
                    MDFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    ]
                )
        self.dialog.open()

    #display a confirmation dialog upon log out
    def logout_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Log Out",
                text = "Are you sure you want to log out?",
                buttons = [
                    MDFlatButton(
                        text = "CANCEL", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    MDRectangleFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.login),
                    ]
                )
        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title = "Log Out",
                text = "Are you sure you want to log out?",
                buttons = [
                    MDFlatButton(
                        text = "CANCEL", text_color=self.theme_cls.primary_color
                        , on_release = self.close_dialog),
                    MDRectangleFlatButton(
                        text = "OK", text_color=self.theme_cls.primary_color
                        , on_release = self.login),
                    ]
                )
        self.dialog.open()

    #close any dialog box
    def close_dialog(self, obj):
        self.dialog.dismiss()

    #clear login text fields upon log out
    def clear_login(self):
        self.root.get_screen('login').ids.login_email.text = ""
        self.root.get_screen('login').ids.login_passwd.text = ""

    #display date_range values into MDLabel
    def date_save(self, instance, value, date_range):
        self.root.get_screen('planner').ids.first_day.text = str(date_range[0])
        self.root.get_screen('planner').ids.last_day.text = str(date_range[-1])
        self.root.get_screen('planner').ids.dur.text = (str(len(date_range)) + " Days")

    #display range date picker
    def select_date(self):
        date_dialog = MDDatePicker(mode="range")
        date_dialog.bind(on_save=self.date_save)
        date_dialog.open()

    #display information on profile screen
    def disp_profile(self):
        #cred_pass = self.root.get_screen('login').ids.login_passwd.text
        con = sqlite3.connect('user_data.db')
        cur = con.cursor()

        #search login credentials from the database
        cur.execute("""SELECT * FROM users where email=? AND passwd=?""",
            (self.root.get_screen('login').ids.login_email.text, self.root.get_screen('login').ids.login_passwd.text
        ))
        row = cur.fetchone()
        if row:
            self.root.get_screen('profile').ids.prof_name.text = row[0]
            self.root.get_screen('profile').ids.prof_bday.text = row[1]
            self.root.get_screen('profile').ids.prof_email.text = row[2]
            self.root.get_screen('profile').ids.prof_phone.text = row[3]
            self.root.get_screen('profile').ids.prof_car.text = row[4]
            self.root.get_screen('profile').ids.prof_type.text = row[6]
            self.root.get_screen('home').ids.car_model.text = row[4]
        else:
            pass
        con.commit()
        con.close()
    
    #checks if profile is customer, go to customer home elif business, go to home_business
    def decide_home(self):
        if sm.current == "profile":
            if self.root.get_screen('profile').ids.prof_type.text == "Customer":
                sm.current = "home"
            else:
                sm.current = "home_business"
        elif sm.current == "settings":
            if self.root.get_screen('profile').ids.prof_type.text == "Customer":
                sm.current = "home"
            else:
                sm.current = "home_business"
        elif sm.current == "history":
            if self.root.get_screen('profile').ids.prof_type.text == "Customer":
                sm.current = "home"
            else:
                sm.current = "home_business"
        elif sm.current == "promo":
            if self.root.get_screen('profile').ids.prof_type.text == "Customer":
                sm.current = "home"
            else:
                sm.current = "home_business"

    #get mechanic shops information from the database
    def get_market(self):
        #create connection to mech_shops database
        conmech = sqlite3.connect("mech_shops.db")
        curmech = conmech.cursor()

        #select all data from the database
        curmech.execute("""SELECT * FROM mechanic_shops""")
        mechshop = curmech.fetchall()

        #create a marker popup for every mechanical shop
        for shops in mechshop:
            mark = MapMarkerPopup(source = "images/mechanic.png",lat=shops[2], lon=shops[3])
            self.root.get_screen('map_one').ids.map.add_widget(mark)
        conmech.commit()
        conmech.close()

    #get carwash information from the database
    def get_carwash(self): 
        #create connection to carwash database
        conwash = sqlite3.connect("carwash.db")
        curwash = conwash.cursor()
        
        #select all data from the database
        curwash.execute("""SELECT * FROM carwash""")
        car_wash = curwash.fetchall()
        #create a marker popup for every carwash
        for wash in car_wash:
            mark = MapMarkerPopup(source = "images/carwash.png",lat=wash[2], lon=wash[3])
            self.root.get_screen('map_one').ids.map.add_widget(mark)
        conwash.commit()
        conwash.close()

    #get gas station information from the database
    def get_gas(self): 
        #create connection to carwash database
        congas = sqlite3.connect("gas_station.db")
        curgas = congas.cursor()
        
        #select all data from the database
        curgas.execute("""SELECT * FROM gas_station""")
        car_wash = curgas.fetchall()
        #create a marker popup for every gas station
        for wash in car_wash:
            mark = MapMarkerPopup(source = "images/gas.png",lat=wash[2], lon=wash[3])
            self.root.get_screen('map_one').ids.map.add_widget(mark)
        congas.commit()
        congas.close()

    #get hospital information from the database
    def get_hospital(self): 
        #create connection to carwash database
        conhos = sqlite3.connect("hospital.db")
        curhos = conhos.cursor()
        
        #select all data from the database
        curhos.execute("""SELECT * FROM hospitals""")
        hospitals = curhos.fetchall()
        #create a marker popup for every hospitals
        for hospital in hospitals:
            mark = MapMarkerPopup(source = "images/hospital.png",lat=hospital[2], lon=hospital[3])
            self.root.get_screen('map_one').ids.map.add_widget(mark)
        conhos.commit()
        conhos.close()

     #get towing services information from the database
    def get_tow(self): 
        #create connection to carwash database
        contow = sqlite3.connect("towing.db")
        curtow = contow.cursor()
        
        #select all data from the database
        curtow.execute("""SELECT * FROM towing""")
        towing = curtow.fetchall()
        #create a marker popup for every hospitals
        for tow in towing:
            mark = MapMarkerPopup(source = "images/towing.png",lat=tow[2], lon=tow[3])
            self.root.get_screen('map_one').ids.map.add_widget(mark)
        contow.commit()
        contow.close()

       
if __name__ == "__main__":
    MainApp().run()