class Conf():


    @classmethod
    def setup(cls,settings):
        cls.adminname   =settings.get("ppss_auth.adminname","admin")
        cls.adminpass   =settings.get("ppss_auth.adminpass","")
        cls.initdb = settings.get("ppss_auth.initdb","true").lower() == 'true'

        cls.logoutroute = settings.get("ppss_auth.post_logout_route","home")
        cls.postloginroute = settings.get("ppss_auth.post_login_route","home")
        cls.postloginfollow = settings.get("ppss_auth.post_login_follow","true").lower() == 'true'
        cls.saltforhash = settings.get("ppss_auth.salt","ImTheSaltOfThisLife")
        cls.logintemplate = settings.get("ppss_auth.logintemplate","ppss_auth:/templates/login.mako")
        cls.logintemplateinherit = settings.get("ppss_auth.logintemplateinherit","ppss_auth:/templates/layout.mako")
        cls.changepasswordtemplate = settings.get("ppss_auth.changepasswordtemplate","ppss_auth:/templates/change.mako")
        cls.modifyusertemplate = settings.get("ppss_auth.modifyusertemplate","ppss_auth:/templates/modifyuser.mako")
        cls.listusertemplate = settings.get("ppss_auth.listusertemplate","ppss_auth:/templates/listuser.mako")
        

        

        