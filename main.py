import email
import sys
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    """Utility class to strip HTML tags and convert HTML to plain text."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)

def strip_html(html):
    """Strip HTML tags from a string and return plain text."""
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def decode_part(part):
    """Decode the body of the email part with appropriate encoding."""
    charset = part.get_content_charset(failobj='utf-8')
    payload = part.get_payload(decode=True)

    if charset == 'iso-2022-jp':
        return payload.decode('iso-2022-jp', errors='replace')
    else:
        try:
            return payload.decode(charset)
        except UnicodeDecodeError:
            # Fallback to iso-2022-jp if other decodings fail
            return payload.decode('iso-2022-jp', errors='replace')

def parse_email(file_path):
    """Parse and display various components of an email file."""
    try:
        with open(file_path, 'rb') as file:
            # Read the file and parse the email content
            msg = email.message_from_bytes(file.read())

            # Initialize a dictionary to store the email components
            email_details = {}

            # Extracting headers
            for header in ['From', 'To', 'Subject', 'Date']:
                email_details[header] = msg.get(header)

            # Extracting body
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain' or content_type == 'text/html':
                        email_details['Body'] = decode_part(part)
                        break
            else:
                email_details['Body'] = decode_part(msg)

            return email_details
    except FileNotFoundError:
        return "File not found: {}".format(file_path)
    except Exception as e:
        return "An error occurred: {}".format(e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <email_file>")
    else:
        file_path = sys.argv[1]
        email_content = parse_email(file_path)
        for key, value in email_content.items():
            print(f"{key}: {value}")
