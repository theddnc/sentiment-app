# sentiment-app

Proszę zachować spokój

## Jak to postawić?!

1. Zainstaluj pythona
2. Zainstaluj pip oraz virtualenv:
  
  ```easy-install pip```

  ```pip install virtualenv```
  
  Virtualenv to prosty skrypt, który tworzy oddzielny interpreter pythona w celu odseparowania zależności
  między projektami. 
  
3. W widocznym dla siebie miejscu utwórz środowisko wirtualne:

  ```virtualenv sentiment-app```
  
  oraz je uruchom:
  
  ```cd sentiment-app```
  ```source bin/activate```
  
  Do wyjścia ze środowiska służy komenda ```deactivate```.
  
4. Przejdź do katalogu z projektem i zaciągnij zależności:

  ```pip install -r requirements.txt```
  
5. Przeprowadź pierwszą konfigurację:

  ```python manage.py migrate``` - zmigruj bazę danych
  
6. Żeby uruchomić apkę wystarczy (będąc w virtualenv oraz w katalogu projektu):

  ```python manage.py runserver```
  
  Nawigujemy do http://localhost:8080/ i cieszymy się aplikacją bez żadnych danych. Yay.
  
## Mam pycharma professional i chciałbym go skonfigurować do debugowania django. Co teras?

1. Wejdź w preferences, wyszukaj django support.
2. Wskaż plik settings (sentiment-app/settings/dev.py).
3. Wyszukaj interpreter w preferences.
4. Dodaj interpreter pythona znajdujący się w utworzonym virtualenv - nawiguj do katalogu środowiska, wskaż bin/python. 
5. Utwórz konfigurację uruchomienia (prawy górny róg, obok zielonej ikonki play). 
6. Kliknij play. 
7. Działa.

## Świetnie, nie mam żadnych danych. Co teraz?

Baza to sqlite, więc można ją otoworzyć w czymś co umie ją otworzyć (np. pycharm umie) i wklepać dane ręcznie. 
TEORETYCZNIE powinno działać też API, ale nie testowałem. 

Jest jeszcze opcja z uruchomieniem ```python manage.py shell``` i napisaniu kawałka kodu:

```python
from api.models import *
keyword = Keyword(key="kopytko")
tweet = KeywordTweet(text="kopytko jest calkiem okej")
keyword.save()
tweet.save()
sentiment = KeywordSentiment(keyword=keyword, tweet=tweet, value=80.0)
sentiment.save()
```

Co powinno dodać słowo kluczowe "kopytko" oraz powiązaną z nim wartość sentymentu.

## Agenci

Żeby uruchomić agentów, najpierw ściągamy:
https://pypi.python.org/pypi/SPADE
rozpakowujemy, przechodzimy do katalogu i odapalamy:

```python 
configure.py 0.0.0.0
runspade.py
```

Po przejściu do katalogu agents (z aktywnym virtualenvem) uruchamiamy pythona i wpisujemy:

```python 
import nltk
nltk.download()
```

i z menu na ekranie wybieramy pakiet 'books'.

Na koniec wystarczy uruchomić twitter_crawler.py z katalogu agents i cieszyć się świeżutkimi tweetami
