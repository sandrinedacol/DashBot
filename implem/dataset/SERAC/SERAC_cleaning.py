import csv

root = '/home/sandrine/Pro/data-science/DashBots/bandits-and-applications/code/interface/implem/dataset/SERAC'

with open(f'{root}/SERAC_raw.csv', newline='') as csvfile:
	attributes = csvfile.readline().strip().split(',')
	# print(attributes)
	#['"Document"', '"Document (lien)"', '"Titre"', '"Activités"', '"Complétude"', '"Localisation"', '"Altitude"',
	# '"Régions"', '"Contributeur"', '"Contributeur (lien)"', '"Date"', '"Type d\'évènement"', '"Nombre de participants"',
	# '"Participants associés"', '"Nombre de personnes touchées"', '"Intervention des services de secours"', '"Gravité"',
	# '"Niveau de risque d\'avalanche"', '"Pente de la zone de départ"', '"Âge"', '"Sexe"', '"Implication dans la situation"',
	# '"Niveau de pratique"', '"Fréquence de pratique dans l\'activité"', '"Nombre de sorties"', '"Blessures antérieures"',
	# '"Résumé"', '"Description"', '"Lieu"', '"Étude de l\'itinéraire"', '"Conditions"', '"Préparation physique et niveau technique"',
	# '"Motivations"', '"Gestion du groupe"', '"Niveau de l\'attention et évaluation des risques"', '"Gestion de l\'horaire"',
	# '"Mesures et techniques de sécurité mises en oeuvre"', '"Éléments ayant atténué les conséquences de l\'évènement"',
	# '"Éléments ayant aggravé les conséquences de l\'évènement"', '"Conséquences sur les pratiques"',
	# '"Conséquences physiques et autres commentaires"', '"Itinéraires associés"', '"Sorties associées"', '"Articles associés"']

# ['activity', 'location', 'altitude', 'country', 'region', 'massif', 'date', 'event', 'cause',
# 'N participant(s)', 'N victim(s)', 'rescue', 'severity', 'age', 'gender', level', 'frequency']

# selected_attributes = ['activity', 'altitude', 'cause', 'age']
selected_attributes = ['activity', 'altitude', 'country', 'event', 'cause', 'N victim(s)', \
	'rescue', 'severity', 'age', 'gender', 'level']


with open(f'{root}/SERAC.csv', 'w', newline='') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=selected_attributes)
    writer.writeheader()

