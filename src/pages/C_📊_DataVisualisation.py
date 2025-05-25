import streamlit as st
import numpy
import pandas
from pandas import DataFrame
import plotly.express as px
from models.structure import numerizer, to_learn, denumerizer


def bar_chart_data_knowledge(chart_data_knowledge : DataFrame,
                             MAX_KNOWLEDGE        : int = 10) -> None :

    so_much_knowledge : bool = bool(MAX_KNOWLEDGE < len(chart_data_knowledge))
    born_max_knowledge : int = MAX_KNOWLEDGE if so_much_knowledge else len(chart_data_knowledge) - 1
    if so_much_knowledge :
        st.write("Il y a trop de compétences pour toutes les mettre sur le graphe")
    chart_data_knowledge = chart_data_knowledge.iloc[:born_max_knowledge + 1, :]

    fig = px.bar(chart_data_knowledge,
                 x="index",
                 y=["NA", "ECA","A", "T"],
                 # color=["NA", "ECA","A", "T"],
                 text_auto=True,
                 #pattern_shape_sequence=[".", "x", "+", ":"]
                 )
    fig.update_layout(
        title             = ".",
        title_font_family = "Times New Roman",
        title_font_color  = "black",
        yaxis_title       = "count",

        showlegend=True,
        legend=dict(
            orientation = "h",
            title       = "step",
            title_font_color="black",
            yanchor = "bottom",
            y       = 1,
            xanchor = "right",
            x       = 1),
        font=dict(
            family = "Times New Roman",
            #size   = "auto",
            weight = "normal",
            style  = "normal",
            color  = "RebeccaPurple"))
    fig.update_traces(#textfont_size="auto",
                        textposition="auto",
                        orientation="v",
                        cliponaxis=False)
    fig.update_xaxes(
                    title_text = "knowledge",
                    title_font = {"size"   : 20,
                                  "family" : "Arial"},
                    tickangle = 30,
                    #range     = [-0.5, born_max_knowledge + 0.5],
                    showline  = False, linewidth = 2, linecolor = 'black')
    st.plotly_chart(fig)

def get_chart_data_knowledge(childs : list, france_connaissances_connues : list) -> DataFrame :
    childs_knowledge_Numerise = numpy.concatenate([child["knowledge_Model"] for child in childs], axis=0)
    connaissances_No_Numerise = [child["knowledge_NotModel"] for child in childs]
        # RQ : la faisabilitté d'une concaténation est à étudier
        #      Actuellement refusé car 2 enfants peuvent être dans des établissements différents
    connaissances_Denumerise = denumerizer(childs_knowledge_Numerise, france_connaissances_connues)


    childs_knowledge_Numerise = childs_knowledge_Numerise.astype(int)
    f = lambda x : numpy.identity(4)[x] # [0,2] => [[1,0,0,0], [0,0,1,0]]
    childs_knowledge_habilities = numpy.apply_along_axis(f, 1, childs_knowledge_Numerise).astype(int)
    knowledge_habilities = numpy.sum(childs_knowledge_habilities,axis=0)
    chart_data_knowledge = DataFrame(
                                knowledge_habilities,
                                columns=["NA", "ECA","A", "T"],
                                index=etablissement_connaissances_connues)
    chart_data_knowledge["index"] = chart_data_knowledge.index
    return chart_data_knowledge

def get_chart_data_can_learn(childs : list, france_connaissances_connues : list) -> DataFrame :
    # Prédiction
    childs_knowledge_Numerise = numpy.concatenate([child["knowledge_Model"] for child in childs], axis=0)

    childs_tolearn   = to_learn(childs_knowledge_Numerise)                                # M(n_childs x n_comp : [0,1])
    childs_canlearn  = numpy.where(childs_tolearn - childs_knowledge_Numerise > 0, 1, 0)
    connaissances_tolearn_Denumerise = denumerizer(childs_canlearn, france_connaissances_connues)

    class_canknow  = numpy.where(childs_knowledge_Numerise > 1, 1, 0)
    class_canknow  = numpy.sum(class_canknow  , axis=0)
    class_canlearn = numpy.sum(childs_canlearn, axis=0)

    class_canknow  = numpy.where(childs_knowledge_Numerise > 1, 1, 0)
    answers = childs_canlearn + 2*class_canknow
        # 0 : it isn't possible to learn
        # 1 : can learn
        # 2 : is learn

    f = lambda x : numpy.identity(3)[x]
    numbers_count = numpy.apply_along_axis(f, 1, answers).astype(int)
    numbers_count = numpy.sum(numbers_count,axis=0)
    chart_data_can_learn = DataFrame(numbers_count, columns=["can't learn","can learn", "know"], index=france_connaissances_connues)

    return chart_data_can_learn



