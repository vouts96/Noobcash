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
