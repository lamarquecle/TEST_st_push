import streamlit as st
from PIL import Image
import altair as alt
import numpy as np
import pandas as pd
from datetime import datetime

st.write("creuser le fait de faire passer le 'questionnaire MBTI' suivi d'un entretien jugé très fiable par Jean-Luc LODS rencontré aux entretiens de l'excellence.")

questionnaire_disc = [('Concemant votre poignée de main :',
  ('Elle est ferme et plutôt appuyée.',
   'Elle est rapide et plutôt chaleureuse.',
   'Elle est moyennement forte.',
   "Elle est discrète et vous n'aimez pas forcément semer la main.")),
 ('Dans votre quotidien vous aimez :',
  ("Relever les challenges et être toumé vers l'action.",
   'Etre compréhensif et ne pas rentrer dans le conflit.',
   'Divertir et prendre plaisir avec les gens.',
   'Être prudent, réfléchi et ne pas donner votre confiance facilement.')),
 ('Quand vous vous exprimez, vous parlez plutôt :',
  ("Fort car il est important de se faire entendre et d'impacter.",
   'Avec un très faible volume et lentement, vous aimez être discret.',
   'Avec de grandes variations vocales et un rythme très rapide.',
   'Avec un volume modéré et de manière calme, voir monocorde.')),
 ("C'est samedi, qu'avez vous prévu ?",
  ("Partir à l'aventure sans me préoccuper des autres.",
   'Organiser un barbecue avec des amis.',
   "Ranger et mettre de l'ordre dans mes affaires.",
   'Aider une association locale et prendre mon temps.')),
 ('Quand vous échangez avec les autres :',
  ("Vous parlez plus que vous n'écoutez et avez tendance à couper la parole et être affirmatif dans vos propos.",
   "Vous avez une grande capacité d'écoute ce qui est pour vous, un signe de respect.",
   "Vous adorez prendre part à une conversation. Discuter est essentiel pour vous qu'importe le contenu.",
   'Votre préférence les emails. Vous parlez peu et exprimez pas forcément vos sentiments.')),
 ('Concemant le regard :',
  ('Vous regardez dans les yeux de manière soutenu en cherchant à évaluer votre interlocuteur.',
   "Vous avez regard amical et chaleureux et cherchez à éveiller l'intérêt.",
   "Vous n'aimez pas qu'on vous regarde de manière fixe, vous détoumez facilement le regard.",
   'Vos contacts visuels sont rares, voire inexistants, vous évitez le regard des autres.')),
 ('Quelles sont les qualités que vous aimez ?',
  ("Aller de l'avant, faire preuve de détermination, affronter les challenges.",
   "Le sens de l'humour, la répartie, l'optimisme et l'enthousiasme.",
   "Les règles, les procédures, la précision et la recherche de l'excellence.",
   "Faire preuve d'empathie, être ouvert aux autres et comprendre leurs sentiments.")),
 ('Vos principales peurs:',
  ("Que l'on tire avantage de vous.",
   "Faire face à des changements soudains, à l'instabilité permanente.",
   "Être critiqué pour votre travail, l'absence de qualité et de précision.",
   "L'ignorance des autres, étre délaissé.")),
 ('Dans une réunion vous êtes celui qui:',
  ('Propose de nouvelles idées et est toujours de bonne humeur.',
   'Aime décider et imposer ses idées pour avancer.',
   "Se conforme aux règles, procédures et suit scrupuleusement l'agenda de la réunion.",
   "S'attache à la cohésion du groupe et aux sentiments des autres.")),
 ('Au travail vous êtes:',
  ('Formel, rationnel, structuré et concret.',
   'Attentionné, pratique et altruiste.',
   'Interactif, social et amical',
   'Efficace, rapide, structuré et occupé')),
 ('Parmi les métiers suivants, quel est celui que vous choisirez:',
  ("Avocat, comptable, informaticien pour la précision et l'analyse.",
   "Thérapeute, infirmier ou coach, pour le don de soi et l'écoute.",
   'Sportif, entrepreneur, cadre dirigeant pour les challenges et la compétition.',
   'Cadre commercial, publiciste, journaliste pour le relationnel et les interactions.')),
 ('Concemant votre mode de réflexion:',
  ("Vous réfléchissez à voix haute et n'hésitez pas à exprimer vos ressentis.",
   "Vous allez rapidement à l'essentiel et décidez vite avec un minimum d'informations.",
   'Votre réflexion est lente et profonde.',
   'Vous aimez analyser les choses et rentrer dans les détails ce qui peut vous paralyser dans votre prise de décision.')),
 ('Au niveau de votre espace personnel:',
  ('Même avec vos proches, vous gardez votre distance.',
   "Vous occupez l'espace et n'hésitez pas à rentrer dans l'espace privé de votre interlocuteur.",
   'Vous restez à distance et prenez uniquement vos aises quand une relation profonde vous lie avec votre interlocuteur.',
   'Vous êtes très rapidement tactile et familier avec votre interlocuteur, voir trop.')),
 ('La structure de vos emails:',
  ("Au maximum 3 lignes, sans forcément de salutations. Ils sont courts et vont à l'essentiel.",
   "Vos emails sont moyennement longs et vous n'hésitez pas à utiliser des smileys et raconter une anecdote.",
   'Les courriels que vous rédigés sont complets, détaillés, très longs et souvent avec des pièces jointes.',
   'Vos emails sont plutôt longs, détaillés et personnels avec des formules de politesse.')),
 ("Quand vous donnez votre opinion lors d'une conversation :",
  ("Vous n'hésitez pas à donner votre opinion directement et sans filtres.",
   'Vous êtes très spontané, voir trop de temps en temps.',
   "Vous prenez le temps avant de répondre et vous exprimez plus en termes de données et de faits qu'opinion générale.",
   'Vous vérifiez que les personnes comprennent vos propos et faites attention à ne pas les froisser.'))]
