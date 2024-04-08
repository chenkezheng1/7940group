From python
WORKDIR /APP
COPY . /APP
RUN pip install update
RUN pip install -r requirements.txt

ENV TLG_ACCESS_TOKEN = 6761320624:AAGQB0_Zg5XUESDfhQaZHDzJ_TtjFsIm7XQ
ENV BASICURL = https://chatgpt.hkbu.edu.hk/general/rest
ENV MODELNAME = gpt-35-turbo
ENV APIVERSION = 2024-02-15-preview
ENV GPT_ACCESS_TOKEN = 15fde8b4-20ca-4a24-998b-68612c132b46

