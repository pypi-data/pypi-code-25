#!/usr/bin/python
#coding:utf-8


from dmpdfparser import PdfParser


import sys
import json
import copy

class PdfParserData(object):

	def __init__(self, config):
	
		self.config = config
		
		
	def find_tables_floats_locs(self, parsed_pdf):
	
		table_loc_index = 0
		
		prev_line_bottom = -1
		next_line_top = -1
		
		table_loc = None
	
		for parsed_page in parsed_pdf["pages"]:
				
			for parsed_text in parsed_page["texts"]:
							
				if True:
				
					content = parsed_text["content"]
					table_loc = self.config["TABLES_LOCS_FLOAT"][table_loc_index]
					
					if(prev_line_bottom == -1):
						for col_name in table_loc["prev_line"]:
							if(col_name.upper() in content.upper()):
							
								prev_line_bottom = parsed_text["bottom"]
								break
					
					elif( (next_line_top == -1) and (parsed_text["bottom"] > prev_line_bottom) ):
						for col_name in table_loc["next_line"]:
							if(col_name.upper() in content.upper()):
								
								next_line_top = parsed_text["top"]
								break
								
					if( (prev_line_bottom > 0) and (next_line_top > 0) ):
					
						table_loc["top"] = prev_line_bottom + 1
						table_loc["bottom"] = next_line_top - 1
						table_loc["page_number"] = parsed_page["number"]
						
						table_loc_index = table_loc_index + 1
						prev_line_bottom = -1
						next_line_top = -1
					
					
				if(table_loc_index >= len(self.config["TABLES_LOCS_FLOAT"])):
					break
					
			
			
			if(table_loc_index >= len(self.config["TABLES_LOCS_FLOAT"])):
				break
				
				
			if( (prev_line_bottom > 0) and (next_line_top == -1) ):
				
				table_loc = self.config["TABLES_LOCS_FLOAT"][table_loc_index]
				
				table_loc_copy = {key : table_loc[key] for key in table_loc}
				self.config["TABLES_LOCS_FLOAT"].insert(table_loc_index + 1, table_loc_copy)
				
				table_loc["top"] = prev_line_bottom + 1
				table_loc["bottom"] = self.config["TABLES_LOCS_FLOAT_MAX_BOTTOM"]
				table_loc["page_number"] = parsed_page["number"]
				
				
				table_loc_index = table_loc_index + 1
				prev_line_bottom = -1
				next_line_top = -1
			
	
	
	def parse_to_model(self, filepath_pdf_in, filepath_json_out, filepath_html_out):
		
		model = {}
		model["tables"] = {}
		model["fields"] = {}
				
		parsed_pdf = PdfParser.save_parse(filepath_pdf_in, filepath_json_out)
		
		
		tables_locs_fixed_template = self.config["TABLES_LOCS_FIXED"]			
		self.config["TABLES_LOCS_FIXED"] = []
				
		for i, parsed_page in enumerate(parsed_pdf["pages"]):	
		
			parsed_page["texts"].sort(key = lambda parsed_text: (parsed_text["top"], parsed_text["left"], parsed_text["bottom"], parsed_text["right"]))
			
			tables_locs_fixed = copy.deepcopy(tables_locs_fixed_template)
			
			for table_loc in tables_locs_fixed:
				table_loc["page_number"] = str(i + 1)
				
			self.config["TABLES_LOCS_FIXED"] = self.config["TABLES_LOCS_FIXED"] + tables_locs_fixed
					
		PdfParser.save_parsed_pdf_to_html(parsed_pdf, filepath_html_out)
		
		if(len(self.config["TABLES_LOCS_FLOAT"]) > 0):
			self.find_tables_floats_locs(parsed_pdf)	
		
		self.config["TABLES_LOCS"] = self.config["TABLES_LOCS_FIXED"] + self.config["TABLES_LOCS_FLOAT"]
		
		for table_loc in self.config["TABLES_LOCS"]:
			table_loc["rows_top"] = []
					
		parsed_text_empty = \
		{
		"left" : 0,
		"top": 0,
		"right": 0,
		"bottom": 0,
		
		"width": 0,
		"height": 0,
		
		"font_id": "0",
		
		"content": "---"
		}
		
		threshold_top_same = 5
				
		for parsed_page in parsed_pdf["pages"]:
			
			tables_locs_float = [table_loc for table_loc in self.config["TABLES_LOCS_FLOAT"] if(table_loc["page_number"] == parsed_page["number"])]
			
			
			tables_locs_fixed = [table_loc for table_loc in self.config["TABLES_LOCS_FIXED"] if(table_loc["page_number"] == parsed_page["number"])]
				
			tables_locs = tables_locs_fixed + tables_locs_float
						
			for parsed_text in parsed_page["texts"]:
			
				is_field_value = False
			
				for i, field_loc in enumerate(self.config["FIELDS_LOCS"]):
					
					if( (field_loc["left"] <= parsed_text["left"]) and (parsed_text["right"] <= field_loc["right"]) and  (field_loc["top"] <= parsed_text["top"]) and (parsed_text["bottom"] <= field_loc["bottom"]) ):
						
						page_left_top = str(parsed_page["number"]) + "," + str(field_loc["left"]) + "," + str(field_loc["top"])
						
						if(page_left_top not in model["fields"]):
							model["fields"][page_left_top] = {}
						
						if (field_loc["field_name"] not in model["fields"][page_left_top]):
							model["fields"][page_left_top][field_loc["field_name"]] = []
						
						model["fields"][page_left_top][field_loc["field_name"]].append(parsed_text)
						
						is_field_value = True
						break
						
						
				if(not is_field_value):
				
					for i, table_loc in enumerate(tables_locs):
					
						if( (table_loc["left"] <= parsed_text["left"]) and (parsed_text["right"] <= table_loc["right"]) and  (table_loc["top"] <= parsed_text["top"]) and (parsed_text["bottom"] <= table_loc["bottom"]) ):
							
							page_left_top = str(parsed_page["number"]) + "," + str(table_loc["left"]) + "," + str(table_loc["top"])
												
							if(page_left_top not in model["tables"]):
								model["tables"][page_left_top] = {}
								
								for col_name in table_loc["cols_name"]:
									model["tables"][page_left_top][col_name] = []
							
							
							if( all(abs(parsed_text["top"] - row_top) > threshold_top_same for row_top in table_loc["rows_top"]) or (len(table_loc["rows_top"]) == 0) ):		

								table_loc["rows_top"].append(parsed_text["top"])
								
								for col_name in table_loc["cols_name"]:
									model["tables"][page_left_top][col_name].append([parsed_text_empty])
								
					
							first_col_name = table_loc["cols_name"][0]
							
							if(len(model["tables"][page_left_top][first_col_name]) == 0):
								for col_name in table_loc["cols_name"]:
									model["tables"][page_left_top][col_name].append([parsed_text_empty])
												
							last_row_index = len(model["tables"][page_left_top][first_col_name]) - 1
							found = False
													
							for j, col_left in enumerate(table_loc["cols_left"]):
							
								col_name = table_loc["cols_name"][j]
								
								if(parsed_text["right"] < col_left):
									
									if(model["tables"][page_left_top][col_name][last_row_index][0] == parsed_text_empty):
										model["tables"][page_left_top][col_name][last_row_index][0] = parsed_text
										
									else:

										model["tables"][page_left_top][col_name][last_row_index].append(parsed_text)								
									
									found = True
									break
									
							if(not found):
							
								col_name = table_loc["cols_name"][len(table_loc["cols_name"]) - 1]
							
								if(model["tables"][page_left_top][col_name][last_row_index][0] == parsed_text_empty):
									model["tables"][page_left_top][col_name][last_row_index][0] = parsed_text
										
								else:
									model["tables"][page_left_top][col_name][last_row_index].append(parsed_text)
									
							break
				
		return model
		
		
	def print_model(self, model):
	
		for page_left_top in sorted(model["fields"]):
			print("\n\n\n\n")
			print("page \t left \t top")
			print(page_left_top.replace(",", " \t"))
			
			for field_name in sorted(model["fields"][page_left_top]):
				print("\n")
				print(PdfParser.content_to_unicode(field_name))
				parsed_text = model["fields"][page_left_top][field_name]
				print(PdfParser.content_to_unicode(parsed_text["content"]))
			
	
		for page_left_top in sorted(model["tables"]):
			print("\n\n\n\n\n\n\n\n")
			print("page \t left \t top")
			print(page_left_top.replace(",", " \t"))
			
			for col_name in sorted(model["tables"][page_left_top]):
				print("\n")
				print(PdfParser.content_to_unicode(col_name))
				
				for parsed_text in model["tables"][page_left_top][col_name]:
					print(PdfParser.content_to_unicode(parsed_text["content"]))


def main(argv):						 
	
	basepath = "bp3"

	if(len(argv) > 1):
		basepath = argv[1]

	filepath_pdf_in = basepath + ".pdf"
	filepath_config_in = "pdfparserdata_config_" + basepath + ".json" 
	
	filepath_html_out = basepath + ".html"
	filepath_json_out = basepath + ".json"
	
	filepath_model_json_out = basepath + "_model" + ".json"	
	
		
		
	with open(filepath_config_in) as file_config_in:
		config = json.load(file_config_in)	
	
	pdf_parser_data = PdfParserData(config)
	model = pdf_parser_data.parse_to_model(filepath_pdf_in, filepath_json_out, filepath_html_out)	

	with open(filepath_model_json_out, 'w') as file_model_json_out:
		json.dump(model, file_model_json_out)
		
		
if __name__ == "__main__":

	print("dmpdfparserdata.PdfParserData.main", sys.argv)
	main(sys.argv)
	
	
	
	
	


	

	
	
	
	
	
	
	
	
	
	
	
	