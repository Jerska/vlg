# Workpackage 3

Pour ce rendu, j'utilise le double-sweep fourni dans le `diam.c`.
Plutôt que de modifier le code fourni et essayer de merge community avec
`diam.c`, j'ai fait un script de préprocessing pour réordonner les noeuds
directement dans le fichier de description du graphe.
Note : J'ai évidemment commenté le `random_renumbering` dans `diam.c`
et j'ai rajouté un bout de code pour évaluer le temps d'exécution à
chaque itération du double-sweep.

Pour que le script fonctionne, il attend `inet` et `ip` à la racine du projet
sous ces noms exacts.

Le script mettant approximativement 10/15 minutes à tourner, voici son
output chez moi :

    * Compiling the different binaries
    * Creating binary versions of our inputs
      - inet
      - ip
    * Generating communities
      - inet
      - ip
    * Reordering by communities
      - inet
        # Parsing file
        # Communitizing 1719037 nodes
        # Renumber with these new 45 communities
        # Parsing original graph file
          + Getting degrees
          + Getting links
        # Printing a new graph file to match this reordering
      - ip
        # Parsing file
        # Communitizing 2250498 nodes
        # Renumber with these new 35 communities
        # Parsing original graph file
          + Getting degrees
          + Getting links
        # Printing a new graph file to match this reordering
    * Evaluating performance (Let it some time to run)
      - inet
        # Diam unordered : 53'129 ms
          - Iteration 1 : 2'332 ms
          - Iteration 2 : 2'326 ms
          - Iteration 3 : 2'322 ms
          - Iteration 4 : 2'308 ms
          - Iteration 5 : 2'318 ms
          - Iteration 6 : 2'309 ms
          - Iteration 7 : 2'308 ms
          - Iteration 8 : 2'323 ms
          - Iteration 9 : 2'327 ms
          - Iteration 10 : 2'307 ms
          - Iteration 11 : 2'306 ms
          - Iteration 12 : 2'297 ms
          - Iteration 13 : 2'309 ms
          - Iteration 14 : 2'323 ms
          - Iteration 15 : 2'327 ms
          - Iteration 16 : 2'314 ms
          - Iteration 17 : 2'307 ms
          - Iteration 18 : 2'309 ms
          - Iteration 19 : 2'309 ms
          - Iteration 20 : 2'312 ms
        # Diam reordered : 54'479 ms
          - Iteration 1 : 2'376 ms
          - Iteration 2 : 2'366 ms
          - Iteration 3 : 2'358 ms
          - Iteration 4 : 2'362 ms
          - Iteration 5 : 2'368 ms
          - Iteration 6 : 2'362 ms
          - Iteration 7 : 2'364 ms
          - Iteration 8 : 2'360 ms
          - Iteration 9 : 2'361 ms
          - Iteration 10 : 2'357 ms
          - Iteration 11 : 2'366 ms
          - Iteration 12 : 2'365 ms
          - Iteration 13 : 2'376 ms
          - Iteration 14 : 2'374 ms
          - Iteration 15 : 2'405 ms
          - Iteration 16 : 2'385 ms
          - Iteration 17 : 2'384 ms
          - Iteration 18 : 2'363 ms
          - Iteration 19 : 2'379 ms
          - Iteration 20 : 2'378 ms
        # Community unordered : 164'851 ms
        # Community reordered : 76'933 ms
      - ip
        # Diam unordered : 11'352 ms
          - Iteration 1 : 1'646 ms
        # Diam reordered : 12'236 ms
          - Iteration 1 : 1'711 ms
        # Community unordered : 86'598 ms
        # Community reordered : 39'566 ms

Comme nous pouvons le voir, le renumbering selon les communautés a un apport
nul voire négatif sur le double-sweep. En revanche, il influe directement
sur la rapidité d'exécution de community.

L'amélioration sur community paraît évidente, cependant mérite d'être
soulignée : On divise par deux le temps d'exécution.

Le résultat sur diam me semble également cohérent : en effet, réordonner les
noeuds ne devrait avoir que peu d'impact sur un BFS : nous ne parlons pas ici
d'un parcours profondeur, par conséquent, nous visitons malgré tout tous les
fils de notre noeud, et sortons donc autant de sa communauté, avant d'y
rerentrer au niveau d'après. Il est cependant étonnant que cela ne diminue pas
les pages misses.
