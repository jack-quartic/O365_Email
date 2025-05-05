# SanGIS_Python_Emailing
 Python module that includes O365 and python-decouple to send emails with python, using Microsoft Graph and 365ww

This folder contains the following libraries:
 - O365 (email interaction with Office 365 via MSGraph)
 - python-decouple (effective separation/access of environment settings from scripts)

## Dependencies
O365 has the following dependencies:
 - requests
 - requests-oauthlib
 - beatifulsoup4
 - stringcase
 - python-dateutil
 - tzlocal
 - pytz

It also contains a custom python module that abstracts the use of O365 to authorize and send emails:
 - sendmail.py

## Background/Instructions
The O365 API has a somewhat complex method to set up your organization for emailing
through Office 365, due to the deprecation of basic auth for email by Microsoft in 2022. The
setup methodology is described in full in the PyPi docs (https://pypi.org/project/O365/#description).
You will need access to Azure Portal for your org to register an application that will enable
OAuth2.0 authentication.

Azure Portal: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

With a registered application, you'll set up and get a **client ID** and **secret** that are used
for authentication through a python script and an IDE's interactive terminal. Follow the O365 PyPi
documentation for this part. 

Once you have the client ID/secret from the registered Azure application, look at the docstring for the
**SendMail** class in **sendmail.py**. This explains what you need to do with that client info (create an .env 
file). Next - and hopefully only once - instantiate a SendMail() object in a python script, doing the following:
 - Only if you didn't put the .env file in the root of this library, specify the path to the .env file
   with the **client_info_path** parameter 
 - Set the **token_backend** (.txt file type) parameter to wherever you want to store this token file. This
   will be generated later by the SendMail.auth() method

Then call the object's .auth() method. This will prompt you (in the terminal) to follow a URL, log in and
given consent to the application, and then you're re-directed. Copy the resulting URL back into the terminal,
and hit enter. It should then tell you you're authenticated. 

Now you can use the SendMail() object in any of your scripts. You do not need to (and should not)
authenticate each time you send an email. The token that's created by the O365 API is technically 
**valid for 60 minutes**. However, once authenticated, as long as some script that calls SendMail() 
executes within **90 days** of the last execution, the O365 API automatically refreshes that auth
token. 

You can also call the .mail() method, which is a convenience method to access the MailBox class. Then
you can read your mailbox. Follow the O365 documentation for info on how to use the mailbox. 

If any of your scripts ever error when trying to send mail, it's likely that you do just need to
quick re-authenticate. Call SendMail() with the token_backend, and then the .auth() method as
previously explained.

The reason for the sendmail.py module is just to simplify calls to the O365 API in your scripts, 
by automating some of the settings that the API objects require (scopes, protocol, credentials,
account). Once authenticated, in your script you can simply call:

  *email = SendMail(client_info_path='', token_backend='')*  
  *email.messaging(Recipients list, 'Email Subject', 'Email Body', Attachment(s)*)  

Once *obj.messaging()* executes, the email is sent. 

**Protocols and Attachments
The default protocol used by SendMail() is [MSGraphProtocol](https://o365.github.io/python-o365/latest/usage/connection.html#protocols) 
as suggested by the API authors. However, it restricts emails with attachments to a size total of 4MB. If
you need to be sending emails with much larger attachments, you must do the following:
  - In your Azure app, add more delegated permissions for reading, writing, and sending emails. Follow the
    [O365 instructions](https://pypi.org/project/O365/#:~:text=AUTHENTICATION%20STEPS) for adding permissions,
    but search for **Office 365 Exchange Online API** *instead of* **Microsoft Graph**
  - Instantiate SendMail() in a script, setting parameter **prot = 1**. This will use MSOffice365Protocol instead,
    which allows for up to 150MB. You also need your Azure app to have. Also, you can either overwrite your
    current token file, or set a path to a new one, so you have a token file for each protocol
  - run the .auth() method, as described earlier. Now you can send larger attachments if you call *prot=1*
    and the new token file you created in SendMail() within your scripts.
    
If you create two token files, one for each protocol, or you're just not sure which protocol the
token you have is authorized for, you can just open the token file and check.
  - If you see https://outlook.office.com/(permission), it's MSOffice365Protocol
  - If you see https://graph.microsoft.com/(permission), it's MSGraphProtocol