interpretation_disc = {
    "Dominant" : ["Tenace", "Agressif", "Vif", "Positif", "Energétique", "Efficace", "Factuel", "Fonceur", "Rapide", "Autonome", "Direct", "Franc"],
    "Influent" : ["Convivial", "Sincère", "Energétique", "Positif", "Amical", "Expansif", "Enthousiaste", "Optimiste", "Cordial", "Démonstratif", "Tactile", "Sociable"],
    "Stable" : ["Fiable", "Modeste", "Patient", "Calme", "Humble", "Réfléchi", "Méthodique", "Protecteur", "Attentionné", "Doux", "Timide", "Généraux"],
    "Conscencieux" : ["Analytique", "Classique", "Logique", "Froid", "Précis", "Formel", "Indépendant", "Réservé", "Réfléchi", "Prudent", "Collectionneur", "Méticuleux"]}

questionnaire_kolb = [
    ("""Quand j'utilise un nouvel appareil (ordinateur, magnétoscope...),""",
        ("""j'analyse soigneusement le mode d'emploi et j'essaie de bien comprendre le fonctionnement de chaque élément.""",
        """je procède par essais et erreurs, je tâtonne.""",
        """je me fie à mes intuitions ou je demande à un copain de m'aider.""",
        """j'écoute et j'observe attentivement les explications de celui qui s'y connait.""")),
    ("""En général, face à un problème,""",
        ("""je prends tout mon temps et j'observe""",
        """j'analyse rationnellement le probleme, j'essaie de rester logique.""",
        """je n'hésite pas, je prends le taureau par les cornes et j'agis""",
        """je réagis plutôt instinctivement, je me fie à mes impressions ou à mes sentiments""")),
    ("""Pour m'orienter dans une ville inconnue,""",
        ("""je me fie à mon intuition, je 'sens' la direction générale, Si cela ne va pas, j'interpelle quelqu'un de sympathique.""",
        """j'observe calmement et attentivement. j'essaie de trouver des points de repère""",
        """je me repère rationnellement ; de préférence, je consulte une carte ou un plan.""",
        """l'important pour moi, c'est de réagir rapidement : parfois je demande, parfois j'essaie un itinéraire, quitte à faire demi-tour...""")),
    ("""Si je dois étudier un cours,""",
        ("""j'essaie surtout de faire des exercices et de découvrir des applications pratiques.""",
        """je décortique soigneusement la matière : j'analyse et je raisonne""",
        """je prends mon temps, je lis et relis attentivement la matière.""",
        """j'aime travailler avec des amis et je m'attache à ce qui me paralt important.""")),
    ("""Quand je dois faire un achat important, pour choisir,""",
        ("""j'observe, j'écoute les avis et les contre-avis, je prends tout mon temps.""",
        """je fais confiance à mon intuition.""",
        """j'essaie de calculer le meilleur rapport qualité-prix (au besoin je consulte une revue spécialisée).""",
        """ce qui m'intéresse, c'est d'abord de faire un essai, je n'achète pas un chat dans un sac""")),
    ("""Le professeur qui me convient le mieux est quelqu'un""",
        ("""qui expose sa matière avec rigueur, logique et précision.""",
        """qui fait agir ses étudiants aussi souvent que possible.""",
        """qui, avant tout, fait appel à l'expérience vécue des étudiants""",
        """qui a le souci de faire observer et réfléchir avant d'agir""")),
    ("""Pour apprendre une langue étrangère, je préfère""",
        ("""lire et écouter pour bien m'imprégner de la langue.""",
        """étudier un vocabulaire de base et un minimum de grammaire avant de me lancer dans une conversation.""",
        """me plonger dans la pratique et parler le plus tôt possible!""",
        """improviser: tout dépend de la langue, de mes rencontres et de mon état d'esprit....""")),
    ("""Pour préparer un exposé,""",
        ("""je le construis en fonction de mon public. S'il le faut, j'improvise sur place.""",
        """je répète seul ou en petit comité.""",
        """je m'inspire d'exemples que j'ai pu observer et apprécier.""",
        """je construis une structure logique, une analyse et une synthèse.""")),
    ("""Pour passer de bonnes vacances,""",
        ("""je me décide rapidement, je prépare mes bagages ou mon matériel et je fonce.""",
        """je rassemble une solide documentation, je pèse le pour et le contre et je choisis en connaissance de cause...""",
        """j'aime voir sur place et risquer un peu d'imprévu.""",
        """j'hésite à me décider, j'ai besoin d'avis, de témoignages.""")),
    ("""Si je dois lire un livre difficile,""",
        ("""j'analyse la table des matières... J'essaie d'assimiler chaque élément avant de passer au suivant""",
        """je commence par le parcourir pour mieux le "sentir" et pour voir si cela vaut la peine d'insister....""",
        """je recherche surtout les exemples, les aspects concrets et les applications.""",
        """je ne me presse pas, je demande parfois des avis, des appréciations.""")),
    ("""Si je dois préparer un bon petit plat,""",
        ("""je m'adresse à quelqu'un qui s'y connaît et je l'observe.""",
        """j'analyse la recette; il faut de la rigueur et de la précision.""",
        """je me fie plutôt à mon expérience et à mon coup d'oeil ...""",
        """je me lance, je tâtonne, je goûte... Je mets tout de suite la main à la pâte.""")),
    ("""Pour choisir une profession,""",
        ("""le mieux c'est d'essayer en faisant un stage.""",
        """Pour moi, le plus important est de se fier à ses intuitions et à ses relations.""",
        """l'idéal est d'observer les professionnels sur le terrain et de solliciter leurs témoignages.""",
        """l'essentiel est d'analyser tous les éléments, par exemple les aptitudes, les débouchés, les salaires..."""))
    ]
