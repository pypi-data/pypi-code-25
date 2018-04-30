class VVKException(Exception):
    pass


class VVKAuthException(VVKException):
    """
    Login page or OAuth2 error exception
    """
    pass


class VVKPageWarningException(VVKException):
    """
    Raises when errors were found on the page
    """
    pass


class VVKBaseUrlException(VVKException):
    """
    Raises when base url for send data was not found
    """
    pass


class VVKApiException(VVKException):
    """
    Raises when an error occurred in the response on method request
    """
    def __init__(self, vk_error_data):
        super().__init__()
        self.code = vk_error_data.get('error_code')
        self.message = vk_error_data.get('error_msg')
        self.redirect_uri = vk_error_data.get('redirect_uri')
        self.captcha_sid = vk_error_data.get('captcha_sid')
        self.captcha_url = vk_error_data.get('captcha_img')

    def __str__(self):
        return self.message
