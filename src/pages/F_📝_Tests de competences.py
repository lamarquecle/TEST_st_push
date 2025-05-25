import streamlit as st
import requests
import numpy as np
import datetime
import uuid

API_URL='http://fastapi:8502'


def st_create_evaluation(etablissement_connaissances_connues, selected_childs_uuid):
    with st.expander("Création de l'évaluation :", expanded=False):
        with st.form(key="tests_creator"):
            titre     = st.text_area ("Titre de l'évaluation :")
            categorie = st.radio     ("Sélectionner la catégorie de l'évaluation :", ["CS", "DM", "CR"])
            beginning = st.date_input("Date de distribution de l'évaluation aux élèves :")
            collecte  = st.date_input("Date de rendu des élèves :")
            rendu     = st.date_input("Date de rendu de l'enseignant :")
            knowledges = st.multiselect("Quels sont les connaissances utilisées ?", etablissement_connaissances_connues, [])
            knowledge_NotModel = []#st.session_state["etablissement_connaissances_non_connues"       ]


            if st.form_submit_button (label="Save test", help="Click to save") :
                new_evaluation = {
                    "titre"     : titre,
                    "uuid"      : str(uuid.uuid4()),
                    "category" : categorie, # évaluation surveillé, evaluation à la maison, evaluation rapide
                    "beginning" : beginning.__str__(),
                    "collecte"  : collecte .__str__(),
                    "rendu"     : rendu    .__str__(),
                    "knowledge_model"   : knowledges,
                        # RQ : Ceci devrait être une liste de int pour structurer au format
                        # De premiers test avec List[compétences] sotn faits, puis cela sera à numériser
                        # avant l'envoi à l'api
                    "knowledge_NotModel": knowledge_NotModel,

                    "childs_evaluated"  : selected_childs_uuid
                        # NB : n'est-ce pas aux élèves que l'on doit assigner k'uuid du test ?
                    #"childs_non_evaluated" : ["uuid5"],
                    #"classe_evaluatede"  : ["class_uuid"]
                    }

                # INSERTION DE CETTE NOUVELLE EVALUATION DANS LA DB
                url = API_URL+f'/add_evaluation/'
                response = requests.post(url, json=new_evaluation, headers=headers)


                # Vérifier la réponse
                if response.status_code == 200:
                    st.success('The assessment is created !', icon="✅")
                    #st.session_state['evaluations'] += [new_evaluation]
                else:
                    st.error("😕 Request failed !")

def st_correction_evaluation_description(user_uuid):
    url = API_URL+f'/user/{user_uuid}/evals'


    headers = {
            "accept" : "application/json",
            "Authorization": f'Bearer {st.session_state["access_token"]}'}
    accessible_evals_encode = requests.get(url, headers=headers)
    accessible_evals = accessible_evals_encode.json()
    if accessible_evals_encode.status_code != 200 : st.warning("😕 Error to find evals from API")

    evaluations = accessible_evals
        # NB : la restriction aux élèves sélectionés est omise contrairement au cadre
        #      "parent" ou "child".
        # RQ : des conditions préliminaires de tri sont à faire naître ici
        #      (classe, niveau, selected_childs) et respecté par tous les élèves à selectionner
        # NB : il peut être accepté que la fonctionnaligé get soit mise en place juste après la connexion
        #      à la place de faire l'appel ici
    evaluations_title = list(map(lambda x:x["titre"], evaluations))
    try    : st.session_state['evaluations_select_index'] = evaluations_title.index(evaluation_select["title"])
    except : st.session_state['evaluations_select_index'] = 0

    # if evaluation_title == [] or

    evaluations_select_title = st.radio(
        "Sur quelle évaluation désirez-vous entrer les compétences d'élèves ?",
        evaluations_title, index=st.session_state['evaluations_select_index'] , key="evaluations_select_title")
        # RQ : compléter cette portion de telle sorte à ce lorsqu'une evaluations_select_title est sélectionnée,
        #      le rechargement de la page montre le choix et changement effectué (?cf var index)
    evaluations_select = [i for i in evaluations if i["titre"]==evaluations_select_title]
    evaluation_select = evaluations_select[0]
    if len(evaluations_select) > 1 : st.info("😕 2 évaluations avec un même titre !", icon="🚨")

    return evaluation_select