interpretation_kolb = {
    "accomodants" : {
        "description" : ["part de l'expérimentation", "se fie plus sur l'instinct que la logique", "<< je vais tout essayer aumoins une fois >>"],
        "objectifs" : ["besoin de généraliser", "clarifier ce que l'on peut faire avec ce qui a été appris"],
        "questions usuelles" : ["<< Et, que puis-je en faire ? >>", "<< Où et quand puis-je m'en servir ? >>"],
        "pédagogie" : ["dynamique", "orienté vers le transfert du savoir faire dans le futur"],
        "interets" : ["diriger", "prendre des risques", "réaliser des projets"],
        "inconvénients" : ["agir pour agir", "se disperser"],
        "état" : ("transfère", ("Expérimentation active", "Expérience concrête")),
        "questions générales" : ("Et après ?", ["utilisation", "applications possibles"])},
    "divergent" : {
        "description" : ["beaucoup de recul", "point de vue sur différents angles", "observent avant d'agir"],
        "objectifs" : ["donner du sens et des raisons à l'apprentissage"],
        "questions usuelles" : [""],
        "pédagogie" : ["intéractif", "imaginatif", "discussions", "partage d'idées"],
        "interets" : ["mise en vant de problèmes sous plein d'angles"],
        "inconvénients" : ["hésiter dans les choix", "retarder les décisions"],
        "état" : ("analyse", ("Observation réflexive", "Expérience concrête")),
        "questions générales" : ("pourquoi ?", ["sens", "intérêts", "raisons"])},
    "assimilant" : {
        "description" : ["réfléxion", "expériences", "conceptualisation"],
        "objectifs" : ["organisation step by step"],
        "questions usuelles" : ["De quoi s'agit il ?", "Preuve des actions ?"],
        "pédagogie" : ["Informative", "Analytique"],
        "interets" : ["créer des modèles"],
        "inconvénients" : ["méconnaitre la pratique (100% théorique, 0% pratique)"],
        "état" : ("généraliste", ("Observation réflexive", "Conceptualisation abstraite")),
        "questions générales" : ("Quoi ?", ["contenu", "informations", "faits"])},
    "convergent" : {
        "description" : ["part du concept et mise et pratique", "démarche par essai-erreur", "rapide prise de décision", "est son propre cadre"],
        "objectifs" : ["expérimenter par essai-erreur"],
        "questions usuelles" : ["Comment mettre en pratique le plus rapidement possible ?"],
        "pédagogie" : ["pratique", "orienté sur une démarche à suivre", "délais à respecter et tâches à effectuer"],
        "interets" : [""],
        "inconvénients" : [""],
        "état" : ("pratique", ("Expérimentation active", "Conceptualisation abstraite")),
        "questions générales" : ("Comment ?", ["pratique", "expérimentation"])}}

