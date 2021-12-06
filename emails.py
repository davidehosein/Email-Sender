from email.message import EmailMessage # For constructing the email messages.
import smtplib # For sending the email messages through an SMTP server.
import os # For interacting with the operating system e.g. checking if a file or directory exists, listing files in a directory etc.
import mimetypes # For determining the type and extension of a file.
from getpass import getpass # For hiding the password when the user types it in.
import sys # For exiting the program.

class Emails:
    '''Class to generate and send emails to recipients.'''
    def __init__(self, sender='', recipients=[]):
        '''Initialze the sender email address, the list of recipients and other attributes.'''
        self.sender = sender # Sender's email address
        self.recipients = recipients # List of recipients.

        self.messages = [] # List containing the email messages to be sent to the recipients.
        self.successful_recipients = [] # List to store the recipients that emails were sent to.
        self.unsuccessful_recipients = [] # List to store the recipients that emails were NOT sent to, due to some error.

        self.attachments_directory = 'attachments' # Folder name containing the attachments.

        self.smtp_server_address = 'smtp.gmail.com' # Address to Gmail SMTP server.

    def construct_emails(self):
        '''Construct the email messages for each recipient.'''
        for recipient in self.recipients: # Loops through each recipient.
            message = EmailMessage() # Creates an EmailMessage object for constructing the email.
            message['From'] = self.sender # Sets the sender email address.
            message['To'] = recipient['Email Address'] # Sets the recipient email address.
            message['Subject'] = recipient['Subject'] # Sets the subject for the recipient.
            message.set_content(recipient['Body']) # Sets the message content for the recipient.
            self.messages.append(message) # Adds the message to the messages list.

    def add_attachments(self):
        '''Adds any attachment(s) to the recipient's message.'''
        if os.path.exists(self.attachments_directory): # Checks if the attachments directory exists.
            files = os.listdir(self.attachments_directory) # List the files in the attachments directory.

            if files: # Checks if there are any files in the attachments directory.
                for message in self.messages: # Loops through each recipient message.   
                    for file in files: # Loops through each file in the attachment directory.

                        # Joins the attachment directory name and the filename to create a relative path.
                        attachment_path = os.path.join(self.attachments_directory, file) 
                        mime_type, _ = mimetypes.guess_type(attachment_path) # Guesses the file type with extension e.g. image/png
                        mime_type, mime_subtype = mime_type.split('/', 1) # Separates the file type and extension.

                        try:
                            with open(attachment_path, 'rb') as f: # Opens the file in read-binary mode, since the file may not be a text file.
                                # Attaches the file to the message.
                                message.add_attachment(f.read(), maintype=mime_type, subtype=mime_subtype, filename=file)                                     
                        except FileNotFoundError:
                            # Displays an error if the file does not exist.
                            print(f'{file} does not exist in the "{self.attachments_directory}" directory.')
            else:
                # Displays a message that there are no files in the attachments directory.
                print(f'There are no files in the "{self.attachments_directory}" directory.\n')
        else:
            # Displays a message that the attachments directory does not exist.
            print(f'The "{self.attachments_directory}" directory does not exist.\n')

    def send_emails(self):
        '''Sends the email messages to the recipients.'''
        try:    
            self.mail_server = smtplib.SMTP_SSL(self.smtp_server_address) # Creates a secure connection to the SMTP server.
            self.authenticate_server() # Authenticates to the server.

            if self.messages: # Checks if there are any recipients' messages.
                for recipient, message in zip(self.recipients, self.messages): # Loops through each recipient and their email message simulatenously.
                    name_email = f'{recipient["Name"]} <{message["To"]}>' # String containing the recipients name and email address in the format name <email>.
                    try:
                        self.mail_server.send_message(message) # Sends the message to the recipient.
                        print(f'Email sent to {message["To"]}') # Displays which recipient the email is being sent to.

                        # After sending the email, the recipient's name and their email address is added to the list of successful recipients.
                        self.successful_recipients.append(name_email) 
                    except smtplib.SMTPRecipientsRefused:
                        # Displays an error if the email was not sent to the recipient.
                        print(f'Unable to send email to {message["To"]}')

                        # If the email was NOT sent, the recipient's name and their email address is added to the list of unsuccessful recipients.
                        self.unsuccessful_recipients.append(name_email) 
                    except smtplib.SMTPSenderRefused:
                        # Displays an error if the sender email address is not able to send the email to the recipient.
                        print(f'{message["From"]} refused to send the email to {message["To"]}')

                        # If the sender was unable to send the email, the recipient's name and their email address is added to the list of unsuccessful recipients.
                        self.unsuccessful_recipients.append(name_email)             
                    except smtplib.SMTPDataError:
                        # Displays an error if the server is unable to accept the message.
                        print(f'The server is unable to accept the message for {message["To"]}')

                        # If the server is unable to accept the email message, the recipient's name and their email address is added to the list of unsuccessful recipients.
                        self.unsuccessful_recipients.append(name_email) 
                self.results() # Displays how many emails were successfully and unsuccessfully sent.
            else:
                # Displays a message if there are no emails to send.
                print('There are no emails to send.\n')

            self.mail_server.quit() # Closes the connection to the SMTP server.

        except smtplib.SMTPConnectError:
            # Displays an error if a connection was not established to the SMTP server, and then terminate the program.
            print(f'Unable to connect to {smtp_server_address}')
            print('Please ensure that the SMTP server address is valid and working.')
            print('Program terminated.\n')
            sys.exit() # Exits the program.
        except smtplib.SMTPServerDisconnected:
            # Displays an error if the SMTP server unexpectedly disconnects, and then terminate the program.
            print('The SMTP server unexpectedly disconnected :(')
            print('Program terminated.\n')
            sys.exit() # Exits the program.

    def authenticate_server(self):
        '''Gets the password for the sender's email address, and authenticates to the server.'''
        attempts = 3 # Number of attempts for entering the password for the sender's email address.

        # Displays a message to the user stating the number of attempts allowed for entering the sender email address password,
        # before the program ends.
        print(f'\nYou have {attempts} attempts to enter the password for {self.sender} before the program terminates.\n')

        while attempts > 0: # Checks if there are any attempts left.
            password = getpass(f'Enter password for {self.sender}: ') # Prompts the user for the password.
            try:
                self.mail_server.login(self.sender, password) # Authenticates with the mail server.
                # Prints a message stating that the authentication was successful.
                print(f'Successfully logged into {self.sender}\n') 
                break
            except smtplib.SMTPAuthenticationError:
                # Displays an error if the password for the sender's email address was incorrect.
                attempts -= 1 # Decrements the number of attempts by 1.

                # Displays a series of messages that the authentication failed, and to re-enter the password.
                print(f'\nUnable to log into {self.sender}')
                print('Please verify that the password is correct, and then re-enter it.')
                print(f'You have {attempts} attempts left.\n')
        else:
            # Displays that the number of attempts for entering the password has been exceeded and then terminate the program.
            print('\nYou have exceeded the number of attempts for entering the password.')
            print('Program terminated.\n')
            sys.exit() # Exits the program.

    def results(self):
        '''Displays the recipients that emails were and were NOT sent to.'''
        print(f'\nEmails sent to {len(self.successful_recipients)} recipients.') # Displays how many recipients that emails were sent to.
        for successful_recipient in self.successful_recipients: # Loops through each successful recipient.
            print(f'\t- {successful_recipient}') # Displays the name and email address of the recipient that the email were sent to.

        if self.unsuccessful_recipients: # Checks if there are any unsuccessful recipients.
            print(f'\nEmails were NOT sent to {len(self.unsuccessful_recipients)} recipients.') # Displays how many recipients that emails were NOT sent to.
            for unsuccessful_recipient in self.unsuccessful_recipients: # Loops through each unsuccessful recipient.
                print(f'\t- {unsuccessful_recipient}') # Displays the name and email address of the recipient that the email were NOT sent to.




