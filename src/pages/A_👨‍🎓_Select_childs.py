import streamlit as st

############################
##   CHILDREN SELECTION   ##
############################

def get_childs() :
    accessible_childs : list                = st.session_state["accessible_childs"]
    accessible_childs_firstName : list[str] = [accessible_child["firstName"][0] for accessible_child in accessible_childs]
        # RQ : Dans cette construction d'identification via "firstName", on admet leur unicité
        #      => mise en place d'un changement via les uuid ?
        #      cela est possible dans le cadre d'un affichage ordonné mais impossible avec st.mutiselect
        #      ! il n'a pas été détecté de solutions pour remplacer "firstName" par "uuid"
        #        dans le multiselect tout en gardant les "firstName" à vue
        #      ?=> remplacer "firstName" par "firstName" + " " + "lastName"

    if "selected_childs_firstName" in st.session_state :
        default_selected_childs_firstName : list[str] = st.session_state["selected_childs_firstName"]
    else :
        default_selected_childs : list = st.session_state["selected_childs"]
        #city = st.multiselect(
        #            "Select the city :",
        #            options = df["City"].unique(),
        #            default = df["City"].unique())
        #class = st.multiselect(
        #            "Select the class :",
        #            options = df["Class"].unique(),
        #            default = df["Class"].unique())
        #df_selection = df.query(" City == @city & Class == @class")
        default_selected_childs_firstName : list[str] = [default_selected_child["firstName"][0] for default_selected_child in default_selected_childs]
            # RQ : cette variable peut être restreinte suivant des choix (établissement, classe, niveau, compétences, ...)

    with st.form("selected_childs_firstName_form"):
        # "with" + "submit_button" sont nécessaire dans l'utilisation du "multiselect"
        # mais peut être supprimé en cas de cases à cocher pour la sélection
        selected_childs_firstName : list[str] = st.multiselect(
                "Tu désires te renseigner sur quel(s) enfants(s) ?",
                options = accessible_childs_firstName,
                default = default_selected_childs_firstName,
                key     = "selected_childs_firstName")

        submitted : bool = st.form_submit_button("Submit")
        if submitted :
            st.success('Childs are selected', icon="✅")

    selected_childs : list = [accessible_child for accessible_child in accessible_childs if accessible_child["firstName"][0] in selected_childs_firstName]

    return selected_childs


#####################################
##    FRONT END TO SELECT CHILDS   ##
#####################################

if "identification"  in st.session_state and "selected_childs" in st.session_state :

    identification = st.session_state["identification"]["actual_role"]
    if "child" in st.session_state["identification"]["actual_role"] :
        st.error("😕 You are not a teacher or parent, nothing to do on this page !")
    if "parent" in identification :
        st.title("Selection des enfants :")
        st.session_state["selected_childs"] = get_childs()
    if "teacher" in identification :
        st.title("Sélection des élèves")
        st.session_state["selected_childs"] = get_childs()