def categories_from_answers_disc(answers) :
    answers=answers.astype(int)
    R_ind_DISC = list(map(int,list("000000001321100")))
    J_ind_DISC = list(map(int,list("122121130230311")))
    V_ind_DISC = list(map(int,list("211312313112233")))
    B_ind_DISC = list(map(int,list("333233222003022")))

    R = sum([answers[i, R_ind_DISC[i]] for i in range(15)])
    J = sum([answers[i, J_ind_DISC[i]] for i in range(15)])
    V = sum([answers[i, V_ind_DISC[i]] for i in range(15)])
    B = sum([answers[i, B_ind_DISC[i]] for i in range(15)])

    #coords = (J+V-R-B, J+R-V-B) # (taches_personnes, intraverti_extraverti)
        # NB : ce passage aux coords peur se discuter :
        # J=10, V=0, R=B=7   =>   coords = (-4, 10)
        # la première est discutable en vue du non respect de max(J, V, R, B) = Jr où Jr=(>0, >0)

    results = [R, J, V, B]
    return results
def have_chart_datas_disc(childs_disc):
    X_childs_disc = np.array(childs_disc)
    st.write(X_childs_disc)

    graph_categories = []
    for child_disc  in X_childs_disc :
        for value, category in zip(child_disc[1:5], ["Dominant", "Influent", "Stable", "Conscencieux"]) :
            graph_categories += [[child_disc[0], category, value, child_disc[5]]]

    df_categories = pd.DataFrame(graph_categories, columns = ["firstName", "category", "n_answers", "date"])
    return df_categories

