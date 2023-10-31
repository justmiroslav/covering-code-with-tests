Commands to deploy fastAPI project on a public server using nginx:
1 - ssh root@domain.name
2 - enter password {generated in D.O}
3 - sudo apt update
optional - sudo apt upgrade
4 - sudo apt install -y python3-pip python3-venv nginx
5 - sudo vim /etc/nginx/sites-available/fastapi_project
6 - *
optional - sudo rm -r /etc/nginx/sites-enabled/fastapi_project
7 - sudo ln -s /etc/nginx/sites-available/fastapi_project /etc/nginx/sites-enabled/
8 - sudo nginx -t
9 - sudo systemctl restart nginx
10 - git clone https kink to the project
11 - cd name-of-your-project
12 - python3 -m venv venv
13 - source venv/bin/activate
14 - pip install fastapi uvicorn
15 - pip install -r requirements.txt - if present
16 - nano fastapi_project.service
17 - #
18 - sudo cp fastapi_project.service /etc/systemd/system/
19 - sudo systemctl daemon-reload
20 - sudo systemctl enable fastapi_project
21 - sudo systemctl start fastapi_project
22 - sudo systemctl status fastapi_project

*
server {
    listen 80;
    server_name domain.name;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

#
[Unit]
Description=FastAPI Project

[Service]
User=root
WorkingDirectory=path/to/the/project
ExecStart=path/to/the/project/venv/bin/uvicorn file_name:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