0*"""
    #######################################
    ######  VARIABLES DESCRIPTION  ########
    #######################################

    user : dictionary with user's description = st.session_state["identification"]

    accessible_evals : dict of evaluations in relation with the user = API(/user/{user_uuid}/evals)
    evaluations : accessibles_evals in relation with selected_clilds
    evaluation_select : evaluation select from evaluations = (radio button)

    selected_childs : childs selected
    childs_evaluated : childs in the evaluation
    childs_evaluated : childs selected in the evaluation = selected_childs INTER childs_evaluated


"""

#if "evaluations" not in st.session_state : st.error("😕 BDD connexion error !") # NB "etablissement connaissances connues" est aussi utilisé
if False : pass
elif "identification" not in st.session_state : st.error("😕 No valid identification !")
elif  "selected_childs" not in st.session_state: st.error("😕 We don't have 'selected_childs'")
#elif len(st.session_state["selected_childs"]) < 2    : st.error("😕 No utility to select 'selected_childs'")
elif "child" in st.session_state["identification"]["actual_role"] :
    st.write("C.")
    st.title("Tests de compétences into the child")

    st.write(st.session_state["identification"])

        # RQ : Cela demande au préalable que les résultats de chaque évaluations
        # auxquelles l'élève a participé soient répertoriées sur ses données
        # child_evaluations = [evaluations]
        # evaluation = {"evaluation_id":
        #               "results": ... }
        # NB : dans le cadre actuel, toutes les évaluations sont importées puis
        #  triées suivant l'existence ou non de l'uuid de l'élève dans les participants

    user_uuid = st.session_state["identification"]["uuid"]
    headers = {
            "accept" : "application/json",
            "Authorization": f'Bearer {st.session_state["access_token"]}'}
    accessible_evals_encode = requests.get(API_URL+f'/user/{user_uuid}/evals', headers=headers)
    accessible_evals = accessible_evals_encode.json()
        # RQ : actuellement, user peut acceder à toutes les evaluations
        #    par la suite "etablissement_evaluations", "accessible_evaluations", "selected_evaluations"


    child_uuid = st.session_state["selected_childs"][0]["uuid"]
    evaluations = [accessible_eval for accessible_eval in accessible_evals if child_uuid in accessible_eval["childs_evaluated"]]

    evaluation_name = st.radio(
        "Sur quelle évaluation désires tu avoir des informations ?",
        list(map(lambda x:x["titre"], evaluations)))

    evaluation_select = [i for i in evaluations if i["titre"]==evaluation_name]
    if len(evaluation_select) > 1 : st.info("😕 2 évaluations avec un même titre !")
    evaluation_select = evaluation_select[0]

    st.session_state['evaluation_select_id'] = evaluations.index(evaluation_select)

    st.write(evaluation_select)
elif "parent" in st.session_state["identification"]["actual_role"] :
    st.write("P.")
    if len(st.session_state["selected_childs"]) != 1 : st.error("😕 You should select one child !")
    else :
        st.write("Tests de compétences into one of your childs")

        user_uuid = st.session_state["identification"]["uuid"]
        headers = {
            "accept" : "application/json",
            "Authorization": f'Bearer {st.session_state["access_token"]}'}
        accessible_evals_encode = requests.get(API_URL+f'/user/{user_uuid}/evals', headers=headers)
        accessible_evals = accessible_evals_encode.json()
        child_uuid = st.session_state["selected_childs"][0]["uuid"]
        evaluations = [accessible_eval for accessible_eval in accessible_evals if child_uuid in accessible_eval["childs_evaluated"]]

        evaluation_name = st.radio(
            "Sur quelle évaluation désires tu avoir des informations ?",
            list(map(lambda x:x["titre"], evaluations)))
        evaluation_select = [i for i in evaluations if i["titre"]==evaluation_name]
        if len(evaluation_select) > 1 : st.info("😕 2 évaluations avec un même titre !")
        elif not evaluation_select : st.info("😕 No assessment selected !")
        evaluation_select = evaluation_select[0]

        st.session_state['evaluation_select_id'] = evaluations.index(evaluation_select)


        st.write(evaluation_select)