def is_valid_answers_kolb(answers):
    for answer in answers :
        if set(answer) != set(range(1,5)) :
            return False
    return True
def coords_from_answers_kolb(answers) :
    # answers = M(12*4 : 1,2,3,4)
    answers=answers.astype(int)
    A_ind = list(map(int,list("130231302132")))
    B_ind = list(map(int,list("213102121010")))
    C_ind = list(map(int,list("021310230203")))
    D_ind = list(map(int,list("302023013321")))

    A = sum([answers[i, A_ind[i]] for i in range(12)])
    B = sum([answers[i, B_ind[i]] for i in range(12)])
    C = sum([answers[i, C_ind[i]] for i in range(12)])
    D = sum([answers[i, D_ind[i]] for i in range(12)])

    coords = (A - B - 9, C - D - 5)
    return coords
def have_chart_datas_kolb(childs_kolb):
    X_childs_kolb = np.array(childs_kolb)
    scale_xMin = min(X_childs_kolb[:,1].astype(int))
    scale_xMax = max(X_childs_kolb[:,1].astype(int))
    scale_yMin = min(X_childs_kolb[:,2].astype(int))
    scale_yMax = max(X_childs_kolb[:,2].astype(int))

    st.write(X_childs_kolb)

    if scale_xMin > 0 : scale_xMin = 0 # NB : transform to have (0, 0) in the graph
    if scale_xMax < 0 : scale_xMax = 0
    if scale_yMin > 0 : scale_yMin = 0
    if scale_yMax < 0 : scale_yMax = 0

    x_domain = [scale_xMin-1, scale_xMax +1]
    y_domain = [scale_yMin-1, scale_yMax +1]

    df_coords = pd.DataFrame(childs_kolb, columns = ["firstName", "x", "y", "date"])

    chart = alt.Chart(df_coords, title="KOLB : Cycle d'apprentissage").mark_circle().encode(
                x=alt.X('x', title="activité <--> réflexion", scale=alt.Scale(domain=x_domain)),
                y=alt.Y('y', title="abstrait <--> concret"  , scale=alt.Scale(domain=y_domain)),
                tooltip=['firstName', 'x', 'y','date'], color='firstName') #, size='count')
    line_x = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule().encode(x='x')
    line_y = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule().encode(y='y')
    return chart + line_x + line_y

def have_childs(selected_childs, test = "KOLB"):
    childs_test = []
    for selected_child in selected_childs :
        # NB : la première boucle est inutile dans le cadre d'un élève connecté
        child_firstName = selected_child["firstName"][0]
        for test_result in selected_child[f"{test}_results"] :
            childs_test += [[child_firstName] + test_result]
    return childs_test
def categories_from_answers_disc(answers) :
    answers=answers.astype(int)
    R_ind_DISC = list(map(int,list("000000001321100")))
    J_ind_DISC = list(map(int,list("122121130230311")))
    V_ind_DISC = list(map(int,list("211312313112233")))
    B_ind_DISC = list(map(int,list("333233222003022")))

    R = sum([answers[i, R_ind_DISC[i]] for i in range(15)])
    J = sum([answers[i, J_ind_DISC[i]] for i in range(15)])
    V = sum([answers[i, V_ind_DISC[i]] for i in range(15)])
    B = sum([answers[i, B_ind_DISC[i]] for i in range(15)])

    #coords = (J+V-R-B, J+R-V-B) # (taches_personnes, intraverti_extraverti)
        # NB : ce passage aux coords peur se discuter :
        # J=10, V=0, R=B=7   =>   coords = (-4, 10)
        # la première est discutable en vue du non respect de max(J, V, R, B) = Jr où Jr=(>0, >0)

    results = [R, J, V, B]
    return results
