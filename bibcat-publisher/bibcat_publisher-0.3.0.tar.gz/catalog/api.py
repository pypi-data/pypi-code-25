__author__ = "Jeremy Nelson", "Mike Stabile", "Jay Peterson"

from flask import Blueprint, render_template
#import views
from .views import search_data as search_catalog

catalog = Blueprint('catalog', __name__,
                template_folder='templates')

@catalog.route("/detail")
def record_detail():
    return "In record detail"

@catalog.route("/search", methods=["GET", "POST"])
def search_data():
    #return views.search_data()
    return search_catalog()

@catalog.route("/suggest/<path:name>")
def auto_suggest(name=None):
    return "In auto suggest name={}".format(name)

