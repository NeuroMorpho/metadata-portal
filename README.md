<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">Metadata Portal</h3>

  <p align="center">
     An open-source project for annotating neuronal reconstructions in neuroscience litrature.
    <br />
    <a href="http://cng-nmo-meta.orc.gmu.edu/"><strong>View online »</strong></a>
    <br />
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

To maximize impact and discovery in research, shared data should be annotated with appropriate metadata (information that provides supplementary knowledge about the associated datasets). This online metadata portal for NeuroMorpho.Org relies on state-of-the-art web technologies and is designed to incorporate novel machine learning algorithms for promoting and facilitating the systematic acquisition of descriptive information for neuronal reconstructions. This project is fully open-source and the development may also be extended to other research projects that require knowledge management.

Key features:
* Open-source
* Easy to integrate

### Built With
* [Python](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com)
* [PostgreSQL](https://www.postgresql.org/)


<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may set up the metadata portal locally to integrate it for your personal use.
Please clone or download the source code and follow these example steps.

### Prerequisites
This project requires you to have your database set up before. Once you have the credentials for the database put them in the `./metadata/settings.py` file.
* ./metadata/settings.py
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', // for example our database is PostgreSQL
        'NAME': 'ADD YOURS',
	    'USER': 'ADD YOURS',
	    'PASSWORD': 'ADD YOURS',
	    'HOST': 'ADD YOURS', 
	    'PORT': 'ADD YOURS',
    }
}
```
Or simply use sqlite:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

### Installation

1. Download and install Python and pip for your prefered operating system. (https://www.python.org/downloads/)
```sh
# ubuntu:
$ sudo apt-get update
$ sudo apt-get install python2.7
$ sudo apt-get install python-pip
```
2. It’s highly recommended to install `Virtualenv` that creates new isolated environments to isolates your Python files on a per-project basis. That will ensure that any modifications made to your project won’t affect others you’re developing. The interesting part is that you can create virtual environments with different python versions, with each environment having its own set of packages.
```sh
$ pip install virtualenv
Collecting virtualenv
  Downloading virtualenv-x.x.x-pyx.pyx-none-any.whl (1.8MB)
  100% |████████████████████████████████| 1.8MB 367kB/s
Installing collected packages: virtualenv
Successfully installed virtualenv-x.x.x
```
3. Make your virtual environment
```sh
$ python -m venv myvenv
```
4. Activate the virtual environment
```sh
$ source ./myvenv/bin/activate
>> (myvenv) $
```
5. Install the required Python packages
```sh
$ pip install -r req.txt --no-index --find-links file:///tmp/packages
```
6. obtain a secret from [MiniWebTool](https://miniwebtool.com/django-secret-key-generator/) key and add to `settings.py`
```
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'PUT/MAKE YOURS'
```
7. Migrate
```sh
$ python manage.py migrate
```
8. Create admin account and make migrations
```sh
$ python manage.py createsuperuser
#then
$ python manage.py makemigrations ig_miner_app #to makemigrations for the app
#then again run
$ python manage.py migrate #to start the development server
```
9. Run the server
```sh
$ python manage.py runserver
```
<!-- USAGE EXAMPLES -->
## Usage

The web-based implementation naturally enables its direct usage by the authors of the articles described the original datasets, namely the data contributors. Considering the dramatically improved performance of metadata annotation, we invite all researchers depositing their neuronal and glial tracings into [NeuroMorpho.Org](http://neuromorpho.org/) to utilize the portal for annotating their submission.
_For more help, please refer to the [Help Page](http://cng-nmo-meta.orc.gmu.edu/help/)_


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request (if you like)



<!-- LICENSE -->
## License
Distributed under the GPL 3.0 License.



<!-- CONTACT -->
## Contact

- Kayvan Bijari - kbijari[@]gmu[dot]edu
- NeuroMorpho.Org administration team - nmadmin[@]gmu[dot]edu
- Project Link: [Metadata Portal](http://cng-nmo-meta.orc.gmu.edu/)
- Source Link: [GitHub](https://github.com/NeuroMorpho/metadata-portal)


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [NeuroMorpho.Org](http://neuromorpho.org/)
* [Office of Research Computing](https://orc.gmu.edu/)
* [George Mason University](https://www2.gmu.edu/)


<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=flat-square
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=flat-square
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=flat-square
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=flat-square
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=flat-square
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/main.png