def have_chart_datas_disc(childs_disc):
    X_childs_disc = np.array(childs_disc)
    st.write(X_childs_disc)

    graph_categories = []
    for child_disc  in X_childs_disc :
        for value, category in zip(child_disc[1:5], ["Dominant", "Influent", "Stable", "Conscencieux"]) :
            graph_categories += [[child_disc[0], category, value, child_disc[5]]]

    df_categories = pd.DataFrame(graph_categories, columns = ["firstName", "category", "n_answers", "date"])
    return df_categories

def is_valid_answers_kolb(answers):
    for answer in answers :
        if set(answer) != set(range(1,5)) :
            return False
    return True
def coords_from_answers_kolb(answers) :
    # answers = M(12*4 : 1,2,3,4)
    answers=answers.astype(int)
    A_ind = list(map(int,list("130231302132")))
    B_ind = list(map(int,list("213102121010")))
    C_ind = list(map(int,list("021310230203")))
    D_ind = list(map(int,list("302023013321")))

    A = sum([answers[i, A_ind[i]] for i in range(12)])
    B = sum([answers[i, B_ind[i]] for i in range(12)])
    C = sum([answers[i, C_ind[i]] for i in range(12)])
    D = sum([answers[i, D_ind[i]] for i in range(12)])

    coords = (A - B - 9, C - D - 5)
    return coords
def have_chart_datas_kolb(childs_kolb):
    X_childs_kolb = np.array(childs_kolb)
    scale_xMin = min(X_childs_kolb[:,1].astype(int))
    scale_xMax = max(X_childs_kolb[:,1].astype(int))
    scale_yMin = min(X_childs_kolb[:,2].astype(int))
    scale_yMax = max(X_childs_kolb[:,2].astype(int))

    st.write(X_childs_kolb)

    if scale_xMin > 0 : scale_xMin = 0 # NB : transform to have (0, 0) in the graph
    if scale_xMax < 0 : scale_xMax = 0
    if scale_yMin > 0 : scale_yMin = 0
    if scale_yMax < 0 : scale_yMax = 0

    x_domain = [scale_xMin-1, scale_xMax +1]
    y_domain = [scale_yMin-1, scale_yMax +1]

    df_coords = pd.DataFrame(childs_kolb, columns = ["firstName", "x", "y", "date"])

    chart = alt.Chart(df_coords, title="KOLB : Cycle d'apprentissage").mark_circle().encode(
                x=alt.X('x', title="activité <--> réflexion", scale=alt.Scale(domain=x_domain)),
                y=alt.Y('y', title="abstrait <--> concret"  , scale=alt.Scale(domain=y_domain)),
                tooltip=['firstName', 'x', 'y','date'], color='firstName') #, size='count')
    line_x = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule().encode(x='x')
    line_y = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule().encode(y='y')
    return chart + line_x + line_y

def have_childs(selected_childs, test = "KOLB"):
    childs_test = []
    for selected_child in selected_childs :
        # NB : la première boucle est inutile dans le cadre d'un élève connecté
        child_firstName = selected_child["firstName"][0]
        for test_result in selected_child[f"{test}_results"] :
            childs_test += [[child_firstName] + test_result]
    return childs_test

