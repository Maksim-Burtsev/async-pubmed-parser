# **PubMed-parser** #

## *What is PubMed*

PubMed - is a search engine for biomedical research.

In particular, it publishes studies (descriptions) on a wide variety of topics. 

## *Что делает эта программа*

This application collects the title and abstract of studies and then writes them in a file (.md or .txt). 

## *How is works*

The program receives a ready-made URL, which includes all the necessary query parameters. 

*Example of correct URL:*
```
https://pubmed.ncbi.nlm.nih.gov/?term=heart&filter=simsearch1.fha&filter=years.2017-2022
```
*You can use it to make a test run of program.*

Then links to all studies from the first 5 pages of the specified query are collected. (you can change this value when entering the data)

After that the html page of each of the studies is parsed separately. If for some reason it is not possible to do this, then the link to the study goes to the list of *skipped*, which is displayed at the end. 
 

## **Usage**

``` 
python main.py
```

**After that make input:**

``` URL: ``` **https://pubmed.ncbi.nlm.nih.gov/?term=heart&filter=simsearch1.fha&filter=years.2017-2022**

``` Filename: ``` **heart**

```What type of output file: .txt or .md?(default is .md)```

```1 - .md```

```2 - .txt ```

**1**

```Default amount of pages is 5 (1 page = 50 research). ```
```Do you want to change it? [Y-yes, N-no]``` **N**

```Research links have been successfully collected.```

```Data collection begins...```

```Data successfully collected!```
```Preparing and writing to file...```

```Success!```
```Now you can view collected researches in your file.```

The running time was 7.1 sec.

The file **heat.md** with formatted data appears in the current directory.

Example of file contents:

## **Metabolic remodelling in heart failure**
*https://pubmed.ncbi.nlm.nih.gov/29915254/*<br> The heart consumes large amounts of energy in the form of ATP that is continuously replenished by oxidative phosphorylation in mitochondria and, to a lesser extent, by glycolysis. To adapt the ATP supply efficiently to the constantly varying demand of cardiac myocytes, a complex network of enzymatic and signalling pathways controls the metabolic flux of substrates towards their oxidation in mitochondria. In patients with heart failure, derangements of substrate utilization and intermediate metabolism, an energetic deficit, and oxidative stress are thought to underlie contractile dysfunction and the progression of the disease. In this Review, we give an overview of the physiological processes of cardiac energy metabolism and their pathological alterations in heart failure and diabetes mellitus. Although the energetic deficit in failing hearts - discovered >2 decades ago - might account for contractile dysfunction during maximal exertion, we suggest that the alterations of intermediate substrate metabolism and oxidative stress rather than an ATP deficit per se account for maladaptive cardiac remodelling and dysfunction under resting conditions. Treatments targeting substrate utilization and/or oxidative stress in mitochondria are currently being tested in patients with heart failure and might be promising tools to improve cardiac function beyond that achieved with neuroendocrine inhibition. 
## **Heart regeneration using pluripotent stem cells**
*https://pubmed.ncbi.nlm.nih.gov/32690435/*<br> Pluripotent stem cells (PSCs), which include embryonic and induced pluripotent stem cells (ESCs and iPSCs, respectively), have great potential in regenerative medicine for heart diseases due to their virtually unlimited cardiogenic capacity. Many preclinical studies have described the functional benefits after transplantation of PSC-derived cardiomyocytes (PSC-CMs). However, transient ventricular arrhythmias were detected after injection into non-human primates and swine ischemic hearts; as engrafted PSC-CMs form an electrical coupling between host and graft, the immature characteristics of PSC-CMs may serve as an ectopic pacemaker. We are entering a critical time in the development of novel therapies using PSC-CMs, with the recent first clinical trial using human iPSC-CMs (hiPSC-CMs) being launched in Japan. In this review, we summarize the updated knowledge, perspectives, and limitations of PSC-CMs for heart regeneration. 

```...```

