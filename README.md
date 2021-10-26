# DashBot

This repository contains code for DashBot, a machine-learning powered system for dashboard generation.
DashBot recommends panels iteratively and processes **user feedback**.
The recommendation first relies on a notion of **data-driven relevance** of attributes, but also **coverage** of attributes to ensure summarization.
It offers the possibility to give an **explanation** on why a panel is rejected, learns from user feedback and can trigger **multi-armed bandits** algorithms to refine intelligently a rejected panel without explanation from the user.

## Folder structure
DashBot is implemented to run via a user **interface** as well as perform **experiments**.
The folder *implem/* contains the main part of the code, shared by both usages.
*experiment/* contains the code specific to experiments and *interface/* the code specific to the interface.

In the root folder, you will also find the python script to execute:
* *start-api.py* for the interface
* *start_experiment.py* to run experiments.

### How to use DashBot?

1. Download code 
1. Download required versions of libraries
`> pip3 install -r requirements.txt`
1. Start API
`> python3 start-api.py`
1. Open [http://0.0.0.0:8080/src/dashbot.html](http://0.0.0.0:8080/src/dashbot.html) in your browser

## Citation

If you are using this source code in your research please consider citing us:
Sandrine da Col, Radu Ciucanu, Marta Soare, Nassim Bouarour, Sihem Amer-Yahia. **DashBot: An
ML-Guided Dashboard Generation System**. *30th ACM International Conference on
Information and Knowledge Management*, Nov 2021, Queensland (in line), Australia. [[pdf](https://hal.archives-ouvertes.fr/hal-03379720/document)] [[video](https://youtu.be/iOtDOaIYVzk)]
```
@inproceedings{da2021dashbot,
  title={DashBot: An ML-Guided Dashboard Generation System},
  author={Da Col, Sandrine and Ciucanu, Radu and Soare, Marta and Bouarour, Nassim and Amer-Yahia, Sihem},
  booktitle={ACM International Conference on Information and Knowledge Management (CIKM)-Demo track. Accepted for publication,
  year={2021}
}
```

## Team



![sandrine](/interface/src/img/sandrine.jpg) | ![radu](/interface/src/img/radu.png) | ![marta](/interface/src/img/marta.jpg) | ![nassim](/interface/src/img/nassim.png) | ![sihem](/interface/src/img/sihem.jpg)
------------ | ------------- | ------------- | ------------- | -------------
[Sandrine Da Col](https://scholar.google.fr/citations?hl=fr&user=sbOKfl8AAAAJ) | [Radu Ciucanu](https://dl.acm.org/profile/81759010757) | [Marta Soare](https://lig-membres.imag.fr/soare/) | [Nassim Bouarour](http://www.gipsa-lab.grenoble-inp.fr/page_pro.php?vid=3886) | [Sihem Amer-Yahia](https://lig-membres.imag.fr/amery/)

