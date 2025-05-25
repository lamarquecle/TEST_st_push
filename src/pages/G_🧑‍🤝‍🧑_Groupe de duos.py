import streamlit as st
import numpy as np
import pandas as pd
from itertools import product
from collections import Counter

from models.structure import numerizer, to_learn, denumerizer

def get_collaborations_possibilities(working_childs   : np.array,
                                     childs_can_learn : np.array,
                                     childs_know      : np.array,
                                     n_childs         : int,
                                     n_comp           : int) -> np.array :
    # matrice de collaboration inter-élèves (rapprochements_inter_eleves(class_know_description, n_volontes))
    # M(n_childs1 x n_childs2 x n_comp x 4 : indices("volontes") = [0,1])
    wc  = working_childs .copy()
    ccl = childs_canlearn.copy()
    ck  = childs_know    .copy()

    collaborations_possibilities = np.zeros((n_childs, n_childs, n_comp, 4)).astype(int)
    for i_child1, i_child2, i_comp in product(range(n_childs), range(n_childs), range(n_comp)):
        collaborations_possibilities[i_child1, i_child2, i_comp, :] = np.array([
            wc[i_child1, 0]*wc[i_child2, 2] * ccl[i_child1, i_comp]*ck [i_child2, i_comp],
                # <=> child1_veut_apprendre*child2_veut_transmettre  *  child1_peut_apprendre*child2_peut_transmettre
                # RQ : child1_veut apprendre regrouppe l'envie de travail de l'élève et son acceptation par l'enseignant
            wc[i_child1, 1]*wc[i_child2, 1] * ccl[i_child1, i_comp]*ccl[i_child2, i_comp],
            wc[i_child1, 2]*wc[i_child2, 0] * ck [i_child1, i_comp]*ccl[i_child2, i_comp],
            wc[i_child1, 3]*wc[i_child2, 3] * ck [i_child1, i_comp]*ck [i_child2, i_comp]])

    # RQ : si des poids sont à accorder à des chapitres suivant l'envie de l'enseignant et des élèves,
    #      multiplier des portions de collaborations_possibilities (à definir) suivant la matrice
    #      recapitulative des des envies poids_eleves_chap et poids_enseignant_chap
    # RQ : ces poids sont à créer
    return collaborations_possibilities

def get_sujets_percent(collaborations_possibilities : np.array,
                       n_comp                       : int) -> list :
    # matrice d'existence d'une collaboration inter-élèves sur une compétence
    sujets_existence = np.max(collaborations_possibilities, axis=3)   # M(n_childs1 x n_childs2 x n_comp : [0,1])
    # matrice du nombre de collaborations entre deux élèves
    sujets_count     = np.sum(sujets_existence            , axis=2)   # M(n_childs1 x n_childs2 : [0,1,2,...])
    # matrice du % des sujets concernants la collaboration inter-élèves
    sujets_percent   = ((n_comp - sujets_count)/n_comp*100).astype(int)
    sujets_percent[np.diag_indices_from(sujets_percent)] = 100

    return sujets_count, sujets_percent

def get_methodologies_percent(collaborations_possibilities : np.array) -> list :

    # matrice d'une collaboration inter-élèves suivant leurs choix
    methodologies_existence = np.max(collaborations_possibilities, axis=2) # M(n_childs1 x n_childs2 x 4 : [0,1])
    # matrice sur la quantité opposée de collaboration inter-élèves possibles
    methodologies_count     = np.sum(methodologies_existence     , axis=2) # M(n_childs1 x n_childs2 : [0,1,2,3])
    # matrice du % opposé de méthodologies concernant la collaboration inter-élèves
    methodologies_percent   = ((1 - methodologies_count/4)*100).astype(int)
    methodologies_percent[np.diag_indices_from(methodologies_percent)] = 100

    return methodologies_count, methodologies_percent

