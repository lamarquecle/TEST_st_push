import numpy as np
import streamlit as st
from keras.models import load_model

def numerizer(X_connaissances_actuelles, france_connaissances_connues):
    connaissances_Numerise = [[int(i in connaissances_actuelles) for i in france_connaissances_connues] \
                                for connaissances_actuelles in X_connaissances_actuelles]
    connaissances_Numerise = np.array(connaissances_Numerise)
    connaissances_No_Numerise = [list(set(connaissances_actuelles) - set(france_connaissances_connues)) \
                                for connaissances_actuelles in X_connaissances_actuelles]
    return connaissances_Numerise, connaissances_No_Numerise


@st.cache_resource
def to_learn(connaissances_Numerise, model_file = "models/can_learn_model.h5"):
    # compétences à acquérir
    model = load_model(model_file)
    Y_pred = model.predict(connaissances_Numerise)
    Y_pred = np.around(Y_pred).astype(int)
    return Y_pred

@st.cache_resource
def to_learn_v2(connaissances_Numerise : np.array) :
    X = connaissances_Numerise
    cols_ones = np.ones((1, len(X))).T
    X_ones = np.hstack ((X, cols_ones)).astype(int)

    a = [[-2.  ,  0.  ,  0.  ,  0.  ,  0.  ,  0.,    0.  ,  0.  ,  0.  ], # -2 est remplaceable par tous nombres tq a[0,0]+b[0] < 0 et b[0] > 0
         [ 2.  , -3.  ,  0.  ,  0.  ,  0.  ,  0.,    0.  ,  0.  ,  0.  ],
         [ 0.  ,  0.  , -2.  ,  0.  ,  0.  ,  0.,    0.  ,  0.  ,  0.  ],
         [ 0.  ,  0.  ,  0.  , -2.  ,  0.  ,  0.,    0.  ,  0.  ,  0.  ],
         [ 0.  ,  0.  ,  2.  ,  2.  , -5.  ,  0.,    0.  ,  0.  ,  0.  ],
         [ 0.  ,  0.  ,  0.  ,  0.  ,  0.  , -2.,    0.  ,  0.  ,  0.  ],
         [ 0.  ,  0.  ,  0.  ,  0.  ,  0.  ,  2.,   -3.  ,  0.  ,  0.  ],
         [ 0.  ,  3.  ,  0.  ,  0.  ,  3.  ,  1.,    0.  , -3.  ,  1.  ], # RQ : 3+3+1+1 + (-3-6.5) < 0 good, -3 et remplaceable par -9 < (3+3+1+1)
         [ 0.  ,  0.  ,  0.  ,  0.  ,  0.  ,  0.,    0.  ,  0.  , -2.  ]]
    a = np.array(a).astype(float)
    """ BEFORE
        -8.99	8.02	0.19	0.24	-0.41	0.21	-0.24	-0.38	0.22
        0.2 	-8.36	0.19	0.23	-0.4	0.21	-0.24	3.49	0.22
        0.2 	-0.22	-8.87	0.23	5.6 	0.21	-0.24	-0.37	0.22
        0.2 	-0.22	0.19	-8.78	5.6 	0.21	-0.24	-0.36	0.22
        0.2 	-0.21	0.19	0.23	-7.35	0.21	-0.24	3.49	0.22
        0.2 	-0.21	0.18	0.23	-0.4	-8.95	7.44	1	0.22
        0.2 	-0.22	0.18	0.23	-0.41	0.21	-7.86	-0.36	0.22
        0.2 	-0.23	0.19	0.23	-0.41	0.21	-0.24	-5.34	0.22
        0.2 	-0.22	0.18	0.23	-0.4	0.21	-0.25	1.01	-9.13
    """
    b = [[ 1.  ,
          -1.  ,
           1.  ,
           1.  ,
          -3.  ,
           1.  ,
          -1.  ,
          -6.5 ,
           1.  ]]
    b = np.array(b).astype(float).T
    """ BEFORE
        3.61
        -3.42
        3.62
        3.35
        -7.47
        3.53
        -3.02
        -6.62
        3.58
    """
    model_weights = np.hstack ((a,b))
    Y     = np.dot(model_weights, X_ones.T).T
    Y_int = np.where(Y>0,1,0)
    return Y_int

    """ to_learn_v2 explain weights
        Si compétence sans ancêtres et auto-selectionnée :
                M_i_i = -2    M_i_(n+1) = 1
        Si la compétence a un seul ancêtre au rang j :
                M_i_i = -3    M_i_j = 2   M_i_(n+1) = -1
        Si la compétence demande la connaissance des ancêtres au rang j et k :
                M_i_i = -5    M_i_j = M_i_k = 2   M_i_(n+1) = -3
        Si la compétence demande la connaissance de k ancêtres au rang 1, 2, ..., k (similaire si 1, 5, 7) (rang des ancêtres != i) :
                M_i_i = -1 - 2*k      M_i_1 = ... = M_i_k = 2     M_i_(n+1) = 1 - 2*k
            RQ : pour plus de précisions : M_i_i < -(M_i_1 + ... + M_i_k) < M_i_(n+1) < -(M_i_1 + ... + M_i_k) + min(M_i_1, ..., M_i_k)
            RQ : Il est tout à fait concevable de mettre M_i_i = -inf
            RQ : Il est possible de mettre M_i_i = -min(M_i_1, ..., M_i_k) si -(M_i_1 + ... + M_i_k) < M_i_(n+1) < -(M_i_1 + ... + M_i_k) + min(M_i_1, ..., M_i_k)
                ! cela n'est pas valide dans le cadre de plusieurs possibilités d'obtention


        Si la competence i peut s'obtenir sous deux conditions c1 € [1, 3, 7], ou c2 € [1, 3, 9]   (i not in   c1 ou c2)
                | M_i_i < -(M_i_1 + M_i_3 + M_i_7) < M_i_(n+1) < -(M_i_1 + M_i_3 + M_i_7) + min(M_i_1, M_i_3, M_i_7)
            ET  | M_i_i < -(M_i_1 + M_i_3 + M_i_9) < M_i_(n+1) < -(M_i_1 + M_i_3 + M_i_9) + min(M_i_1, M_i_3, M_i_9)

            <=> | M_i_i < - MAX(M_i_1 + M_i_3 + M_i_7, M_i_1 + M_i_3 + M_i_9)
                | - MAX(M_i_1 + M_i_3 + M_i_7, M_i_1 + M_i_3 + M_i_9) < M_i_(n+1)
                | M_i_(n+1) < MIN[ -(M_i_1 + M_i_3 + M_i_7) + min(M_i_1, M_i_3, M_i_7),
                |                  -(M_i_1 + M_i_3 + M_i_9) + min(M_i_1, M_i_3, M_i_9)]
            RQ : Dans le cadre de plusieurs condidition où les poids autres que M_i_i et M_i_(n+1) sont connus, la formule plus générale est :
                    M_i_(n+1) € ]-(M_i_:), -(M_i_:) + min(M_i_:)[  où (: != i et n+1)
                    M_i_i >= min(M_i_:)
            RQ : Il n'est pas garanti de pouvoir toujours fournir des poids dans le cadre de plusieurs conditions via cette formule
                => l'IA via un RNN en a peut-être la possibilité mais rien n'est garanti
    """