if "identification" not in st.session_state : st.error("😕 No valid identification !")
elif "selected_childs" not in st.session_state : st.error("😕 No 'selected_childs' !")
elif "child" in st.session_state["identification"]["actual_role"] :
    st.write("C.")
    disc_tab, kolb_tab, results_tab = st.tabs(["DISC", "KOLB", "Results"])

    with disc_tab:

        X_answers = np.zeros((15,4))
        for i_question, content in enumerate(questionnaire_disc):
            question, answers = content
            value = st.radio(question, label_visibility="visible", options = answers, key=f"disc_{i_question}")
            value_index = answers.index(value)
            X_answers[i_question, value_index] = 1

        if st.button('Validation', key="disc_validation"):

            categories = categories_from_answers_disc(X_answers)
            date_now = datetime.now().strftime("%Y%m%d%H%M%S.%f")
            st.session_state["selected_childs"][0]["DISC_results"] += [[categories[0], categories[1], categories[2], categories[3], date_now]]

            all_coords = st.session_state["selected_childs"][0]["DISC_results"]
            # st.session_state["etablissement_childs"][i]["DISC_results"] += [[categories[0], categories[1], categories[2], categories[3], date_now]]
            # <=> sauvegarde dans la BDD + importation de toutes les donnees DICS

            st.success('Answers are save in BDD !', icon="✅")
    with kolb_tab:
        st.write("DECOUVREZ VOTRE STYLE D'APPRENTISSAGE DOMINANT!")
        st.write("À tout moment, nous sommes amenés à faire face à un problème (qu'il soit pratique ou théorique) et chacun y réagit à sa manière. C'est ce qu'on appelle le style d'apprentissage.")
        st.write("Pour découvrir votre style, essayez de réagir le plus spontanément possible aux 12 situations suivantes en classant vos réactions par ordre de préférence.")
        st.write("""
            <ol>
            <li>C'est tout à fait moi</li>
            <li>C'est souvent moi</li>
            <li>C'est parfois moi</li>
            <li>C'est rarement moi</li>
            </ol>""", unsafe_allow_html = True)
        st.write("N'utilisez pas 2 fois le même chiffre dans une même question!")
        st.write("Exemple: Quand j'ai une petite faim,")
        st.write("""
            <ul>
            <li>4 a) je patiente jusqu'à l'heure du repas</li>
            <li>1 b) je mange ce que j'avais prévu</li>
            <li>3 c) je me débrouille</li>
            <li>2 d) je prends ce qui me tombe sous la main</li>
            </ul>""", unsafe_allow_html = True)
        st.write("Grille d'évaluation")
        st.write("""Bien entendu, il n'y a pas de "bonnes" ou de "mauvaises" réponses. Entrez votre réponse dans les cases prévues à cet effet.""")

        X_answers = np.zeros((12,4))
        for i_question, content in enumerate(questionnaire_kolb):
            question, answers = content
            st.write(question)
            for i_answer, answer in enumerate(answers):
                _, col_txt, col_answer = st.columns([1,1, 10])
                value = col_txt.text_input("hidden", label_visibility="hidden", key=f"kolb_{i_question}_{i_answer}")
                col_answer.write("") # NB : visuellement utile pour la page
                col_answer.write("") # NB : visuellement utile pour la page
                col_answer.write(answer)
                if value in list("1234") : X_answers[i_question, i_answer] = int(value)

        if st.button('Validation', key="kolb_validation"):

            coords = coords_from_answers_kolb(X_answers)
            if is_valid_answers_kolb(X_answers) :

                date_now = datetime.now().strftime("%Y%m%d%H%M%S.%f")
                st.session_state["selected_childs"][0]["KOLB_results"] += [[coords[0], coords[1], date_now]]
                all_coords = st.session_state["selected_childs"][0]["KOLB_results"]
                # st.session_state["etablissement_childs"][i]["KOLB_results"] += [[coords[0], coords[1], date_now]]
                # <=> sauvegarde dans la BDD
                st.success('Answers are save in BDD !', icon="✅")
            else : st.error("😕 Answers are not valid !")

    with results_tab:
        selected_childs = st.session_state["selected_childs"]

        st.write("DISC results :")
        childs_disc = have_childs(selected_childs, test = "DISC")
        if childs_disc == [] : st.write(f"Les enfants sélectionnés n'ont pas effectués de test DISC")
        else :
            df_categories = have_chart_datas_disc(childs_disc)
            st.write(df_categories)
            #chart_datas = have_chart_datas_disc(childs_disc)
            #st.altair_chart(chart_datas, use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)
        image = Image.open('documents_externes/DISC traits.jpg')
        col1.image(image, caption="Traits d'une personne suivant DISC")
        image = Image.open('documents_externes/DISC rôles.png')
        col2.image(image, caption="Rôles d'une personne suivant DISC")
        image = Image.open('documents_externes/DISC impacter.jpg')
        col3.image(image, caption="Impacter une personne suivant DISC")
        image = Image.open('documents_externes/DISC pratique.jpg')
        col4.image(image, caption="Aspect pratique de DISC")

        st.write("KOLB results :")
        childs_kolb = have_childs(selected_childs, test = "KOLB")
        if childs_kolb == [] : st.write(f"Les enfants sélectionnés n'ont pas effectués de test KOLB")
        else :
            chart_datas = have_chart_datas_kolb(childs_kolb)
            st.altair_chart(chart_datas, use_container_width=True)
        image = Image.open('documents_externes/kolb-graph.png')
        st.image(image, caption='Interprétation du test de KOLB')