with open(f'{root}/SERAC_raw.csv', newline='') as input_file:
	reader = csv.DictReader(input_file)
	for row in reader:
		cleaned_row = dict()

		# activity
		if 'activity' in selected_attributes:
			val = row["Activités"]
			if val == "VTT,":
				cleaned_row['activity'] = 'mountain bike'
			if val == "parapente," :
				cleaned_row['activity'] = 'paragliding'
			if val == "cascade de glace," : 
				cleaned_row['activity'] = 'ice climbing'
			if val == "randonnée," : 
				cleaned_row['activity'] = 'hiking'
			if val in ["escalade,randonnée,", "escalade,"] : 
				cleaned_row['activity'] = 'climbing'
			if val in [ 'ski de randonnée,', 'ski de randonnée,raquettes,' , 'raquettes,ski de randonnée,'] : 
				cleaned_row['activity'] = 'backcountry'
			if val in ["rocher haute-montagne," , "rocher haute-montagne,escalade,", "rocher haute-montagne,randonnée,"] : 
				cleaned_row['activity'] = 'rock mountaineering'
			if val in ['neige glace mixte,', "randonnée,neige glace mixte,", 'ski de randonnée,neige glace mixte,'] : 
				cleaned_row['activity'] = 'snow/ice/mixed'
			if val in ["rocher haute-montagne,neige glace mixte,", "neige glace mixte,rocher haute-montagne,"] : 
				cleaned_row['activity'] = 'mountaineering'

		# location
		if 'location' in selected_attributes:
			cleaned_row['location'] = row["Localisation"]

		# altitude
		if 'altitude' in selected_attributes:
			cleaned_row['altitude'] = row["Altitude"]

		# date
		if 'date' in selected_attributes:
			cleaned_row['date'] = row["Date"]

		#  N participant(s)
		if 'N participant(s)' in selected_attributes:
			cleaned_row['N participant(s)'] = row["Nombre de participants"]

		# N victims
		if 'N victim(s)' in selected_attributes:
			cleaned_row['N victim(s)'] = row["Nombre de personnes touchées"]

		# slope
		if 'slope' in selected_attributes:
			cleaned_row['slope'] = row["Pente de la zone de départ"]

		# age
		if 'age' in selected_attributes:
			cleaned_row['age'] = row["Âge"]

		# country
		val = row["Régions"]
		val = val.split(',')
		val = [v for v in val if len(v) > 0]
		if len(val) > 0:
			if val[0] == 'Provence':
				if 'country' in selected_attributes:
					cleaned_row['country'] = 'France'
				if 'region' in selected_attributes:
					cleaned_row['region'] = val[0]
				if 'massif' in selected_attributes:
					cleaned_row['massif'] = val[1]
			else:
				if 'country' in selected_attributes:
					if val[0] == 'France':
						cleaned_row['country'] = 'France'
					if val[0] == 'Suisse':
						cleaned_row['country'] = 'Switzerland'
					if val[0] == 'Italie':
						cleaned_row['country'] = 'Italy'
					if val[0] == 'Espagne':
						cleaned_row['country'] = 'Spain'
					if val[0] == 'Royaume-Uni':
						cleaned_row['country'] = 'UK'
					if val[0] == 'Belgique':
						cleaned_row['country'] = 'Belgium'
					if val[0] == 'Andorre':
						cleaned_row['country'] = 'Andorra'
					if val[0] == 'Nouvelle-Zélande':
						cleaned_row['country'] = 'New-Zealand'
					if val[0] == 'Éthiopie':
						cleaned_row['country'] = 'Ethiopia'
					if val[0] == 'Cuba':
						cleaned_row['country'] = 'Cuba'
					if val[0] == 'Argentine':
						cleaned_row['country'] = 'Argentina'
					if val[0] == 'Kirghizstan':
						cleaned_row['country'] = 'Kirghizstan'
					if val[0] == 'Colombie':
						cleaned_row['country'] = 'Colombia'
					if val[0] == 'Chine':
						cleaned_row['country'] = 'China'
					if val[0] == 'Laos':
						cleaned_row['country'] = 'Laos'
					if val[0] == 'Autriche':
						cleaned_row['country'] = 'Austria'

				# region / massif
				if val[0] in ['Italie', 'Espagne', 'Autriche']:
					if 'region' in selected_attributes:
						cleaned_row['region'] = val[2]
					if val[1] in ['Valais W - Alpes Pennines W', 'Valais E - Alpes Pennines E']:
						if 'massif' in selected_attributes:
							cleaned_row['massif'] = 'Valais - Alpes Pennines'
					else:
						if 'massif' in selected_attributes:
							cleaned_row['massif'] = val[1]
				else:
					if len(val) > 1:
						if 'region' in selected_attributes:
							cleaned_row['region'] = val[1]
						if len(val) == 3:
							if 'massif' in selected_attributes:
								if val[2] in ['Valais W - Alpes Pennines W', 'Valais E - Alpes Pennines E']:
									cleaned_row['massif'] = 'Valais - Alpes Pennines'
								else:
									cleaned_row['massif'] = val[2]

		# event/cause
		val = row["Type d\'évènement"]
		if 'event' in selected_attributes:
			if val in ['chute encordé,autre,', 'chute encordé,', 'défaillance physique,chute encordé,']:
				# 149 : cause = défaillance physique
				cleaned_row['event'] = 'roped fall'
			if val in ["chute d'une personne,", "chute d'une personne,chute encordé,", "chute encordé,chute d'une personne,", "chute d'une personne,autre,", "défaillance physique,chute encordé,chute d'une personne,", "défaillance physique,chute d'une personne", "chute d'une personne,défaillance physique,"]:
				cleaned_row['event'] = 'fall'
			if val == "défaillance physique,":
				# 222 & 301 : cause = défaillance physique
				cleaned_row['event'] = 'injury'
		if 'cause' in selected_attributes:
			if val == 'chute de pierres,':
				cleaned_row['cause'] = 'falling rocks'
			if val == 'chute de glace,':
				cleaned_row['cause'] = 'falling ice'
			if val in ['avalanche,', 'avalanche,chute de pierres,']:
				cleaned_row['cause'] = 'avalanche'
			if val == 'foudre,':
				cleaned_row['cause'] = 'lightning'
		if val == 'défaillance physique,avalanche,':
			if 'cause' in selected_attributes:
				cleaned_row['cause'] = 'avalanche'
			if 'event' in selected_attributes:
				cleaned_row['event'] = 'injury'
		if val in ["défaillance physique,chute d'une personne,chute de pierres,", "chute de pierres,chute d'une personne,", "chute de pierres,chute encordé,chute d'une personne,", "chute de pierres,chute d'une personne,chute encordé,", "chute d'une personne,chute de pierres,"]:
			if 'event' in selected_attributes:
				cleaned_row['event'] = 'fall'
			if 'cause' in selected_attributes:
				cleaned_row['cause'] = 'falling rocks'
		if val == "chute en crevasse,chute d'une personne,chute encordé,":
			if 'cause' in selected_attributes:
				cleaned_row['cause'] = 'crevasse'
			if 'event' in selected_attributes:
				cleaned_row['event'] = 'fall'
		if val in ["chute encordé,chute de pierres,", "chute de pierres,chute encordé,", "chute encordé,chute de pierres,autre,"]:
			if 'cause' in selected_attributes:
				cleaned_row['cause'] = 'falling rocks'
			if 'event' in selected_attributes:
				cleaned_row['event'] = 'roped fall'
		if val == "chute en crevasse,":
			# 372 : cause = avalanche, event = chute
			if 'cause' in selected_attributes:
				cleaned_row['cause'] = 'crevasse'
			if 'event' in selected_attributes:
				cleaned_row['event'] = 'roped fall'
		if val == "chute encordé,chute en crevasse,":
			if 'cause' in selected_attributes:
				cleaned_row['cause'] = 'crevasse'
			if 'event' in selected_attributes:
				cleaned_row['event'] = 'roped fall'
		if val == "avalanche,chute d'une personne,":
			if 'cause' in selected_attributes:
				cleaned_row['cause'] = 'avalanche'
			if 'event' in selected_attributes:
				cleaned_row['event'] = 'fall'
		if val == "chute d'une personne,chute de glace,":
			if 'cause' in selected_attributes:
				cleaned_row['cause'] = 'falling ice'
			if 'event' in selected_attributes:
				cleaned_row['event'] = 'fall'
		


		# rescue
		if 'rescue' in selected_attributes:
			val = row["Intervention des services de secours"]
			if val == 'oui':
				cleaned_row['rescue'] = True
			if val == 'non':
				cleaned_row['rescue'] = False

		# severity
		if 'severity' in selected_attributes:
			val = row["Gravité"]
			if val =='pas de blessure' : 
				cleaned_row['severity'] = 0 # '0'
			if val == 'De 1 à 3 jours' : 
				cleaned_row['severity'] = 0.02 # '1-3'
			if val == 'De 4 jours à 1 mois' :
				cleaned_row['severity'] = 0.17 # '4-30'
			if val == 'De 1 à 3 mois' :
				cleaned_row['severity'] = 0.6 # '30-90'
			if val == 'supérieur à 3 mois' :
				cleaned_row['severity'] = 0.9 # '>90'

		# BRA
		if 'BRA' in selected_attributes:
			val = row["Niveau de risque d\'avalanche" ]
			try:
				cleaned_row['BRA'] = int(val.split(' - ')[0])
			except ValueError:
				pass

		# gender
		if 'gender' in selected_attributes:
			val = row["Sexe"]
			if val == 'H':
				cleaned_row['gender'] = 'M'
			else:
				cleaned_row['gender'] = val

		# level
		if 'level' in selected_attributes:
			val = row["Niveau de pratique"]
			if val == 'expert':
				cleaned_row['level'] = 'expert'
			if val == 'débrouillé':
				cleaned_row['level'] = 'initiated'
			if val == 'autonome':
				cleaned_row['level'] = 'self-sufficient'
			if val == 'non autonome':
				cleaned_row['level'] = 'novice'

		# frequency
		if 'frequency' in selected_attributes:
			val = row["Fréquence de pratique dans l\'activité"]
			if val == "moins d'1 fois par an" :
				cleaned_row['frequency'] =  '<1'
			if val == "moins d'1 fois par mois" : 
				cleaned_row['frequency'] = '1-10'
			if val == '1 fois par mois' : 
				cleaned_row['frequency'] = '10-20'
			if val == '2 à 3 fois par mois' : 
				cleaned_row['frequency'] = '20-50'
			if val == '1 à 2 fois par semaine' : 
				cleaned_row['frequency'] = '50-150'
			if val == 'au moins 3 fois par semaine' : 
				cleaned_row['frequency'] = '>150'

		with open(f'{root}/SERAC.csv', 'a', newline='') as output_file:
			writer = csv.DictWriter(output_file, fieldnames=selected_attributes)
			writer.writerow(cleaned_row)

values = dict()
with open(f'{root}/SERAC.csv', newline='') as csvfile:
	for col in selected_attributes:
		values[col] = set()
	reader = csv.DictReader(csvfile)
	for row in reader:
		for col in selected_attributes:
			values[col].add(row[col])		
with open(f'{root}/SERAC_values.csv', 'w') as file:
	for col, vals in values.items():
		file.write('\n///////////////////////////\n' + col + '\n////////////////////////////\n')
		for val in vals:
			file.write(val + '\n')







