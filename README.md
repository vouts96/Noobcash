# Noobcash


Instructions for installation:

	pip3 install pipenv
	
	or
	
	pip install pipenv 
	
based on your python versions. We prefer python3

Inside the noobcash directory run:

	pipenv install Flask

	pipenv install requests

	pipenv install rsa

	pipenv install llist
	
Activate the virtual env by running:
	
	pipenv shell

In order to run the server for a node run:

	python node.py
	
For a new node open a new terminal in the Noobcash dir,
activate the env by running:
	
	pipenv shell
	
and start a new node server also by running:

	python node.py

## Virtual Machines Setup
### Machine 1:
    Hostname: master
    Password: master
    Public IP: 83.212.80.50
    Local IP: 192.168.0.1

### Machine 2:
    Hostname: slave1
    Password: slave1
    Local IP: 192.168.0.2

### Machine 3:
    Hostname: slave2
    Password: slave2
    Local IP: 192.168.0.3

### Machine 4:
    Hostname: slave3
    Password: slave3
    Local IP: 192.168.0.4

### Machine 5:
    Hostname: slave4
    Password: slave4
    Local IP: 192.168.0.5
    