elif "parent" in st.session_state["identification"]["actual_role"] :
    st.write("P.")
    selected_childs = st.session_state["selected_childs"]

    st.write("DISC results :")
    childs_disc = have_childs(selected_childs, test = "DISC")
    if childs_disc == [] : st.write(f"Les enfants sélectionnés n'ont pas effectués de test DISC")
    else :
        df_categories = have_chart_datas_disc(childs_disc)
        st.write(df_categories)
        #chart_datas = have_chart_datas_disc(childs_disc)
        #st.altair_chart(chart_datas, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    image = Image.open('documents_externes/DISC traits.jpg')
    col1.image(image, caption="Traits d'une personne suivant DISC")
    image = Image.open('documents_externes/DISC rôles.png')
    col2.image(image, caption="Rôles d'une personne suivant DISC")
    image = Image.open('documents_externes/DISC impacter.jpg')
    col3.image(image, caption="Impacter une personne suivant DISC")
    image = Image.open('documents_externes/DISC pratique.jpg')
    col4.image(image, caption="Aspect pratique de DISC")

    st.write("KOLB results :")
    childs_kolb = have_childs(selected_childs, test = "KOLB")
    if childs_kolb == [] : st.write(f"Les enfants sélectionnés n'ont pas effectués de test KOLB")
    else :
        chart_datas = have_chart_datas_kolb(childs_kolb)
        st.altair_chart(chart_datas, use_container_width=True)

    image = Image.open('documents_externes/kolb-graph.png')
    st.image(image, caption='Interprétation du test de KOLB')

else :
    st.write("T.")
    selected_childs = st.session_state["selected_childs"]

    st.write("DISC results :")
    childs_disc = have_childs(selected_childs, test = "DISC")
    if childs_disc == [] : st.write(f"Les enfants sélectionnés n'ont pas effectués de test DISC")
    else :
        df_categories = have_chart_datas_disc(childs_disc)
        st.write(df_categories)
        #chart_datas = have_chart_datas_disc(childs_disc)
        #st.altair_chart(chart_datas, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    image = Image.open('documents_externes/DISC traits.jpg')
    col1.image(image, caption="Traits d'une personne suivant DISC")
    image = Image.open('documents_externes/DISC rôles.png')
    col2.image(image, caption="Rôles d'une personne suivant DISC")
    image = Image.open('documents_externes/DISC impacter.jpg')
    col3.image(image, caption="Impacter une personne suivant DISC")
    image = Image.open('documents_externes/DISC pratique.jpg')
    col4.image(image, caption="Aspect pratique de DISC")

    st.write("KOLB results :")
    childs_kolb = have_childs(selected_childs, test = "KOLB")
    if childs_kolb == [] : st.write(f"Les enfants sélectionnés n'ont pas effectués de test KOLB")
    else :
        chart_datas = have_chart_datas_kolb(childs_kolb)
        st.altair_chart(chart_datas, use_container_width=True)

    image = Image.open('documents_externes/kolb-graph.png')
    st.image(image, caption='Interprétation du test de KOLB')