def collaborations(liaisons_eventuelles):
    n_potentials_collabs = dict(Counter(liaisons_eventuelles[:,0]))
    components_weights   = [[min(n_potentials_collabs[i], n_potentials_collabs[j])] for i,j in liaisons_eventuelles[:, :2]]
        # détection de l'élève le moins lié aux autres (à aumoins une liaison)
    liaisons_eventuelles = np.concatenate((liaisons_eventuelles,  components_weights), axis = 1)

    # liaisons_weight
    weights = (10^6)*liaisons_eventuelles[:, 4] + (10^3)*liaisons_eventuelles[:, 3] + liaisons_eventuelles[:, 2]
        # RQ : On admet que :
        #    1) n_potentials_collabs > methodologies_percent > sujet_percent via :
        #       (10^6)*liaisons_eventuelles[:, 4] + (10^3)*liaisons_eventuelles[:, 3] + liaisons_eventuelles[:, 2]
        #    2) il est certain que liaisons_eventuelles[:, 4] étant le nombre de potentielles collaboration est prioritaire sur les deux autres
        #    néanmoins, nous admettons que methodologies_percent et prioritaire sur sujets_percent ce qu'il ne m'est pas possible d'attester à 100%
        #    d'où une éventuelle étude de la formule :
        #    lambda in ]0,1[ fixé où       weights = (10^3)*liaisons_eventuelles[:, 4] + lambda*liaisons_eventuelles[:, 3] + (1-lambda)*liaisons_eventuelles[:, 2]
        # RQ : Le nombre de potentielles collaboration est prioritaire sur les deux autres, il est possible de fusionner les colonnes 2 et 3 avant la fonction collaborations
    index_min_weight = np.argmin(weights, axis=0)
    e1, e2, *_       = liaisons_eventuelles[index_min_weight]
    liaisons_eventuelles = list(filter(lambda x : not (x[0] in (e1, e2) or x[1] in (e1, e2)), liaisons_eventuelles))

    if not liaisons_eventuelles : return (e1, e2), []
    liaisons_eventuelles = np.stack(liaisons_eventuelles, axis = 0)
    return (e1, e2), liaisons_eventuelles[:, :4]

def get_childs_affiliation(sujets_percent        : np.array,
                           methodologies_percent : np.array,
                           n_childs              : int) -> list :
    liaisons_eventuelles = np.array([[i,j,sujets_percent[i,j], methodologies_percent[i,j]] for i, j in product(range(n_childs), range(n_childs))])
        # RQ : il y a peut-être une optimisation à étudier sachant que j > i
    liaisons_eventuelles = liaisons_eventuelles[liaisons_eventuelles[:,2] < 100]
        # NB : suppression des duos d'élèves impossibles
    eleves_non_affiliables = set(range(n_childs)) - set(np.unique(liaisons_eventuelles[:, :2]))
        # NB : eleves_non_affiliables sont les indices de la liste des uuid_eleves
    eleves_non_affiliables_firstNames = [selected_childs[i]["firstName"][0] for i in eleves_non_affiliables]

    # obtention des groupes d'élèves
    childs_groups   = []
    eleves_affilies = set()
    while len(liaisons_eventuelles) > 0 :
        child_group, liaisons_eventuelles = collaborations(liaisons_eventuelles)
        childs_groups   += [child_group]
        eleves_affilies  = eleves_affilies | set(child_group)

    childs_groups_firstNames = [(selected_childs[childs_group[0]]["firstName"][0],
                                 selected_childs[childs_group[1]]["firstName"][0])
                                        for childs_group in childs_groups]

    eleves_non_affilies  = set(range(n_childs)) - eleves_non_affiliables - eleves_affilies
        # NB : eleves_non_affiliables sont les indices de la liste des uuid_eleves

    eleves_non_affilies_firstNames = [selected_childs[i]["firstName"][0] for i in eleves_non_affilies]

    # NEXT : Fonction d'insertion d'un eleve_non_affilié dans un duo existant

    return (childs_groups         , childs_groups_firstNames         ), \
           (eleves_non_affiliables, eleves_non_affiliables_firstNames), \
           (eleves_non_affilies   , eleves_non_affilies_firstNames   )

