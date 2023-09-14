# Logisim16bCPU

Un design processeur 16b n'utilisant que des portes logiques  
**NOT, AND, OR, XOR, NAND, NOR**,  
des **transistors NMOS et PMOS** 3-broches,  
et des **multiplexeurs** (par simplicité et rapidité de simulation, 
mais qui n'en demeurent pas moins immédiatement recréables en portes logiques élémentaires).

## Statut

*Projet en cours d'évolution.*

## Pré-requis

- Logisim-evolution, disponible sur leur repo : https://github.com/logisim-evolution/logisim-evolution  
Téléchargez de préférence un *nightly-build* plutôt que la dernière version stable 3.8.0  , 
la durée d'ouverture d'un projet ayant grandement été réduite depuis.
- Python 3.6+ avec Numpy


## Organisation des fichiers

Le dossier ***V2*** renferme tous les fichiers utiles:  
1. 16bCPUv2.circ à ouvrir avec Logisim et dont le fichier principal est *testall_wlogic_V2*. 
	Ce dernier exhibe le bloc CPU, sa logique, et un affichage de mot à 7-segments.
1. assemblerV2.py qui permet d'assembler vos programmes *.S* vers un fichier *flashMe.hex* 
	qui sera chargé dans la RAM (simulée) lors de l'opération FLASH.
1. controllogicV2.xlsx, dataflowV2.pptx documentent les potentialités de l'architecture, 
	ainsi que leur implémentation dans la micro-architecture.
1. microcodeV2.py qui permet de générer les ROMs de contrôle utilisées par le bloc *handles_puller* du projet .circ.
	Ces fichiers étant fournis déjà générés dans le répertoire *v2roms_space*, il n'est pas nécessaire de l'exécuter
	(sauf à des fins de modification du CPU).
1. Un programme de démonstration montrant la multiplication de deux entiers non-signés, en Python et en Assembleur,
	est disponible dans le répertoire *test_programs*. Le fichier *flashMe.hex* émanant de l'assemblage du code *.S* par le script Python
	vous permet de tester le bon fonctionnement de ses quelques instructions par le CPU 
	sans que vous ayez à écrire un *.S* par vous-même.

## Walkthrough du programme de démonstration

Se référer à la [documentation disponible](/V2/walkthrough/8b_unsigned_mult.pdf).

#### Debug
Si le programme de test (multiplication de 2 entiers) affiche à la fin de chaque exécution `0x0000` comme résultat , 
	vérifiez la bonne connection des sélecteurs des multiplexeurs.  
Les versions <3.9 de Logisim sont sujettes à ce problème
(souffrant d'un point d'ancrage du pin sélecteur des multiplexeurs mal placé, 
avec mon desing ceux-ci ne seront pas alimentés et se résoudront obstinément à sélectionner toujours l'entrée 0).

## Version du projet : 2.0

- [x] Architecture refondue  &check;
- [ ] Emulation logicielle des opérations en Float32 &cross;
- [ ] Ajout de nouvelles instructions, niveau matériel (Rotate, Shift by Shift Amount, ADD/SUB with Carry Flag, etc.) &cross;
- [ ] Ajout de nouvelles instructions, niveau assembleur (push/pull to stack, mult.i, add.f, etc.) &cross;
- [ ] Ajout d'un co-processeur pour les opérations à virgule fixe &cross;
- [ ] Ajout d'un co-processeur pour les opérations à virgule flottante &cross;

#### divers

- [ ] regf_1w_Dual n'utilise plus le sous-circuit regf_1cell_Dual (&rarr; *regf_1w_DualOpt*) &cross;