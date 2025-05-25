import streamlit as st
st.write("Nothing for the moment")

if   "etablissement_connaissances_connues"     not in st.session_state  : st.error("😕 BDD connexion error !"       )
elif "etablissement_connaissances_non_connues" not in st.session_state  : st.error("😕 BDD connexion error !"       )
elif "france_connaissances_connues"            not in st.session_state  : st.error("😕 BDD connexion error !"       )
elif "france_connaissances_non_connues"        not in st.session_state  : st.error("😕 BDD connexion error !"       )
elif "selected_childs"                         not in st.session_state  : st.error("😕 Childs are not selected !"   )
elif not st.session_state["selected_childs"]                            : st.error("😕 Not enough childs selected !")
#elif len(st.session_state["selected_childs"]) > 1                       : st.error("😕 Only one child can be selected !")
elif "teacher" not in st.session_state["identification"]["actual_role"] : st.error("😕 You are not a teacher !"     )
else :
    st.write("You are a teacher. That's why you can change datas about your students")


# RQ : Ajoût d'une page permettant de changer les compétences des élèves sans passer par une évaluation
    # 0. Ouverture de la BDD

    # 2. Multi-selection d'élèves (1 privilégiable)
    #   -> cela sera simplement symbolisé par un curseur nb élèves dans un premier temps
    # 3. Entrée des données à changer pour l'élève
    # Affichage des diverses données +

        # a. 2 cas : Si la connaissance est connue par le modèle, alors selection multiple
        #            Si non connue, la compétence va s'ajouter