if   "etablissement_connaissances_connues" not in st.session_state : st.error("😕 BDD connexion error !"          )
elif "volontes"                            not in st.session_state : st.error("😕 BDD connexion error !"          )
elif "identification"                      not in st.session_state : st.error("😕 No valid identification !"      )
elif "selected_childs"                     not in st.session_state : st.error("😕 We don't have 'selected_childs'")
elif "child"  in st.session_state["identification"]["actual_role"] : st.error("😕 No utility into one child"      )
elif len(st.session_state["selected_childs"]) < 2                  : st.error("😕 Not enough 'selected_childs'"   )
else : # "teacher" ou "parent" where seance childs>1
    ##############################################
    ####  PHASE 1 : obtention des donnees  #######
    ##############################################
    etablissement_connaissances_connues = st.session_state["etablissement_connaissances_connues"]
    volontes                            = st.session_state["volontes"                           ]
    selected_childs                     = st.session_state["selected_childs"                    ]
        # RQ : selected_childs peut être obtevu via l'API de l'établissement en envoyant :
        #      uuid_élèves, (avec sécurisation de l'API)

    # connaissances acquises et, connaissances pouvant être apprises
    knowledge_childs = np.concatenate([child["knowledge_Model"] for child in selected_childs], axis=0).astype(int)     # M(n_childs x n_comp : [0,1,2,3])
    childs_know      = np.where(knowledge_childs             > 1, 1, 0)                                # M(n_childs x n_comp : [0,1])
    childs_tolearn   = to_learn(childs_know                           )                                # M(n_childs x n_comp : [0,1])
    childs_canlearn  = np.where(childs_tolearn - childs_know > 0, 1, 0)                                # M(n_childs x n_comp : [0,1])
        # RQ : Suivant le modèle prédictif, les connaissances actuelles de l'élèves peuvent apparaitre ou non dans la prédiction
        # => child_can learn = pred(childs_know)                                si connaissances actuelles non présentes
        # OU child_can_learn = pred(childs_know) - childs_know                  si connaissances actuelles présentes
        # OU child_can_learn = pred(childs_know) - childs_know  avec -1 -> 0    si connaissances actuelles partiellement présentes
            # RQ : le troisième cas plus général englobe les 2 autres

    # méthodes de travail possibles pour l'élève
    working_methods_childs     = np.concatenate([child["working_methods"    ] for child in selected_childs], axis=0).astype(int)    # M(n_childs x 4 : [0,1])
    working_viabilities_childs = np.concatenate([child["working_viabilities"] for child in selected_childs], axis=0).astype(int)    # M(n_childs x 4 : [0,1])
    working_childs             = working_methods_childs*working_viabilities_childs                                                # M(n_childs x 4 : [0,1])

    n_childs, n_comp = knowledge_childs.shape
    collaborations_possibilities = get_collaborations_possibilities(working_childs,
                                                                    childs_canlearn,
                                                                    childs_know,
                                                                    n_childs,
                                                                    n_comp)

    sujets_count       , sujets_percent        = get_sujets_percent       (collaborations_possibilities, n_comp)
    methodologies_count, methodologies_percent = get_methodologies_percent(collaborations_possibilities)

    affiliations = get_childs_affiliation(sujets_percent,
                                          methodologies_percent,
                                          n_childs)
    childs_groups                     = affiliations[0][0]
    childs_groups_firstNames          = affiliations[0][1]
    eleves_non_affiliables            = affiliations[1][0]
    eleves_non_affiliables_firstNames = affiliations[1][1]
    eleves_non_affilies               = affiliations[2][0]
    eleves_non_affilies_firstNames    = affiliations[2][1]





    # AFFICHAGE DES RESULTATS
    st.title("Création des duos d'élèves suivant leurs attentes et compétences relatives à la BDD.")

    0*"""
    with st.expander("Résultat des compétences communes aux attentes des élèves :"):
        col0, col1 = st.columns(2)
        col0.write(sujets_count)
        col1.write(sujets_percent)
    with st.expander("Résultat du nombre de volontés en accord entre les élèves :"):
        col0, col1 = st.columns(2)
        col0.write(methodologies_count)
        col1.write(methodologies_percent)
    """

    st.write(f"<h4>Sélection et description des duos d'élèves :</h4>", unsafe_allow_html=True)

    with st.expander("Regrouppements des élèves :", expanded=True):
        col1, col2 = st.columns(2)
        col1.write("Duos d'élèves :")
        col1.dataframe(pd.DataFrame(childs_groups_firstNames, columns = ["eleve1", "eleve2"]))
        if len(eleves_non_affiliables_firstNames) > 0 :
            col2.write("Elèves non affiliables :")
            col2.dataframe(pd.DataFrame(eleves_non_affiliables_firstNames, columns=["eleves_non_affiliables"]))
        if len(eleves_non_affilies_firstNames) > 0 :
            col2.write("Elèves non affilies :")
            col2.dataframe(pd.DataFrame(eleves_non_affilies_firstNames, columns = ["eleves_non_affilies"]))

    if childs_groups == [] : st.write("Il est impossible de créer un duo !")
    else :

        descriptions = ["description_eleves_affilies", "description_eleves_non_affiliables", "description_eleves_non_affilies"]
        description_eleves_affilies, description_eleves_non_affiliables, description_eleves_non_affilies = st.tabs(descriptions)

        with description_eleves_affilies :
            st.write("<h4>Description des caractéristiques associées aux duos d'élèves :</h4>", unsafe_allow_html=True)

            if len(childs_groups) == 1 : i_child_group = 0
            else : i_child_group = st.slider("Sélection d'un duo d'élèves :", 0, len(childs_groups) - 1, 0)
            n1          , n2           = childs_groups           [i_child_group]
            n1_firstName, n2_firstName = childs_groups_firstNames[i_child_group]

            with st.expander("Compétences du duo d'élèves :", expanded=False):

                col0, col1 = st.columns(2)
                col0.write(f"{n1_firstName} :")
                col1.write(f"{n2_firstName} :")
                col0.write("Compétences actuelles (0,1) :")
                col1.write("Compétences actuelles (0,1) :")
                col0.write(denumerizer(childs_know[n1:n1+1,:], etablissement_connaissances_connues)[0])
                col1.write(denumerizer(childs_know[n2:n2+1,:], etablissement_connaissances_connues)[0])
                    # RQ : les compétences actuelles [0,1,2,3] sont stockées dans la variable knowledge_childs

                col2, col3 = st.columns(2)
                col2.write("Travail attendu par l'élève :")
                col3.write("Travail attendu par l'élève :")
                col2.write(denumerizer(working_childs[n1:n1+1,:], volontes)[0])
                col3.write(denumerizer(working_childs[n2:n2+1,:], volontes)[0])

            st.write(f"<h4>Compétences concernées par la rencontre entre {n1_firstName} et {n2_firstName} :</h4>", unsafe_allow_html=True)
            col0, col1 = st.columns(2)
            col2, col3 = st.columns(2)
            col0.write(f"{n2_firstName} transmet à {n1_firstName}.")
            col0.write(denumerizer(collaborations_possibilities[n1,n2:n2+1,:,0], etablissement_connaissances_connues)[0])

            col1.write(f"{n1_firstName} et {n2_firstName} co-apprennent.")
            col1.write(denumerizer(collaborations_possibilities[n1,n2:n2+1,:,1], etablissement_connaissances_connues)[0])

            col2.write(f"{n1_firstName} transmet à {n2_firstName}.")
            col2.write(denumerizer(collaborations_possibilities[n1,n2:n2+1,:,2], etablissement_connaissances_connues)[0])

            col3.write(f"{n1_firstName} et {n2_firstName} révisent.")
            col3.write(denumerizer(collaborations_possibilities[n1,n2:n2+1,:,3], etablissement_connaissances_connues)[0])



        with description_eleves_non_affiliables :
            st.write("<h4>Description des caractéristiques associées élèves non affiliables :</h4>", unsafe_allow_html=True)
            for index_eleve, firstname in zip(eleves_non_affiliables, eleves_non_affiliables_firstNames) :

                col0, col1 = st.columns(2)
                col0.write(f"{firstname} :")
                col0.write("Compétences actuelles (0,1) :")
                col0.write(denumerizer(childs_know[index_eleve:index_eleve+1,:], etablissement_connaissances_connues)[0])
                    # RQ : les compétences actuelles [0,1,2,3] sont stockées dans la variable knowledge_childs

                col1.write("")
                col1.write("Travail attendu par l'élève :")
                col1.write(denumerizer(working_childs[index_eleve:index_eleve+1,:], volontes)[0])

        with description_eleves_non_affilies :
            st.write("<h4>Description des caractéristiques associées aux élèves non affiliés :</h4>", unsafe_allow_html=True)
            for index_eleve, firstname in zip(eleves_non_affilies, eleves_non_affilies_firstNames) :

                col0, col1 = st.columns(2)
                col0.write(f"{firstname} :")
                col0.write("Compétences actuelles (0,1) :")
                col0.write(denumerizer(childs_know[index_eleve:index_eleve+1,:], etablissement_connaissances_connues)[0])
                    # RQ : les compétences actuelles [0,1,2,3] sont stockées dans la variable knowledge_childs

                col1.write("")
                col1.write("Travail attendu par l'élève :")
                col1.write(denumerizer(working_childs[index_eleve:index_eleve+1,:], volontes)[0])




