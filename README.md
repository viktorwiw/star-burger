# Сайт доставки еды Star Burger

Это сайт сети ресторанов [Star Burger](https://starbulka.ru). Здесь можно заказать превосходные бургеры с доставкой на дом.

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

Для логирования в проекте использован сервис [Rollbar](https://rollbar.com/).

Проект полностью контейнеризированный (Django + PostgreSQL + Nginx + Node/Parcel) с поддержкой HTTPS (Let's Encrypt) и автообновлением сертификатов.


## Как запустить dev-версию сайта без Docker

Для запуска сайта нужно запустить **одновременно** бэкенд и фронтенд, в двух терминалах.

### Установка СУБД Postgres и создание БД

Установите Postgress

```
sudo apt-get update
sudo apt-get install libpq-dev postgresql postgresql-contrib
```

Создайте БД

```
sudo passwd postgres
sudo su - postgres
psql
CREATE DATABASE star_burger;
CREATE USER myprojectuser WITH PASSWORD 'password';
ALTER ROLE myprojectuser WITH LOGIN;
GRANT ALL PRIVILEGES ON DATABASE "star_burger" TO myprojectuser;
ALTER USER myprojectuser CREATEDB;
\c star_burger
GRANT ALL ON schema public TO myprojectuser;
\q
exit
```

``myprojectuser`` - имя вашего пользователя для БД


### Как собрать бэкенд

Скачайте код:
```sh
git clone https://github.com/devmanorg/star-burger.git
```

Перейдите в каталог проекта:
```sh
cd star-burger
```

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть 3.10.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`


Установите зависимости в виртуальное окружение:
```sh
pip install -r requirements.txt
```

Определите переменные окружения. Создать файл `.env` в каталоге `star_burger/` и положите туда такой код:
```bash
SECRET_KEY=django-key-random
GEO_API_KEY=ВАШ YANDEX_API_KEY
DB_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
```
``GEO_API_KEY`` - [см. документацию API Яндекс Карт](https://yandex.ru/dev/commercial/doc/ru/concepts/jsapi-geocoder#how-to-use)

Если необходим Rollbar, добавьте в `.env` - ``ROLLBAR_TOKEN``
``ROLLBAR_TOKEN`` - [см. документацию к сервису Rollbar](https://docs.rollbar.com/docs/access-tokens)

в ``DB_URL``

```
NAME - имя БД,
USER - логин,
PASSWORD - пароль юзера,
НOST - localhost,
PORT - порт по умолчанию - 5432,
```

Отмигрируйте  БД следующей командой:

```sh
python manage.py migrate
```

Запустите сервер:

```sh
python manage.py runserver
```

Откройте сайт в браузере по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Если вы увидели пустую белую страницу, то не пугайтесь, выдохните. Просто фронтенд пока ещё не собран. Переходите к следующему разделу README.


### Как собрать фронтенд

**Откройте новый терминал**. Для работы сайта в dev-режиме необходима одновременная работа сразу двух программ `runserver` и `parcel`. Каждая требует себе отдельного терминала. Чтобы не выключать `runserver` откройте для фронтенда новый терминал и все нижеследующие инструкции выполняйте там.

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

Проверьте, что Node.js и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```sh
nodejs --version
# v16.16.0
# Если ошибка, попробуйте node:
node --version
# v16.16.0

npm --version
# 8.11.0
```

Версия `nodejs` должна быть не младше `10.0` и не старше `16.*`. Лучше ставьте `16.16.0`, её мы тестировали. Версия `npm` не важна. Как обновить Node.js читайте в статье: [How to Update Node.js](https://phoenixnap.com/kb/update-node-js-version).

Перейдите в каталог проекта и установите пакеты Node.js:

```sh
cd star-burger
npm ci --include=dev
```

Команда `npm ci` создаст каталог `node_modules` и установит туда пакеты Node.js. Получится аналог виртуального окружения как для Python, но для Node.js.

Помимо прочего будет установлен [Parcel](https://parceljs.org/) — это упаковщик веб-приложений, похожий на [Webpack](https://webpack.js.org/). В отличии от Webpack он прост в использовании и совсем не требует настроек.

Теперь запустите сборку фронтенда и не выключайте. Parcel будет работать в фоне и следить за изменениями в JS-коде:

```sh
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Если вы на Windows, то вам нужна та же команда, только с другими слешами в путях:

```sh
.\node_modules\.bin\parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Дождитесь завершения первичной сборки. Это вполне может занять 10 и более секунд. О готовности вы узнаете по сообщению в консоли:

```
✨  Built in 10.89s
```

Parcel будет следить за файлами в каталоге `bundles-src`. Сначала он прочитает содержимое `index.js` и узнает какие другие файлы он импортирует. Затем Parcel перейдёт в каждый из этих подключенных файлов и узнает что импортируют они. И так далее, пока не закончатся файлы. В итоге Parcel получит полный список зависимостей. Дальше он соберёт все эти сотни мелких файлов в большие бандлы `bundles/index.js` и `bundles/index.css`. Они полностью самодостаточны, и потому пригодны для запуска в браузере. Именно эти бандлы сервер отправит клиенту.

Теперь если зайти на страницу  [http://127.0.0.1:8000/](http://127.0.0.1:8000/), то вместо пустой страницы вы увидите:

![](https://dvmn.org/filer/canonical/1594651900/687/)

Каталог `bundles` в репозитории особенный — туда Parcel складывает результаты своей работы. Эта директория предназначена исключительно для результатов сборки фронтенда и потому исключёна из репозитория с помощью `.gitignore`.

**Сбросьте кэш браузера <kbd>Ctrl-F5</kbd>.** Браузер при любой возможности старается кэшировать файлы статики: CSS, картинки и js-код. Порой это приводит к странному поведению сайта, когда код уже давно изменился, но браузер этого не замечает и продолжает использовать старую закэшированную версию. В норме Parcel решает эту проблему самостоятельно. Он следит за пересборкой фронтенда и предупреждает JS-код в браузере о необходимости подтянуть свежий код. Но если вдруг что-то у вас идёт не так, то начните ремонт со сброса браузерного кэша, жмите <kbd>Ctrl-F5</kbd>.


## Локальный запуск через Docker Compose для разработчиков

Проект можно запустить полностью в контейнерах Docker. В этом режиме база данных, backend и сборка frontend работают в отдельных контейнерах.

### Что нужно установить

Перед запуском убедитесь, что у вас установлены:

- Docker
- Docker Compose (в современных версиях входит в Docker)

Проверить можно командами:

```sh
docker --version
docker compose version
```
[Установите Docker и Docker Compose](https://docs.docker.com/manuals/), если не установлен.


### Подготовка `.env`

Создайте файл `.env` в корне проекта. Минимальный пример:

```sh
SECRET_KEY=django-key-random
GEO_API_KEY=ВАШ_YANDEX_API_KEY
DB_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
POSTGRES_DB=star_burger
POSTGRES_USER=star_burger_user
POSTGRES_PASSWORD=star_burger_password
```
в ``DB_URL``

```
NAME - имя БД,
USER - логин,
PASSWORD - пароль юзера,
НOST - localhost,
PORT - порт по умолчанию - 5432,
```

Если необходим Rollbar, добавьте в `.env` - ``ROLLBAR_TOKEN``

``ROLLBAR_TOKEN`` - [см. документацию к сервису Rollbar](https://docs.rollbar.com/docs/access-tokens)

`GEO_API_KEY` — ключ API Яндекс Карт.

### Запуск проекта

В корне проекта выполните:

```sh
docker compose -f docker-compose.local.yml up --build
```

Docker запустит три контейнера:

- `postgres` — база данных
- `django` — backend Django
- `node` — сборка frontend через Parcel

После запуска сайт будет доступен по адресу:

```
http://localhost:8000
```

### Остановка проекта

Остановить контейнеры можно командой:

```sh
docker compose -f docker-compose.local.yml down
```

### Полная очистка (включая базу данных)

Если нужно удалить все контейнеры и данные базы:

```sh
docker compose -f docker-compose.local.yml down -v
```

### Хранение данных

В Docker Compose используются именованные volumes:

- `postgres_data` — хранит данные базы PostgreSQL
- `media` — хранит пользовательские файлы

Это означает, что данные **не теряются при перезапуске контейнеров**.

А также код можно редактировать и он сразу будет подхватываться


## Деплой на сервер

### Установка Docker

```bash
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo usermod -aG docker $USER
```

Перелогиньтесь.

Проверка:

```bash
docker --version
docker compose version
```

---

### Клонирование проекта

```bash
cd /opt
sudo git clone <REPO_URL> star-burger
cd star-burger
```

---

### Настройка .env

Создайте файл `.env`:

```env
SECRET_KEY=your-secret-key
GEO_API_KEY=ВАШ_YANDEX_API_KEY
DB_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
POSTGRES_DB=star_burger_db
POSTGRES_USER=star_burger_user
POSTGRES_PASSWORD=your-password
ALLOWED_HOSTS=you_domain
CSRF_TRUSTED_ORIGINS=https://you_domen,http://you_domain
```

``GEO_API_KEY`` - [см. документацию API Яндекс Карт](https://yandex.ru/dev/commercial/doc/ru/concepts/jsapi-geocoder#how-to-use)

Если необходим Rollbar, добавьте в `.env` - ``ROLLBAR_TOKEN``
``ROLLBAR_TOKEN`` - [см. документацию к сервису Rollbar](https://docs.rollbar.com/docs/access-tokens)

в ``DB_URL``

```
NAME - имя БД,
USER - логин,
PASSWORD - пароль юзера,
НOST - localhost,
PORT - порт по умолчанию - 5432,
```
---

### Настройка nginx

В папке `nginx/` есть два конфига:

* `http.conf` — для первого запуска
* `https.conf` — после SSL

Замените заглушки:

```
YOUR_DOMAIN
```

Первый запуск:

```bash
cp nginx/http.conf nginx/default.conf
```

---

### Запуск проекта

```bash
docker compose up -d --build
```

Миграции применить командой

```bash
docker compose exec django python manage.py migrate
```

Собрать статику командой

```bash
docker compose exec django python manage.py collectstatic --noinput
```

Перезагрузить nginx

```bash
docker compose restart nginx
```

---

### Выпуск SSL сертификата

```bash
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d YOUR_DOMAIN \
  --email YOUR_EMAIL \
  --agree-tos \
  --no-eff-email
```

Переключение на HTTPS:

```bash
cp nginx/https.conf nginx/default.conf
docker compose restart nginx
```

---

### Автообновление сертификатов

```bash
crontab -e
```

Добавить:

```cron
0 3 * * * cd /opt/star-burger && docker compose run --rm certbot renew && docker compose exec nginx nginx -s reload
```

Проверка:

```bash
docker compose run --rm certbot renew --dry-run
```

---

### Деплой обновлений

```bash
bash deploy.sh
```

---

### Загрузка media

Для создания карточек товаров необходимы файлы медиа.

Скопировать с локальной машины:

```bash
rsync -avz ./media/ root@SERVER_IP:/opt/star-burger/media/
```

Загрузить в volume:

```bash
bash deploy/load_media_to_volume.sh
```

---
## Доступ в панель менеджера

Перед первоначальной работой проекта, наполнения сайта товарами, необходимо зарегестрировать админа, и через админку - https://you_domain/admin добавить менеджера.

```bash
docker compose exec django python manage.py createsuperuser
```
Панель менеджера находится по адресу - https://you_domain/manager

---

## Важно

* media и БД не хранятся в репозитории
* данные сохраняются в Docker volumes
* проект полностью восстанавливается после перезапуска
---


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
