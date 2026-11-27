# Faut-il supprimer la formule Premium ?

*Réponse courte : Non. L'analyse des données de sinistres et de contrats (`assurrisk2`) montre que la formule Premium présente certes un coût moyen par sinistre légèrement supérieur à celui de la formule Essentielle, mais que cet écart reste modéré, que son poids global dans la charge reste minoritaire et que sa fréquence par contrat ou assuré ne dépasse pas celle d'Essentielle.

---

## 1. Coût moyen et poids dans la charge de sinistres

*Coût moyen par dossier (SQL & Python) :
 Montant estimé moyen :7 016,15 € sur Premium contre 6 787,93 € sur Essentielle, soit un écart de +228,22 € par sinistre entre Premium et Essentielle.
 Montant indemnisé moyen (paiements `payé`) : 3 586,59 € sur Premium contre 3 414,32 € sur Essentiell, soit un écart de +172,27 € par sinistre entre Premium et Essentielle.

*Poids dans la charge totale :
 Sur l'ensemble des trois formules (82 216 409,00 € estimés et 41 908 977,42 € indemnisés sur 12 098 sinistres), Premium représente 20,56 % de la charge estimée
 (16 901 896,00 €) et 20,62 % de la charge indemnisée (8 640 102,17 €), derrière Essentielle (41,32 % estimé / 40,78 % indemnisé) et Confort (38,12 % estimé / 38,61 % indemnisé).
 (Sur le périmètre restreint Premium vs Essentielle du script Python, Premium pèse 33,22 % de la charge estimée et 33,58 % de la charge indemnisée.)

---

## 2. Fréquence de sinistres par contrat et par assuré

*Par contrat : Premium affiche 41,24 % (soit `0,4124` sinistre par contrat : 2 409 sinistres pour 5 841** contrats), un niveau légèrement inférieur à celui d'Essentielle* 
(41,80 %, soit `0,4180` : 5 005 sinistres pour 11 975 contrats) et supérieur à Confort (39,86 %, soit `0,3986` : 4 684 sinistres pour 11 752 contrats).

*Par assuré : Premium* est également légèrement sous Essentielle (51,47 %, soit `0,5147` sinistre par assuré sur 4 680 assurés, contre 52,37 %, 
soit `0,5237` sur 9 557 assurés pour Essentielle et 49,79 %, soit `0,4979` sur 9 407 assurés pour Confort). Le ratio de 1,25 contrat par assuré est identique sur les trois formules.

---

## 3. Effet de la franchise et écarts par dossier

*Franchise moyenne : Elle est très proche d'une formule à l'autre : 230,39 € sur Premium (555 020,00 € au total), 229,34 € sur Essentielle (1 147 850,00 €) et 
227,15 € sur Confort (1 063 980,00 €). La franchise n'absorbe donc pas davantage le surcoût de Premium et représente en moyenne 8,06 % du montant estimé sur Premium
(contre 8,20 % sur Essentielle et 8,27 % sur *Confort).

*Écart (`montant estimé - franchise - montant indemnisé`) : Il s'établit en moyenne à 3 199,16 € par dossier sur Premium (7 706 773,83 € au total), 
144,26 € sur Essentielle (15 737 044,31 € et 3 009,56 € sur Confort (14 096 763,44 €).
---

## Conclusion

Supprimer la formule Premium sur le seul constat d'un coût moyen supérieur de +172,27 € indemnisés par sinistre ne paraît pas fondé : 
Premium génère un peu moins de sinistres par contrat et par assuré qu'Essentielle, présente une franchise moyenne quasi équivalente et
ne représente qu'environ 20,6 % de la charge indemnisée totale.