0*""" PROCEDURE DE CREATION DES DUOS PAR DECOUPAGE DU CHEMIN LE PLUS COURT
    import six
    import sys
    sys.modules['sklearn.externals.six'] = six
    import mlrose

    # Tableau du résultat relatif au problème de voyage de Salesperson
    fitness_dists = mlrose.TravellingSales(distances = distance_inter_eleves)
    problem_fit = mlrose.TSPOpt(length = n_child, fitness_fn = fitness_dists, maximize=False)
    best_state, best_fitness = mlrose.genetic_alg(problem_fit, mutation_prob = 0.2, max_attempts = 30, random_state = 2)
        # RQ : max_attemps est une valeur à optimiser suivant le paramètre n_eleves
    st.write(f'The best state found is: {best_state}')
    chemins = [(f"eleve_{e1}", f"eleve_{e2}", class_regroup_sum[e1,e2]) for e1, e2 in zip(best_state[:-1], best_state[1:])]
    chemins += [(f"eleve_{best_state[-1]}", f"eleve_{best_state[0]}", class_regroup_sum[best_state[-1],best_state[0]])]
    chemins = np.array(chemins)
    st.write(chemins)

    # Suppression des liaisons inter-élèves impossibles
    chemins = [(e1, e2, class_regroup_sum[e1,e2]) for e1, e2 in zip(best_state[:-1], best_state[1:])]
    chemins += [(best_state[-1], best_state[0], class_regroup_sum[best_state[-1],best_state[0]])]
    chemins = np.array(chemins)

    idx = np.where( chemins[:, 2] >= 100)[0]
    idx = set(idx) | set(idx+1)
    groups = np.split(chemins, idx)
    groups = [group for group in groups if len(group) >0]


    # raccordement du dernier chemin avec le premier s'ils sont séparés
    if   len(groups) == 0 : pass
    elif len(groups) == 1 :
        # A developper suppression d'une ligne telle que la somme des poids de groupes soit la plus faible possible
        # ici : simplification par la suppression de la ligne ayant le plus petit poid
        ind_max_value = groups[0][:,2].argmax(axis=0)
        groups = [groups[0][:ind_max_value,:],groups[0][ind_max_value+1:,:]]
        groups = [np.concatenate([groups[-1], groups[0]], axis=0)] + groups[1:-1]
    elif groups[0][0,2]<100 and groups[-1][-1,2]<100:
        groups = [np.concatenate([groups[-1], groups[0]], axis=0)] + groups[1:-1]



    sequence_groups = [group for group in groups if len(group) >  1]
    sequence_group  = np.concatenate(sequence_groups, axis = 0)
    sequence_child  = set(sequence_group[:,0]) & set(sequence_group[:,1])
    alone_groups    = [group for group in groups if len(group) <= 1]
    if alone_groups :
        alone_group     = np.concatenate(alone_groups, axis = 0)
        alone_child     = set(alone_group[:,0]) & set(alone_group[:,1])
    else:
        alone_group     = np.zeros((0))
        alone_child     = set()
        # ces enfants n'ont pas le moindre accord avec un autre

    for i in sequence_groups:
        st.write(i)
    st.write(alone_child)
    st.write(sequence_child)


    #st.write(group_child)
    #st.write(both_child)
    # python traveling saleperson problem in 4 dimension
    pair_sequence_groups   = [i for i in sequence_groups if len(i)%2!=0] # ERREUR POTENTIELLE : le dernier couple est potentiellement omis
    impair_sequence_groups = [i for i in sequence_groups if len(i)%2==0]
    st.write([i[::2,:2] for i in pair_sequence_groups])

    st.write(impair_sequence_groups)"""
