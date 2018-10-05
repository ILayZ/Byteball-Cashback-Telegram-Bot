VISION_KEY_PATH = 'gsa_key.json'
BOT_KEY = '678408435:AAHhkhpCyZGFduyCrAsP5rHtmd6sI0RkCog'

USER_DATA = {
				'partner': 'obed-online',
				'partner_key': 'kp6nVdwKtq8n',
				'currency': 'RUR'
			}

CHECK_REGEX = {
				'merchant': 		{ 'pattern': r'ИНН\s+({\d|\s}{12})', 					  'group': 1 },
				'check': 			{ 'pattern': r'(Чек)(.*\s)(\d+){\n|\s}+', 				  'group': 3 },
				'date':  			{ 'pattern': r'(\d\d-\d\d-\d\d\d\d)', 					  'group': 1 },
				'time':	 			{ 'pattern': r'Закрыт\s+(\d\d:\d\d)', 					  'group': 1 },
				'currency_amount':	{ 'pattern': r'Итого:\n(\d+\.\d\d)',	 				  'group': 1 },
				'description':		{ 'pattern': r'(Блюдо\nКол-во\n..мма\n)(.*\n)(Всего:\n)', 'group': 2 }
			  }