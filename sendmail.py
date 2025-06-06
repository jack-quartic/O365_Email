import os
from sangis_email.decouple import config
from sangis_email.O365 import Account, MSGraphProtocol, MSOffice365Protocol, FileSystemTokenBackend
from sangis_email.O365.mailbox import MailBox

class SendMail:
    
    """ Description: uses O365 and python-decouple to access secured Microsoft 
        resources to read, write, and send emails with Microsoft Graph, via a
        registered application on your organization's Azure cloud.
        For the first use of this module, you'll need a client id and secret from
        the Azure application you've registered (application CLIENT_ID and the VALUE
        parameter from the secret created within the application). 
        
        When you get these, create an .env file wherever you'd like, and use the format:
        - CLIENT_ID=IDSTRING
        - CLIENT_SECRET=SECRETSTRING

        This .env file can be put anywhere you like, but you'll need to specify the path
        when instantiating the class if you put it anywhere but the root directory of 
        this module.

        Once you have the .env file, create an instance of the class, then run the auth()
        method. It will ask you to follow a URL, login, and copy the re-direct URL back 
        to the terminal. Then you are authenticated may use the other parts of this module,
        for as long as the token file is valid.  
    """
    
    def __init__(self, client_info_path=None, token_backend=None, prot=None):
        
        # import os
        # from sangis_email.O365 import Account, Connection, Message, MSGraphProtocol, FileSystemTokenBackend
        # from decouple import config

        """ Parameters:
              - client_info_path (str, Optional): the .env file where the credentials are 
                stored for accessing the secure Azure application. If left blank, instantiation
                will search the root folder of this module for the .env file
              - token_backend (str, Optional): the location of token file generated by the
                authentication. This is both where you want it stored, and where it is pulled from
                when token_backend is specified. 
              - prot(int): Default is none, which uses MSGraphProtocol. If needing to send emails
                with attachments larger than 4MB, specify 1 for this parameter
        """
        self.path = client_info_path
        self.scopes = ['basic', 'message_all', 'message_all_shared']
        self.protocol = MSOffice365Protocol(api_version='v2.0') if prot else MSGraphProtocol(api_version='beta')
        self.token = FileSystemTokenBackend(os.path.dirname(token_backend), os.path.basename(token_backend))
        
        # .env file doesn't need to be in the same directory as the module, but if it's not
        #  the user needs to specify the location to search for it
        if not self.path:
            self.credentials = (config('CLIENT_ID', default=''), config("CLIENT_SECRET", default=''))  
        else:
            config.search_path = self.path
            self.credentials = (config('CLIENT_ID', default=''), config("CLIENT_SECRET", default=''))
        
        self.acct = Account(credentials=self.credentials, protocol=self.protocol, token_backend=self.token)


    def auth(self):

        """ This method uses O365 Account.authentication method to authenticate the 
            application and allow use of the messaging method below. It uses data 
            passed during instantiation. It will require you to follow a URL, log
            in and pass back to the console a redirect URI
        """

        account = self.acct
        if account.authenticate(scopes=self.scopes):
            print("You are now authenticated, and can read/write/send emails")

    # Allows interaction with mailbox for the user owning registered Azure app  
    def mail(self):
        return MailBox(con=self.acct.connection, protocol=self.protocol)

    def messaging(self, email_to:list, subject:str, body:str, attach=None):
        
        """ This method utilizes the O365 Message class to set and send messages. It
            will first check for authentication, as it's required before emails can be
            sent. 
            
            Parameters:
              - email_to (list): list of recipients
              - subject (str): the subject of the email
              - body (str): contents of the email. This can be an html-formatted string, too
              - attach(list of str, bytes, path): any attachment. O365 supports in-memory
                objects, like BytesIO. If using in-memory object, attach should be a tuple
                of (object, file name w/ ext) 
        """

        try:
            # Check to see that authorization has occurred
            if not self.acct.is_authenticated:
                raise RuntimeError("""Not Authenticated yet. Please use auth() method first. \n 
                         Authentication must occurr before email capabilities are enabled""")
            
            # Method of Account class that creates a Message() object
            message = self.acct.new_message()

            # Conditionally add an attachment (must be < 4MB, w/ MSGraph Protocol)
            if attach:
                message.attachments.add([attach])

            message.to.add(email_to)
            message.subject = subject
            message.body = body
            message.send()

        except RuntimeError as re:
            print(re)
             