0*""" Méthodes de création des duos depuis impair_sequence_groups
    METHODE 1 : Simple suppression d'une liaison extrême (0 ou -1)
    0--1--2--3--4 => 1--2--3--4
    puis utilisation de la méthode associée à pair_sequence_groups pour obtenir 1--2  3--4

    METHODE 2 : Simple suppression des liaisons associées au numéro pair
    0--1--2--3--4 => 0--1  2  3--4       via i in range(len(impair_sequence_group)%2), pour i = 1,  np.delete(impair_sequence_group, [max(0,2*i-1), 2*i], axis=0]
    puis utilisation de la méthode associée à pair_sequence_groups pour obtenir 0--1  3--4

    METHODE 3 : METHODE 2 avec sélection telle que la somme des poids gardés soit la plus faible possible

    METHODE 4 : METHODE 2 appliquée sur plusieurs impair_sequence_group avec étude des liaisons entre les élèves supprimés
    0--1--2--3--4 => 0--1  2  3--4 puis utilisation de la méthode associée à pair_sequence_groups pour obtenir
    a--b--c       => a--b  c puis utilisation de la méthode associée à pair_sequence_groups pour obtenir (même résultat ici)
    et 2--c   si poids(2--c) < 100
    la validité est mesurée par min(0--1  2  3--4,  a--b  c, 2--c)

    NOUVELLE METHODE 5 :
    1. selection du groupe d'élèves le plus valide
    2. suppression de ce groupe et liaisons associées
    3. répétition des etapes 1 et 2 jusqu'à ce que le tableau soit vide ou que toutes les valeurs soient supérieures à 100

    NOUVELLE METHODE 6 :
    ?? généraliser la méthode 5 sur des groupes de plus de 2 élèves"""