if   "etablissement_connaissances_connues"     not in st.session_state : st.error("😕 BDD connexion error !"    )
elif "etablissement_connaissances_non_connues" not in st.session_state : st.error("😕 BDD connexion error !"    )
elif "france_connaissances_connues"            not in st.session_state : st.error("😕 BDD connexion error !"          )
elif "france_connaissances_non_connues"        not in st.session_state : st.error("😕 BDD connexion error !"          )
elif "identification" not in st.session_state :
    st.error("😕 No valid identification !"  )
    st.write("N.")
    etablissement_connaissances_connues     = st.session_state["etablissement_connaissances_connues"    ]
    etablissement_connaissances_non_connues = st.session_state["etablissement_connaissances_non_connues"]
    france_connaissances_connues            = st.session_state["france_connaissances_connues"           ]
    france_connaissances_non_connues        = st.session_state["france_connaissances_non_connues"       ]

    connaissances_par_defaut=st.checkbox('Connaissances actuelles par defaut')
    connaissances_actuelles_par_defaut = ["Racine carrée", "Expressions littérales", "Priorités opératoires", "Catégories de triangles", "Probabilités"] if connaissances_par_defaut else []
                                            # <=> [0, 1, 1, 1, 0, 1, 0, 0, 0] + ["Probabilités"]
    childs_know = [st.multiselect(
        "Quelles sont les connaissances actuelles de l'élève ?", etablissement_connaissances_connues + etablissement_connaissances_non_connues,
        default = connaissances_actuelles_par_defaut)]
    childs_know_Numerise, connaissances_No_Numerise = numerizer(childs_know, etablissement_connaissances_connues)

    # Prédiction
    childs_tolearn   = to_learn(childs_know_Numerise)                                # M(n_childs x n_comp : [0,1])
    childs_canlearn  = numpy.where(childs_tolearn - childs_know_Numerise > 0, 1, 0)
    connaissances_tolearn_Denumerise = denumerizer(childs_canlearn, france_connaissances_connues)

    # résultats obtenus
    st.title("Prédiction des compétences à acquérir.")
    st.write("Compétences hors modèle prédictif :\n", connaissances_No_Numerise[0])
    st.write("Compétences prédites à acquérir :\n"  , connaissances_tolearn_Denumerise [0])
elif not st.session_state["selected_childs"] : st.error("😕 Not enough childs selected !")
elif "child" in st.session_state["identification"]["actual_role"] :
    st.write("C.")
    etablissement_connaissances_connues     = st.session_state["etablissement_connaissances_connues"    ]
    etablissement_connaissances_non_connues = st.session_state["etablissement_connaissances_non_connues"]
    france_connaissances_connues            = st.session_state["france_connaissances_connues"           ]
    france_connaissances_non_connues        = st.session_state["france_connaissances_non_connues"       ]
        # RQ : Ces deux variables sobnt issues de la BDD

    childs = st.session_state["selected_childs"]
    chart_data_knowledge = get_chart_data_knowledge(childs, france_connaissances_connues)
    chart_data_can_learn = get_chart_data_can_learn(childs, france_connaissances_connues)

    st.title("Compétences des élèves sélectionnés entre les différentes notions.")
    bar_chart_data_knowledge(chart_data_knowledge)
        # RQ : Ajout des compétences non connues de chaque élèves

    st.title("Capacité d'apprentissage des différentes notions.")
    st.bar_chart(chart_data_can_learn)
        # NB : "france_connaissances_connues" a un ordre aléatoire sur X_axis
        # garder le même ordre serait apprécié
elif not st.session_state["selected_childs"]   : st.error("😕 We don't have enough 'selected_childs'")
elif "parent" in st.session_state["identification"]["actual_role"] :
    st.write("P.")
    etablissement_connaissances_connues     = st.session_state["etablissement_connaissances_connues"    ]
    etablissement_connaissances_non_connues = st.session_state["etablissement_connaissances_non_connues"]
    france_connaissances_connues            = st.session_state["france_connaissances_connues"           ]
    france_connaissances_non_connues        = st.session_state["france_connaissances_non_connues"       ]
        # RQ : Ces deux variables sobnt issues de la BDD

    childs = st.session_state["selected_childs"]
    chart_data_knowledge = get_chart_data_knowledge(childs, france_connaissances_connues)
    chart_data_can_learn = get_chart_data_can_learn(childs, france_connaissances_connues)

    st.title("Compétences des élèves sélectionnés entre les différentes notions.")
    bar_chart_data_knowledge(chart_data_knowledge)
        # RQ : Ajout des compétences non connues de chaque élèves

    st.title("Capacité d'apprentissage des différentes notions.")
    st.bar_chart(chart_data_can_learn)
        # NB : "france_connaissances_connues" a un ordre aléatoire sur X_axis
        # garder le même ordre serait apprécié

else :
    st.write("T.")
    etablissement_connaissances_connues     = st.session_state["etablissement_connaissances_connues"    ]
    etablissement_connaissances_non_connues = st.session_state["etablissement_connaissances_non_connues"]
    france_connaissances_connues            = st.session_state["france_connaissances_connues"           ]
    france_connaissances_non_connues        = st.session_state["france_connaissances_non_connues"       ]
        # RQ : Ces deux variables sobnt issues de la BDD

    childs = st.session_state["selected_childs"]
    chart_data_knowledge = get_chart_data_knowledge(childs, france_connaissances_connues)
    chart_data_can_learn = get_chart_data_can_learn(childs, france_connaissances_connues)


    st.title("Compétences des élèves sélectionnés entre les différentes notions.")
    bar_chart_data_knowledge(chart_data_knowledge)
        # RQ : Ajout des compétences non connues de chaque élèves

    st.title("Capacité d'apprentissage des différentes notions.")
    st.bar_chart(chart_data_can_learn)
        # NB : "france_connaissances_connues" a un ordre aléatoire sur X_axis
        # garder le même ordre serait apprécié
