**Link State Router Implementation**

*Techniques Avancées des Réseaux*

Master en Architecture des Systèmes Informatique

Année académique 2017-2018

![image alt text](Ressources/image_0.png)


# Table of Contents
1. [Introduction](#1)
2. [Analyse](#2)
3. [Fonctionnalités implémentées](#3)
4. [Fonctionnalités bonus](#4)
5. [Structure des fichiers](#5)
6. [Problèmes rencontrés](#6)
	6.1. [Détection des interfaces](#7)
	6.2. [Détection des interfaces](#8)
	6.3. [Compréhension du fonctionnement de SPF](#9)
	6.4. [Adaptation de l’algorithme de Dijkstra](#10)
	6.5. [Demande de ressources conséquentes](#11)
7. [Améliorations Possibles](#12)
	7.1. [Amélioration de l’interface web](#13)
	7.2. [Amélioration du code avec l’expérience](#14)
8. [Gestion des voisins par interface](#15)
9. [Conclusion](#16)
10. [Authors](#17)

# Introduction<a name="1"></a>


Dans ce rapport, nous allons détailler l’ensemble des composants et des actions entreprises pour réaliser un programme gérant un protocole de type SPF(Shortest Path First) en utilisant l’algorithme de Dijkstra. Ce programme permettra de gérer les différents envois et réceptions de trames servant au bon fonctionnement du protocole.

# Analyse<a name="2">

*"On a choisi Python car c’est facile, cool et ludique comme les Legos" *(Longrée G. 2018)*.* 

Les principaux atouts de l’utilisation du langage Python sont la simplicité de syntaxe et la librairie Scapy. Scapy étant une librairie de gestion de paquets, elle permet de générer ou modifier sur plusieurs niveaux des trames ainsi que de les envoyer et d’intercepter la réponse de ceux-ci. 

Nous avons définis deux parties principales: la gestion du serveur qui comporte l’envoi des paquets, et la réception ainsi que le traitement de ceux reçus des autres routeurs. Ces deux parties sont explicitement démontrées ci-dessous.
![image alt text](Ressources/ana_0.png)
![image alt text](Ressources/ana_1.png)
# Fonctionnalités implémentées<a name="3">

Dans la réalisation de ce projet, nous avons implémenté diverses fonctionnalités de base comme demandé dans l’énoncé. Nous avons également ajouté des fonctionnalités bonus décrite dans la partie suivante que nous avons jugé nécessaire dû à la nature du protocole.

Lors du démarrage, le routeur lit les informations contenues dans un fichier de configuration. Ce fichier contient des informations sur le routeur ainsi que les routeurs voisins avec qui il s’attend de communiquer.

Une fois ces informations connues, le routeur émet certaines trames. Une trame HELLO, émise à un interval précisé au lancement ou de 5 secondes par défaut, ainsi qu’une trame LSP qui est chargé de transmettre les informations des liens connus du routeur, également précisé au lancement ou de 60 secondes par défaut.

Afin de vérifier l’accusé de réception des messages LSP, nous avons implémenté une table qui contient tous les messages LSP transmis. Lors de l’envoi d’un message LSP, un nouveau thread est lancé afin contrôler toutes les 5 secondes si un accusé de réception à bien été reçu. Dans le cas contraire, le LSP est retransmis, jusqu’à un maximum de 4 fois.

A la réception de paquet, le routeur entreprend diverses actions selon le contenu de la trame :

* Lors de la réception d’une trame HELLO, le routeur va insérer ou mettre à jour les informations dans une table d’adjacence.

* Lors de la réception d’une trame LSP, le routeur va insérer ou mettre à jour les informations dans une table d’état de liens, répondre à la mise à jour par une trame LSACK, pour ensuite propager ce paquet aux autres routeurs (excepté le routeur originaire du LSP).

* Lors de la réception d’une trame DATA, le routeur va vérifier s’il en est le destinataire, afficher le message si c’est le cas, ou router le paquet vers sa destination le cas contraire.

* Lors de la réception d’une trame LSACK, le routeur vérifie si l'accusé de réception est attendu, et supprime l'entrée correspondante dans la table contenant les LSP transmis (mettant fin au processus de retransmission).

Afin de calculer les routes, l’algorithme Dijkstra a été implémenté. Cela a permis de construire un graphe sur base de la base de données d’états des liens, et sur base de ce même graphe, construire une table de routage.

Nous avons également intégré un moniteur d’adjacence. Son but est de vérifier à interval régulier si un voisin n’a plus émis de message HELLO pendant plus de 4 fois le délai HELLO. Si c’est le cas, le voisin est considéré comme mort, il est supprimé de la table d’adjacence, ses entrées sont supprimées de la base de données d’état de lien, et l’algorithme SPF est relancé. L’intervalle de temps est de la moitié du délai maximum entre les transmissions de message LSP.

# Fonctionnalités bonus<a name="4">

Durant le développement du projet, il s’est très vite fait ressentir le besoin d’avoir une console d’interaction afin de pouvoir monitorer et effectuer des tests pendant que le serveur fonctionne. Nous avons donc pourvu notre programme d’une console interactive permettant de pratiquement tout utiliser en terme de code Python. Nous lui avons aussi ajouté des commandes ressemblants à celles d’un routeur Cisco ainsi qu’un travail poussé pour permettre un affichage clair et concis des informations demandées. Il ne vas pas sans dire que chaque erreur est aussi gérée.

Pour le jour des tests avec les autres prototypes, nous avons mis en place une interface web permettant de regrouper la totalité de notre structure de données afin de pouvoir monitorer plus aisément chacun de nos routeurs. Celle-ci s’actualise automatiquement toutes les 2 secondes.

# Structure des fichiers<a name="5">

Le programme est divisé en plusieurs fichiers :

* Router.py

    * Initialise la configuration et lance les divers processus de routage.

    * Se lance également en mode interpréteur de commande.

* Data_structures.py

    * Contient la définition et l’initialisation des classes contenant les diverses tables de données.

* Spf_algorithm.py

    * Contient l’algorithme Dijkstra pour le calcul des chemins les plus courts.

* Packet_sender.py

    * Contient les différents threads chargés de la gestion d’envoi des messages HELLO et LSP ainsi que les méthodes pour l’envoi de message LSACK et la propagation de LSP aux autres routeurs voisins.

* Packet_receiver.py

    * Contient la définition du thread qui gère la réception des messages HELLO, LSP, LSACK et DATA.

* Adjacency_monitor.py

    * Contient la définition du thread qui contrôle la table d’adjacence pour des voisins qui auraient été déconnectés.

* Webserv.py

    * Contient l’ensemble de la base du serveur web ainsi que son initialisation.

* Config.ini

    * Contient l’ensemble des données initiales et théoriques du réseau. Comme demandé dans les consignes initiales.

# Structure des données<a name="6">

Afin de permettre aux divers composants du programme d’accéder à un espace mémoire partagée, nous avons regroupé toutes nos structures de données en un seul fichier, importé par les divers autres fichiers Python.

Pour simplifier le développement et la lecture des modules chargés d’accéder à ces structures, nous avons définit de nombreuses classes d’objet indépendant, tels que **Neighbor** ou **LinkState**, pour ensuite les regrouper dans des dictionnaires/listes.

Dans un même but, nous avons également redéfini les classes dict et list Python en étendant celles-ci, afin d’ajouter d’autres méthodes de manière personnalisé. Ceci nous a permis d’ajouter des méthodes de recherche, de mise à jour et de suppression d’élément de nos structures de données sur base d’argument précis autre qu’une clé ou un index.

Un gros avantage de notre redéfinition des classes dict/list est que nous avons pu directement ajouter une variable de type Lock à chacune de nos structures, nous permettant de pallier au accès concurrentiels.

![image alt text](Ressources/image_1.png)

# Problèmes rencontrés<a name="7">

## Détection des interfaces<a name="8">

Par soucis de temps, nous n’avons pas su intégrer un module de détection des interfaces qui se connecte/déconnecte.

Etant donné que notre implémentation actuelle permet de générer les LSP dynamiquement sur base des voisins présent, et cela même si un voisin tombe, nous avons jugez que l’implémentation de la détection n’était pas une urgence et que son absence n’aurait pas d’effet négatif sur la fonctionnalité, mais uniquement sur l'optimisation.

De plus, la mise en place d’un système de gestion d’événements en Python étant nouvelle pour nous, la courbe d’apprentissage de ce module aurait eu un impacte important sur le reste de l’avancement du projet.

## Compréhension du fonctionnement de SPF<a name="9">

A travers le développement du projet, nous nous sommes souvent trouvé face à des doutes sur les principes du SPF. Notamment la méthode de propagation, le format des LSACK, la méthode de suivis des LSP envoyés par rapport au LSACK reçu, etc.

Afin de nous assister dans la compréhension et nous donner des pistes sur le fonctionnement en cas pratique, nous nous sommes par moment basé sur la RFC 2328 concernant l’OSPF version 2.

## Adaptation de l’algorithme de Dijkstra<a name="10">

Durant nos recherche d’algorithmes existants, nous avons trouvé diverses solutions qui proposaient le calcul du SPF sur base de graphes pondérés. Cependant, la compréhension des codes trouvés s’avéra complexe, rendant l’adaptation des codes trouvés d’autant plus complexe.

Afin de pallier à cette difficulté, nous avons décidé de prendre connaissance de l’algorithme de Dijkstra et de le développer nous même.

Cette approche nous a semblé d’autant plus intéressant et gratifiante face à la compréhension de l’algorithme. De plus, développer notre propre implémentation de l’algorithme nous a permis de prévoir les méthodes nécessaires pour générer la table de routage sur base de l’arbre SPF calculé (chose qui aurait été d’autant plus complexe si nous avions dû adapter un code étranger).

## Demande de ressources conséquentes<a name="11">

Ce projet, si nous voulions faire des tests réels, demande une ressource machine non négligeable. Pour la réalisation des tests de notre équipe, il y a eu un ensemble de 6 machines virtuelles déployées. Cet exercice aurait été encore plus complexe si nous avions dû tester sur des machines physiques.

## Modification de syntaxe du LSACK<a name="12">

Lors de l’implémentation de la gestion des LSACK, nous nous sommes rendu compte que le format demandé dans les consignes ne contenait pas assez d’informations que pour pouvoir assurer de l’accusé de réception d’une LSP précise.

Le format demandé:

*LSACK [Router Name] [Sequence Number]* 

Ou *Router Name* est le nom du routeur voisin accusant réception et *Sequence Number***_ _**le numéro de séquence de la LSP.

En effet, ce format d’accusé de réception ne permet pas de savoir si le routeur voisin accuse réception d’une LSP générée par le routeur courant, ou si l’accusé de réception concerne une LSP qui a été propagée depuis un autre voisin.

Après concertation entre les divers groupes travaillant sur le projet, nous avons convenu d’un nouveau format de LSACK:

*LSACK [Router Name] [LSP Sender Name] [Sequence Number]*

Ce qui différencie ce format du précédent est l’ajout d’un champ *LSP Sender Name* qui contient le nom du routeur dont la LSP est originaire (i.e.: le premier routeur qui a envoyé la LSP).

Ce nouveau format nous permet, dès lors, de savoir avec précision quel LSP le routeur voisin accuse réception, permettant de mettre fin au processus de retransmission de LSP dont la réception n’aurait pas été confirmé.

# Améliorations Possibles<a name="13">

## Amélioration de l’interface web<a name="14">

L’interface web, actuellement, n’est capable que d’afficher les informations d’un routeur. Il aurait été possible avec plus de travail de pouvoir renforcer cette interface d’une invite de commande interactif ainsi que d’une zone prévue pour les notifications d’envoi et réception de trames.

## Amélioration du code<a name="15">

Avec l’expérience acquise et future, le code pourrait certainement être revu dans son entièreté afin d’optimiser et de le rendre encore plus compréhensible. De plus, nous n’avons pas respecter l’architecture type d’un projet Python. Il faudrait ajouter les dépendances dans le projet ainsi que de respecter le schéma ci-dessous.

![image alt text](Ressources/image_2.png)

## Gestion des voisins par interface<a name="16">

Une amélioration intéressante en terme d’optimisation aurait été l’association des voisins configurés avec les interfaces du routeur. 

La démarche requise aurait été de faire une comparaison entre chacunes des adresses IP des voisins et les IP de chaque interface du routeur. Afin de déterminer si le voisin se trouve sur cette interface, un ET binaire avec le masque de l’interface du routeur aurait permis, par une simple comparaison, de déterminer sur quels interfaces du routeur se trouvent chaque voisins.

Cette démarche est notamment appliquée par les routeurs de Cisco lorsqu’ils requièrent d’entrer une adresse réseau et une masque wildcard dans la configuration du processus OSPF.

Cette méthode aurait augmentée la précision de l’envoi de messages via Scapy, qui actuellement ne se base que sur l’adresse IP. Elle aurait également pu prévenir des potentielles erreurs de configuration: un voisin dont l’adresse configurée n’est présente sur aucune des interfaces aurait renvoyé une erreur lors de l’initialisation de la configuration, avant même le lancement du processus SPF.

# Conclusion<a name="17">

Ce travail a permis de développer nos compétences en Python. Cela a permit de limiter le nombre de lignes écrites et donc de mieux se pencher sur le fonctionnement interne du SPF sans pour autant se réduire en terme de fonctionnalités implémentées. Le projet ayant été rudement bien mené, le projet sera surement rendu publique par la suite.



# Authors<a name="18">
* [**Jean-Cyril Bohy**](https://bohy.me) - *Étudiant Master 1* 
* [**Gaëtan Longrée**](https://www.longree.be) - *Étudiant Master 1* 