def denumerizer(Y_pred, france_connaissances_connues):
    connaissances_Denumerise = [[j for i,j in zip(y_pred, france_connaissances_connues) if i] for y_pred in Y_pred]
    return connaissances_Denumerise

"""
        # RQ : On estime que l'appel à l'IA se fait via les phases suivantes :
        #          1. envoi de childs_know_Numerise, etablissement_connaissances_connues et etablissement_connaissances_non_connues
        #               RQ : etablissement_connaissances_non_connues n'est pas nécessaire mais utile pour l'amélioration future de l'IA
        #          2. dénumérisation de childs_know_Numerise puis renumérisation suivant france_connaissances_connues
        #          3. mise en place de l'IA
        #          4. dénumérisation de childs_tolearn puis renumérisation suivant etablissement_connaissances_connues
        #          5. réception de childs_tolearn
        # RQ : L'adaptation de etablissement_connaissances_connues à france_connaissances_connues se fait via une
        #      commande de mise à jour extérieure à la prédiction
        #          1. le serveur de l'établissement reçoit "france_connaissances_connues"
        #          2. réencode childs_know_Numerise au format "etablissement_connaissances_connues" sous le format "france_connaissances_connues"
        #          3. éventuel remplissage avec "knowledge_NotModel" pour chaque élèves soumis à "etablissement_connaissances_non_connues"
        #          4. mise à jour de la BDD associée aux élèves
        #          5. mise à jour de la BDD établissement via "etablissement_connaissances_connues" et "etablissement_connaissances_non_connues"
"""