elif "teacher" in st.session_state["identification"]["actual_role"] :
    st.title("Tests de compétences")


    headers = {
            "accept" : "application/json",
            "Authorization": f'Bearer {st.session_state["access_token"]}'}

    etablissement_connaissances_connues     = st.session_state["etablissement_connaissances_connues"    ]
    etablissement_connaissances_non_connues = st.session_state["etablissement_connaissances_non_connues"]
                    # NB : Nous admettons leur existence dans la BDD

    user_uuid = st.session_state["identification"]["uuid"]


    selected_childs = st.session_state["selected_childs"]
        # NB : il est discutable de prendre "selected_childs" ou "etablissement_childs"
        #      cependant, "etablissement_childs" permet à coup sur d'avoir tous les élèves evaluated par le contrôle
    selected_childs_uuid = list(map(lambda x:x["uuid"], selected_childs))
        # RQ : il y a débat entre la selection de "accessible_childs" et "selected_childs"

    _ = st_create_evaluation(etablissement_connaissances_connues, selected_childs_uuid)


    evaluation_select = st_correction_evaluation_description(user_uuid)

    evaluation_uuid                     = evaluation_select["uuid"]
    childs_evaluated_uuid               = evaluation_select["childs_evaluated"]
    evaluation_connaissances_attendues  = evaluation_select["knowledge_model"] # ex : = ["Priorités opératoires","Expressions littérales"]
    evaluation_connaissances_attendues_index_from_etablissement = list(map(lambda x : etablissement_connaissances_connues.index(x), evaluation_connaissances_attendues))


    childs_evaluated_and_selected           = list(filter(lambda x: x["uuid"] in childs_evaluated_uuid, selected_childs))
    childs_evaluated_and_selected_uuid      = list(map   (lambda x: x["uuid"], childs_evaluated_and_selected))
    childs_evaluated_and_selected_firstName = list(map   (lambda x: x["firstName"][0], childs_evaluated_and_selected))

    with st.expander("Mise à jour de l'évaluation :"):
        with st.form(key="évaluation_modifications"):
            titre     = st.text_area ("Titre de l'évaluation :"                    , evaluation_select["titre"])
            categorie = st.radio     ("Sélectionner la catégorie de l'évaluation :", ["CS", "DM", "CR"],
                                      index = ["CS", "DM", "CR"].index(evaluation_select["category"]))
            beginning     = st.date_input("Date de distribution de l'évaluation aux élèves :",
                                        datetime.datetime.strptime(evaluation_select["beginning"], '%Y-%m-%d'))
            collecte  = st.date_input("Date de rendu des élèves :",
                                        datetime.datetime.strptime(evaluation_select["collecte"], '%Y-%m-%d'))
            rendu     = st.date_input("Date de rendu de l'enseignant :",
                                        datetime.datetime.strptime(evaluation_select["rendu"], '%Y-%m-%d'))
            knowledges = st.multiselect("Quels sont les connaissances utilisées ?", st.session_state["etablissement_connaissances_connues"], evaluation_select["knowledge_model"])
            knowledge_NotModel = evaluation_select["knowledge_NotModel"] # RQ : à adapter suivant la même configuration que la ligne du dessus plus tard

            childs_evaluated = st.multiselect(
                            "Tu désires te renseigner sur quel(s) enfants(s) ?",
                            options = evaluation_select["childs_evaluated"], # selected_childs_uuid,
                            default = childs_evaluated_and_selected_uuid) # evaluation_select["childs_evaluated"]
                # NB : default = evaluation_select["childs_evaluated"]
                #      est actuellement refusé car les élèves de l'évaluation ne sont pas nécessairement
                #      dans l'évaluation => ERROR
            if st.form_submit_button (label="Modification test", help="Click to save") :
                new_evaluation = {
                    "titre"     : titre,
                    "uuid"      : evaluation_select["uuid"],
                    "category"  : categorie, # évaluation surveillé, evaluation à la maison, évaluation rapide
                    "beginning" : beginning.__str__(),
                    "collecte"  : collecte .__str__(),
                    "rendu"     : rendu    .__str__(),
                    "knowledge_model"   : knowledges,
                        # RQ : Ceci devrait être une liste de int pour structurer au format
                        # De premiers test avec List[compétences] sotn faits, puis cela sera à numériser
                        # avant l'envoi à l'api
                    "knowledge_NotModel": knowledge_NotModel,
                    "childs_evaluated"  : childs_evaluated
                        # NB : n'est-ce pas aux élèves que l'on doit assigner k'uuid du test ?
                    #"childs_non_evaluated" : ["uuid5"],
                    #"classe_evaluatede"  : ["class_uuid"]
                    }

                url = API_URL+f'/delete_evaluation/'
                response = requests.post(url, json=evaluation_select, headers=headers)

                url = API_URL+f'/add_evaluation/'
                response = requests.post(url, json=new_evaluation, headers=headers)


                # Vérifier la réponse
                if response.status_code == 200:
                    st.write("Requête de mise à jour réussie !")
                    st.experimental_rerun()
                else:
                    st.write("Échec de la requête :", response.status_code)


    if st.button('Suppression', key=f"suppression_évaluation"):
        url = API_URL+f'/delete_evaluation/'
        response = requests.post(url, json=evaluation_select, headers=headers)

        # Vérifier la réponse
        if response.status_code == 200:
            #st.session_state['evaluation_select_id'] = None
            st.experimental_rerun()
            st.write("Requête réussie !")
        else:
            st.write("Échec de la requête :", response.status_code)
            st.write(response.text)  # Afficher le contenu de la réponse en texte brut


    if not childs_evaluated_and_selected :
        st.info("😕 Aucun des élèves sélectionés ne sont présents sur ce test !", icon="🚨")
    else :
        childs_evaluated_and_selected_knowledge = np.concatenate([child["knowledge_Model"] for child in childs_evaluated_and_selected], axis=0).astype(int)
        childs_evaluated_and_selected_knowledge = childs_evaluated_and_selected_knowledge[:,evaluation_connaissances_attendues_index_from_etablissement]

        n_lines = len(evaluation_connaissances_attendues)
        n_cols  = len(childs_evaluated_and_selected)

        with st.expander("Mise à jour des compétences d'élèves :"):
            if not evaluation_connaissances_attendues :
                st.write("Aucunes compétences n'a été associée à l'évaluation !")
            else :
                with st.form(key="compétences_modifications"):
                    # Numérisation des connaissances attendues dans l'évaluation suivant etablissement_connaissances_connues
                    #connaissances_attendues_numerise, _ = numerizer(evaluation_connaissances_attendues, etablissement_connaissances_connues)
                    #st.write( connaissances_attendues_numerise)
                        # RQ : on admet que les connaissances attendues sont connues par le modèle
                        # Sinon, faire un espace de sélection d'une notion suivant de teste donné (env<=> similarity)
                    #connaissances_attendues_numerise_binar = np.max(connaissances_attendues_numerise, axis= 0)
                    #st.write(connaissances_attendues_numerise_binar)
                    #evaluation_connaissances_attendues_index_from_etablissement = [ind for ind, val in enumerate(etablissement_connaissances_connues) if val in evaluation_connaissances_attendues]


                    X = np.zeros((n_lines, n_cols))
                    table_cols_name = [st.columns([1]*(n_cols+1)) for i in range(n_lines+1)]
                    for n_row, table_row in enumerate(table_cols_name):
                        for n_col, table_col in enumerate(table_row):
                            if n_row == 0 and n_col > 0:
                                word = childs_evaluated_and_selected_firstName[n_col-1]
                                table_cols_name[n_row][n_col].write(word)
                            elif n_row > 0 and n_col == 0 :
                                word = evaluation_connaissances_attendues[n_row-1]
                                table_cols_name[n_row][n_col].write(word)
                            elif n_row != 0 and n_col != 0 :
                                value = childs_evaluated_and_selected_knowledge[n_col-1, n_row-1]
                                key = f"selectcompetences_{n_row}_{n_col}"
                                #X[n_row-1][n_col-1] = table_cols_name[n_row][n_col].checkbox("", value = value, key = key)
                                _ = table_cols_name[n_row][n_col].select_slider(
                                                                "hidden",
                                                                label_visibility="hidden",
                                                                options=["NA", "ECA", "A", "T"],
                                                                value=["NA", "ECA", "A", "T"][value],
                                                                key=key)
                                X[n_row-1][n_col-1] = ["NA", "ECA", "A", "T"].index(_)


                    transmission = st.form_submit_button (label="Modification test", help="Click to save")
                    if transmission:
                        # RQ : Cela demande au préalable que les résultats de chaque évaluations
                        # auxquelles l'élève a participé soient répertoriées sur ses données
                        # child_evaluations = [evaluations]
                        # evaluation = {"evaluation_id":
                        #               "results_model": ...
                        #               "results_notModel": ... }
                        childs_results = np.transpose(X, (1,0))
                        for child, child_results in zip(childs_evaluated_and_selected, childs_results) :
                            evaluation = {"uuid": evaluation_uuid,
                                       "results_model": child_results,
                                       "results_notModel": [] } # RQ : non pris en compte

                            # i
                            child_index = None
                            for i_child, selected_child in enumerate(selected_childs):
                                if selected_child["uuid"]==child["uuid"] :
                                    child_index=i_child
                                    break

                            child_evaluations = st.session_state["selected_childs"][i_child]["results"]
                            in_child_evaluations = False
                            for i_eval, child_evaluation in enumerate(child_evaluations):
                                if child_evaluation["uuid"]==evaluation["uuid"] :
                                    in_child_evaluations = i_eval
                                    break

                            if in_child_evaluations == False :
                                st.session_state["selected_childs"][i_child]["results"] += [evaluation]
                            else : # in_evaluation in |[0, 1, ...]|
                                st.session_state["selected_childs"][i_child]["results"][i_eval] = evaluation

                            # maj de "knowledge_Model" suivant evaluation["results_model"]
                            for i_evaluation_competence, indice_evaluation_connaissance_attendue in enumerate(evaluation_connaissances_attendues_index_from_etablissement) :
                                i_competence = indice_evaluation_connaissance_attendue
                                st.session_state["selected_childs"][i_child]["knowledge_Model"][0][i_competence] = \
                                    evaluation["results_model"][i_evaluation_competence]
                                    #<=>st.session_state["selected_childs"][i_child]["evaluations"][i_eval][i_evaluation_competence]

                        # SAUVEGARDE DES DONNEES DANS LA BDD ETABLISSEMENT
                        evaluation = {
                            "uuid" : evaluation_uuid,
                            "childs_uuid" : childs_evaluated_and_selected_uuid,
                            "childs_competences" : X.tolist(),
                            "etablissement_connaissances_connues" : etablissement_connaissances_connues}

                        url = API_URL+f'/habilities_evaluation/'
                        response = requests.post(url, json=evaluation, headers=headers)
                        if response.status_code == 200:
                            st.success('Skills are saves !', icon="✅")
                            #st.experimental_rerun()
                        else:
                            st.error("Échec de sauvegarde des compétences élèves sur l'évaluation sélectionné dans la DB")





        st.write("<h2>Communication des nouvelles compétences.</h2>", unsafe_allow_html=True)
        cols = st.tabs(childs_evaluated_and_selected_firstName)
        for i_child_evaluated_and_selected, child_evaluated_and_selected, col in zip(range(len(childs_evaluated_and_selected)), childs_evaluated_and_selected, cols):
            # OK knowledge_model
            habilities = {}
            for evaluation_connaissance_attendue in evaluation_connaissances_attendues :
                index_evaluation_connaissance_attendue = etablissement_connaissances_connues.index(evaluation_connaissance_attendue)
                index_hability = child_evaluated_and_selected["knowledge_Model"][0][index_evaluation_connaissance_attendue]
                hability = ["NA", "ECA", "A", "T"][int(index_hability)]
                habilities[evaluation_connaissance_attendue] = hability
                    # RQ : la liste ["NA", "ECA", "A", "T"] est utilisée sur de multiples pages
                    #   ->? Mise en place d'une variable générale ?
                    # RQ : Dans le cadre où hability in ["NA", "ECA"], une précision plus précise des
                    #      compétences peut être mise en place via :
                    #         -> celles demandées pour l'acquérir (notions précédentes)
                    #         -> les actions d'entraînnement possibles pour l'acquérir (exercices sur la notion)
            # RQ : ajouter un deuxième for sur evaluation_select["knowledge_NotModel"]

            text_actual_eval = "\n\t\t\t\t".join([""] + [f"- {k} : {v}" for k, v in habilities.items()])

            with col:
                text = f"""Chers parents de {child_evaluated_and_selected["firstName"][0]} :

                Sur l'évaluation effectuée le {evaluation_select["collecte"]} en mathématiques, voici le bilan associé à ses compétences :{text_actual_eval}"""
                # RQ : les sous-catégories peuvent se formuler ainsi :
                # - Théorème de Pythagore : Non acquis
                #      - Racine carrée : Non acquis
                #      - Equations du premier degré : Acquis
                #      - Catégories de triangles : Acquis
                courriel_content = st.text_area("hidden", label_visibility="hidden", value=text, height=20+35*text.count("\n")+100)
                    # NB : height = ax+b où a et b sont à définir

                if st.button('Envoi', key=f"envoi_{i_child_evaluated_and_selected}"):
                    st.write(f'Message envoyé aux parents de {child_evaluated_and_selected["firstName"][0]} :')