0*""" GENERATION VISUELLE DES ETAPES DE CREATION DES DUOS VIA CHEMIN LE PLUS COURT
    # https://mlrose.readthedocs.io/en/stable/source/tutorial2.html
    # https://sandipanweb.wordpress.com/2020/12/08/travelling-salesman-problem-tsp-with-python/


    # TESTS DE CLUSTERING
    import graphviz
    e = graphviz.Graph('G', filename='see_graphviz.gv', engine='neato', format='pdf') # Digraph or Graph


    e.attr('node', shape='ellipse') # sahpe in ["box", "diamond"], style='filled', color='lightgrey'
    for i in range(n_child) : e.node(f'child_{i}', label=f'child_{i}')
    for i, j in product(range(n_child), range(n_child)):
        if i <=j : continue
        e.edge(f'child_{i}', f'child_{j}', label=str(class_regroup_sum[i,j]), len='3.00')

    for i in range(n_child) : e.node(f'child_{i}f', label=f'child_{i}f')
    for i,j in zip(best_state[:-1], best_state[1:]):
        e.edge(f'child_{i}f', f'child_{j}f', label=str(class_regroup_sum[i,j]), len='1.5')
    e.edge(f'child_{best_state[-1]}f', f'child_{best_state[0]}f', label=str(class_regroup_sum[best_state[-1],best_state[0]]), len='1.00')

    for i in range(n_child) : e.node(f'child_{i}ff', label=f'child_{i}ff')
    for i,j,k in sequence_group:
        e.edge(f'child_{i}ff', f'child_{j}ff', label=str(k), len='1.5')

    e.attr(label=r'\n\nEntity Relation Diagram\ndrawn by NEATO')
    e.attr(fontsize='20')

    e.view()"""

# AFFICHAGE DES RESULTATS
"""
col0, col1 = st.columns(2)
col2, col3 = st.columns(2)
n1 = col0.slider('Number for the first child' , 0, len(bdd_eleves)-1, 1)
n2 = col1.slider('Number for the second child', 0, len(bdd_eleves)-1, 1)
col0.write(f"Elève {n1} :")
col1.write(f"Elève {n2} :")
col0.write("Compétences actuelles :")
col1.write("Compétences actuelles :")
col0.write(denumerizer(bdd_eleves[n1:n1+1,:], connaissances_entree_connues)[0])
col1.write(denumerizer(bdd_eleves[n2:n2+1,:], connaissances_entree_connues)[0])

col2.write("Travail attendu par l'élève : ")
col3.write("Travail attendu par l'élève :")
col2.write(denumerizer(wants[n1:n1+1,:], volontes)[0])
col3.write(denumerizer(wants[n2:n2+1,:], volontes)[0])

st.write(f"Compétences concernées par la rencontre entre l'élève {n1} et l'élève {n2} :")
st.write(denumerizer(class_regroup[n1,n2:n2+1,:], connaissances_entree_connues)[0])"""*0
