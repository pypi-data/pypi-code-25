import pkg_resources
import click
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from flask import abort, flash, jsonify, redirect, render_template 
from flask import request, url_for
from flask_dance.contrib.google import google
from flask_dance.contrib.facebook import facebook
from .forms import LoginForm
#try:
#    es = Elasticsearch(
#        current_app.config.get("ELASTICSEARCH", "localhost"))
#except:
es = Elasticsearch()

def internal_server_error(e):
    return render_template("500.html", error=e), 500

def search_data():
    output_format, output = "html", []
    if request.method.startswith("POST"):
        query_phrase = request.form.get("query")
        offset = request.form.get("offset", 0)
    else:
        query_phrase = request.args.get("query")
        offset = request.args.get("offset", 0)
    search = Search(using=es)
    search = search.query(
        Q("query_string", 
          query=query_phrase,
          default_operator="AND")).params(size=4, 
              from_=offset)
    results = search.execute()
    if output_format.startswith("json"):
        return jsonify(output)
    return render_template("search-results.html",
        results=results,
        offset=offset,
        query_phrase=query_phrase)


def suggest(name=None):
    if not name:
        return
    query = request.args.get("q")
    name = name.lower()
    search = Search(using=es)
    if name.startswith("work"):
        search = search.query(
            Q("match", value=query)).source(include=["value"])
    results = search.execute() 
    soup = BeautifulSoup('', 'lxml')
    output = soup.new_tag("div", style="padding: 1em 2m")
    for row in results.hits.hits:
        link = soup.new_tag("a", 
            href="{}?id={}".format(url_for('detail'),
                                   row.get("_id")))
        link.string = row.get("_source").get("value")
        output.append(link)
        output.append(soup.new_tag("br"))
    return jsonify({"html": output.prettify()})


def detail():
    ident = request.args.get("id")
    
    return render_template("detail.html")


def profile(service=None):
    if service.endswith("google"):
        if not google.authorized:
            return redirect(url_for("google.login"))
        resp = google.get("/oauth2/v2/userinfo")
        assert resp.ok, resp.text
        print(resp.json())
        return "Your Google {email}".format(email=resp.json()["email"])
    elif service.endswith("facebook"):
        if not facebook.authorized:
            return redirect(url_for("facebook.login"))
        resp = facebook.get("/oauth2/v2/userinfo")
        assert resp.ok, resp.text
        print(resp.json())
        return "Your Facebook Authorization and {email}".format(
            email=resp.json()["email"])
    else:
        return render_template("profile.html")
    return abort(404)

def publisher_login():
    login_form = LoginForm()
#    if request.method.startswith("POST"):
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        return redirect("profile")
    return render_template("login.html", form=login_form)
   
def home():
    flash("Public Message")
    return render_template("index.html")
