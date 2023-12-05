# Scraping_Python_Project_2023

## Описание

Данный парсер выполняет парсинг сайтов Dns и Citilink.

Используемый стек:

    Загружаемые библиотеки:
     - flask
     - undetected_chromedriver
     - requests
     - bs4
      
    А также встроенные:
     - time
     - json
     - multiprocessing
     - re
     - string
     - random
  
## Туториал по установке парсера:

1) Создайте папку под парсер в любом удобном для вас месте:
   
   `mkdir Parser`
   
   `cd Parser`
   
3) Произведите клонирование репозитория:
   
   `git clone https://github.com/Koteika1156/Scraping_Python_Project_2023.git`
   
5) Перейдите в папку Scraping_Python_Project_2023:
   
   `cd Scraping_Python_Project_2023`

### Запуск через docker-compose

1) Установите docker и docker-compose себе на компьютер
2) Переключитесь на ветку with-docker-compose:

  `git checkout with-docker-compose`
    
4) Исполните скрипт build.sh

  `./build.sh` или `sudo ./build.sh`

5) Подождите пока закончится сборка проекта, в конце в консоли должно появится:
<kbd>![image](https://github.com/Koteika1156/Scraping_Python_Project_2023/assets/89998783/7e690ee0-643d-46dd-a43a-d5209331af1f)</kbd>

6) Сборка завершена! Откройте браузер и перейдите по ссылке http://127.0.0.1:5000, и используйте парсер.

### Запуск без docker-compose

Установите браузер google chrome, он нужен для корректной работы.

1) Переключитесь на ветку without-docker-compose:

`git checkout without-docker-compose`

2) Установите необходимые библиотеки:

   `pip install -r requirements.txt`

3) Запустите файл app.py:

   `python app.py`

6) Всё! Откройте браузер и перейдите по ссылке http://127.0.0.1:5000, и используйте парсер.

## Туториал по использованию парсера:

Внешний вид:

<kbd>![image](https://github.com/Koteika1156/Scraping_Python_Project_2023/assets/89998783/f028fcd7-6235-456b-ac9d-2be0994c2d54)</kbd>

Для того чтобы начать использовать парсер введите запрос в поисковую строку и нажмите кнопку ниже.
Из-за особенностей парсинга, первый запрос будет выполняться, в среднем, на 40 секунд дольше чем остальные.

Вы можете исключить товары в наименовании которых не будет полного поискового запроса, выбрав соответствующее поле ниже.(Парсер всё равно спарсит все товары по запросу, но выведет только те, что будут иметь в названии полный поисковой запрос.)

Также вы можете посмотреть историю своих запросов нажав на соответствующую кнопку:
<kbd>![image](https://github.com/Koteika1156/Scraping_Python_Project_2023/assets/89998783/7be9eed5-adb3-4117-968d-d7d8e78d7c61)</kbd>

Выберете пункт из списка и нажмите на кнопку ниже, в этом случае будет выведены все товары по этому запросу из базы данных.

<kbd>![image](https://github.com/Koteika1156/Scraping_Python_Project_2023/assets/89998783/cc55f5ed-350e-4fa6-b045-31bcabf65fab)</kbd>

Если вы устанапливали парсер используя docker-compose, то, после пересборки проекта, база данных с прошлыми запросами будет сохранена.
