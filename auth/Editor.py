__author__ = 'helloworld'

import Authenticator
import Authorizor

# set up a test user and permission
Authenticator.authenticator.add_user("joe","joepassword")
Authorizor.authorizor.add_permission("test program")
Authorizor.authorizor.add_permission("change program")
Authorizor.authorizor.permit_user("test program","joe")

class Editor:

    def __init__(self):
        self.username = None
        self.menu_map = {
            "login": self.login,
            "test":self.test,
            "change":self.change,
            "quit":self.quit
        }

    def login(self):
        logged_in = False
        while not logged_in:
            username = input("username: ")
            password = input("password: ")
            try:
                logged_in = Authenticator.authenticator.login(username,password)
            except Authenticator.InvalidUsername:
                print "Sorry, that username does not exist"
            except Authenticator.InvalidPassword:
                print "Sorry, incorrect password"
            else:
                self.username = username

    def is_permitted(self, permission):
        try:
            Authorizor.authorizor.check_permission(permission,self.username)
        except Authorizor.NotLoginError as e:
            print "{} is not logged in ".format(e.username)
            return False
        except Authorizor.NotPermittedError as e:
            print "{} cannot {}".format(e.username,permission)
            return False
        else:
            return True

    def test(self):
        if self.is_permitted("test program"):
            print "testing program now..."

    def change(self):
        if self.is_permitted("change program"):
            print "changing program now..."

    def quit(self):
        raise SystemExit()

    def menu(self):
        try:
            answer = ""
            while True:
                print """Please enter a command:
                \tlogin\tLogin
                \ttest\tTest the program
                \tchange\tChange the program
                \tquit\tQuit
                """
                answer = input("enter a command: ").lower()
                try:
                    func = self.menu_map[answer]
                except KeyError:
                    print "{} is not a valid option".format(answer)
                else:
                    func()
        finally:
            print "Thank you for testing the auth module"

Editor().menu()


