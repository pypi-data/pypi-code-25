#!/usr/bin/python
#coding:utf-8


import sys
import json

import unicodedata

import os
import subprocess

import codecs

from lxml import etree
from lxml.etree import Element


class PdfParser(object):

	@staticmethod
	def run_cmd_array(cmd):

		proc = subprocess.Popen \
		(
		cmd, 
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		stdin = subprocess.PIPE \
		)

		out, err = proc.communicate()

		rslt = \
		{
		"out": out,
		"err": err
		}
	 
		return rslt
	
	
	@staticmethod 
	def content_to_unicode(content):
	
		content_out = unicodedata.normalize('NFKD', unicode(content)).encode('utf-8','ignore')
		
		return content_out
		

	@staticmethod
	def parse(filepath_pdf):	
		
		parsed_pdf = None
		
		basepath, extension = os.path.splitext(filepath_pdf)	
		filepath_xml = basepath + ".xml"	
		
		cmd = ["pdftohtml", "-hidden", "-i", "-c", "-noframes", "-nomerge", "-xml", filepath_pdf, filepath_xml]
		rslt = PdfParser.run_cmd_array(cmd)
		
		xml_tree = etree.parse(filepath_xml)
		xml_node_pdf2xml = xml_tree.xpath("/pdf2xml")[0]
		
		parsed_pdf = { "pages" : [] }
			
		for xml_node_page in xml_node_pdf2xml.findall("page"):
			
			parsed_page = \
			{
			"number": xml_node_page.get("number"),
			"width": xml_node_page.get("width"),
			"height": xml_node_page.get("height"),
			"fontspecs": [],
			"texts": [],
			}
			
			parsed_pdf["pages"].append(parsed_page)
			
			for xml_node_fontspec in xml_node_page.findall("fontspec"):
				
				parsed_fontspec = \
				{
				"id": xml_node_fontspec.get("id"), 
				"size": int(xml_node_fontspec.get("size")),
				"family": xml_node_fontspec.get("family"),
				"color": xml_node_fontspec.get("color"),
				}
				
				parsed_fontspec["color"] = "#000000"
				
				parsed_page["fontspecs"].append(parsed_fontspec)
				
			for xml_node_text in xml_node_page.findall("text"):
				
				parsed_text = \
				{
				"left": int(xml_node_text.get("left")),
				"top" : int(xml_node_text.get("top")), 				
				
				"width": int(xml_node_text.get("width")),
				"height": int(xml_node_text.get("height")),
				
				"font_id": xml_node_text.get("font"),
				"content": xml_node_text.xpath("string()") #etree.tostring(xml_node_text, method = "text")
				}
				
				if(parsed_text["content"] is None):
					print("\n\n\n\n\n")
					print("content none")
					print(xml_node_text)
				
				parsed_text["right"] = parsed_text["left"] + parsed_text["width"]
				parsed_text["bottom"] = parsed_text["top"] + parsed_text["height"]
							
				content_out = PdfParser.content_to_unicode(parsed_text["content"])
				
				if( (len(content_out) > 0) and not (content_out == "\xe2\x9e\xa1") ):		
					parsed_page["texts"].append(parsed_text)
		
		
		parsed_pdf["fontspecs"] = [fontspec for parsed_page in parsed_pdf["pages"] for fontspec in parsed_page["fontspecs"]]
		
		return parsed_pdf
		
		
	@staticmethod
	def save_parse(filepath_pdf_in, filepath_json_out):
		
		parsed_pdf = PdfParser.parse(filepath_pdf_in)
	
		with open(filepath_json_out, 'w') as outfile:
			json.dump(parsed_pdf, outfile)
		
		return parsed_pdf
		
		
	@staticmethod
	def parsed_fontspec_to_htmlstyle(parsed_fontspec):
	
		style = '.ft' + parsed_fontspec["id"] + '{font-size:' + str(parsed_fontspec["size"]) + 'px;font-family:' + parsed_fontspec["family"] + ';color:' + parsed_fontspec["color"] + ';}'
		
		return style
		
		
	@staticmethod
	def parsed_fontspecs_to_htmlstyle(parsed_fontspecs):
	
		htmlstyle = '<STYLE type="text/css">'
		
		for parsed_fontspec in parsed_fontspecs:
		
			fontstyle = PdfParser.parsed_fontspec_to_htmlstyle(parsed_fontspec)
			htmlstyle = htmlstyle + '\n' + fontstyle
			
		htmlstyle = htmlstyle + '\n' + '</STYLE>'
		
		return htmlstyle
		
		
	@staticmethod
	def parsed_text_to_html(parsed_text):
	
		html = '<DIV style="border-style:solid;border-color:#00FF00;position:absolute;top:' + str(parsed_text["top"]) + ';left:' + str(parsed_text["left"]) + ';width:' + str(parsed_text["width"]) + ';height:' + str(parsed_text["height"]) + '"><nobr><span class="ft' + str(parsed_text["font_id"]) + '">' + parsed_text["content"] + '</span></nobr></DIV>'
			
		return html
		
		
	@staticmethod
	def parsed_texts_to_html(parsed_texts):
	
		html = ''
		
		for parsed_text in parsed_texts:
		
			html_text = PdfParser.parsed_text_to_html(parsed_text)
			html = html + '\n' + html_text
			
		
		return html
		
	
	@staticmethod
	def parsed_page_to_html(parsed_page):
	
		html_texts = PdfParser.parsed_texts_to_html(parsed_page["texts"])
	
		html = '<DIV style="position:relative;height:' + str(parsed_page["height"]) + ';width:' + str(parsed_page["width"]) + ';" id="' + parsed_page["number"] +'">' + html_texts + '</DIV>'		
		
		return html
		
		
	@staticmethod
	def parsed_pages_to_html(parsed_pages):
	
		html = '<DIV>'
		
		for parsed_page in parsed_pages:
			html_page = PdfParser.parsed_page_to_html(parsed_page)
			html = html + '\n' + html_page
	
		html = html + '\n' + '</DIV>'		
		
		return html
		
		
	@staticmethod
	def generate_javascript_mouse_tracker():
		html = '<script language="JavaScript" src="./mouse_tracker.js"></script>'
		return html
		
	@staticmethod
	def parsed_pdf_to_html(parsed_pdf):
		
		htmlscript = PdfParser.generate_javascript_mouse_tracker()
		htmlstyle = PdfParser.parsed_fontspecs_to_htmlstyle(parsed_pdf["fontspecs"])
		html_pages = PdfParser.parsed_pages_to_html(parsed_pdf["pages"])
		
		html = '<HTML>' + '\n' + '<BODY>' + '\n' + htmlscript + '\n' + htmlstyle + '\n' + html_pages + '\n' + '</BODY>' + '\n' + '</HTML>'
		
		return html
	
	@staticmethod
	def save_parsed_pdf_to_html(parsed_pdf, filepath_html):
		
		html = PdfParser.parsed_pdf_to_html(parsed_pdf)
	
		with codecs.open(filepath_html, 'w', "utf-8") as outfile:	
			outfile.write(html)
		
		return html
		

def main(argv):						 
	
	basepath = "dt1"
	
	filepath_pdf_in = basepath + ".pdf"
	
	filepath_json_out = basepath + ".json"
	filepath_html_out = basepath + ".html"
	
	

	if(len(argv) > 1):
		filepath_pdf_in = argv[1]
		
	
	parsed_pdf = PdfParser.save_parse(filepath_pdf_in, filepath_json_out)
	
	PdfParser.save_parsed_pdf_to_html(parsed_pdf, filepath_html_out)
		
if __name__ == "__main__":
	
	print("dmpdfparser.PdfParser.main", sys.argv)
	main(sys.argv)
	
	
	
	
	


	

	
	
	
	
	
	
	
	
	
	
	
	