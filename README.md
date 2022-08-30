# **PubMed-parser** #

## *Что такое PubMed*

PubMed - это ресурс, на котором публикуются различные материалы по биомедицине и наукам с целью улучшения здоровья. 

В частности там публикуются исследования на самые разные темы. 

## *Что делает эта программа*

Данное приложение собирает название и описания исследований, а после записывает их в Markdown-файл. 

## *Как работает*

На вход программа получает готовый URL, который включает в себя все необходимые query-параметры. 

*Пример корректного URL со всеми параметрами:*
```
https://pubmed.ncbi.nlm.nih.gov/?term=heart&filter=simsearch1.fha&filter=years.2017-2022
```

Далее собираются ссылки на все исследования с первых 5 страниц по указанному запросу.

После отдельно парсится html-страница каждого из исследований. Если по каким-то причинам сделать это не получается, то ссылка на исследование попадает в список *пропущенных*, который выводится в конце. 
 

## **Запуск и результат работы**

``` 
python main.py
```

**Далее происходит ввод данных и запуск программы:**

``` Ссылка: ``` https://pubmed.ncbi.nlm.nih.gov/?term=heart&filter=simsearch1.fha&filter=years.2017-2022

``` Как назвать файл? ``` heart

``` Ссылки на исследования собраны. ```                                                
```Начинается сбор данных... ```      

```Данные собраны!```<br>
```Подготовка и запись в файл...```

```Данные успешно записаны!```<br>
```Время работы программы составило 5.6 сек.```

В текущей директории появится файл **heat.md** c отформатированными данными:

## **Metabolic remodelling in heart failure**
*https://pubmed.ncbi.nlm.nih.gov/29915254/*<br> The heart consumes large amounts of energy in the form of ATP that is continuously replenished by oxidative phosphorylation in mitochondria and, to a lesser extent, by glycolysis. To adapt the ATP supply efficiently to the constantly varying demand of cardiac myocytes, a complex network of enzymatic and signalling pathways controls the metabolic flux of substrates towards their oxidation in mitochondria. In patients with heart failure, derangements of substrate utilization and intermediate metabolism, an energetic deficit, and oxidative stress are thought to underlie contractile dysfunction and the progression of the disease. In this Review, we give an overview of the physiological processes of cardiac energy metabolism and their pathological alterations in heart failure and diabetes mellitus. Although the energetic deficit in failing hearts - discovered >2 decades ago - might account for contractile dysfunction during maximal exertion, we suggest that the alterations of intermediate substrate metabolism and oxidative stress rather than an ATP deficit per se account for maladaptive cardiac remodelling and dysfunction under resting conditions. Treatments targeting substrate utilization and/or oxidative stress in mitochondria are currently being tested in patients with heart failure and might be promising tools to improve cardiac function beyond that achieved with neuroendocrine inhibition. 
## **Heart regeneration using pluripotent stem cells**
*https://pubmed.ncbi.nlm.nih.gov/32690435/*<br> Pluripotent stem cells (PSCs), which include embryonic and induced pluripotent stem cells (ESCs and iPSCs, respectively), have great potential in regenerative medicine for heart diseases due to their virtually unlimited cardiogenic capacity. Many preclinical studies have described the functional benefits after transplantation of PSC-derived cardiomyocytes (PSC-CMs). However, transient ventricular arrhythmias were detected after injection into non-human primates and swine ischemic hearts; as engrafted PSC-CMs form an electrical coupling between host and graft, the immature characteristics of PSC-CMs may serve as an ectopic pacemaker. We are entering a critical time in the development of novel therapies using PSC-CMs, with the recent first clinical trial using human iPSC-CMs (hiPSC-CMs) being launched in Japan. In this review, we summarize the updated knowledge, perspectives, and limitations of PSC-CMs for heart regeneration. 

```...```

