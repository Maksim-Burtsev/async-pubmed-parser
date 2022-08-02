# PubMed-parser #


<image src="scr_1.jpg" alt="Описание картинки">

*Так выглядит одна из страниц Word-документа в результате работы* 


### **Что такое PubMed**

PubMed - это ресурс, на котором публикуются различные материалы по биомедицине и наукам с целью улучшения здоровья. 

В частности там публикуются исследования, касающиеся самых разных тем. 

### **Что делает эта программа**

Данное приложение собирает основные материалы исследований (заголовок и краткое описание) и записывает их в Word-документ. 

### **Какие библиотеки были использованы**

 - requests
 - BeautifulSoup
 - docx *(для работы с Word-документами)*

### **Как работает**

На вход программа получает готовый URL, который включает в себя все необходимые query-параметры. 

*Пример корректного URL со всеми параметрами:*
```
https://pubmed.ncbi.nlm.nih.gov/?term=heart&filter=simsearch1.fha&filter=years.2022-2022

```

Далее она собирает ссылки на все исследования с первых 5 страниц по указанному запросу.

После отдельно парсится html-страница каждого из исследований, достаётся заголовок и абстракт и в случае успеха результат записывается в Word-документ. 

Все ссылки на статьи, которые распарсить не получилось записываются в отдельный файл. 

*Так же для удобства использования другими людьми был создан exe-файл.*

### **Запуск**

``` 
python main.py
```
**далее вводится ссылка на поисковый запрос как в примере.*


