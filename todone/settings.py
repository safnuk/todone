from django.conf.urls import url

db_conf = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '../db.sqlite3',
    }
}

DATABASES = db_conf
INSTALLED_APPS = ( 'todos.db', 'functional_tests', )
ROOT_URLCONF = __name__
SECRET_KEY = 'sdlfjh3r98ydsuh(^^*&q3kfeuvsdb)%%%dsfw8v' 

urlpatterns = (
    url(r'^$', lambda x: x),
)
