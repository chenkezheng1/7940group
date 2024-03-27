# COMP7940 Group Project -- Telegram Chatbot

we developed a chatbot based on the Telegram platform, aiming to provide better hiking routes services for travelers. In addition, for those who prefer to stay at home, they can also browse TV shows through our chatbot. With the relevant cloud technologies, we have created a practical, scalable and secure application that ensures users easy to  gain the information they need. 

## Prerequisites

- python 3.8
- telegram
- configparser==5.3.0
- redis==4.5.4
- python-telegram-bot==13.7
- requests==2.28.2
- beautifulsoup4==4.12.0
- google-api-python-client==2.21.0


## Usage
1. Start the Telegram:
   ```
    python chatbot.py
    ```
2. Access the chatbot in Telegram


## Features
The chatbot has the following functionalities:

- Use '/' to trigger special commands
  - it has two defined commans '/hiking' and '/tvshow', enterying this two commans to trigger the special features
  - '/hiking': 1.chatbot will Give a hiking route and picture
               2.Users share a picture with caption to the chatbot
               
    '/tvshow': Reading a TV Show and user write a review 

  - undefined commands such as /hi will default to /welcome.

- Chat with chatGPT
    
## Cloud Technologies
- Redis database
- GitHub
- GitHub Action
- Docker
- Render
- ChatGPT API
