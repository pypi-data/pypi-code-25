#!/usr/bin/env python3

from __future__ import division

import matplotlib
matplotlib.use('Agg')
from InfluenceManager.definitions import INFDB
from twython import Twython
from InfluenceManager.scripts.influencer_cloud import InfluencerCloud
import traceback
import operator
import argparse
import networkx as nx
import matplotlib.pyplot as plt

CONSUMER_KEY = "qOQAlcqYI0NNdrFBEve5ANNDJ"
CONSUMER_SECRET = "gVngoxEyPtNKkRIQ7eGVyuQAUPA7I2oLqjmlhze0Pz1UnijDgL"
MAX_ATTEMPTS = 10
COUNT_TO_BE_FETCHED = 500


def parse():
    parser = argparse.ArgumentParser(description="Options for InfluenceManager")
    parser.add_argument("-t", "--topic", required=True, dest="topic")
    parser.add_argument("-q", "--query", required=True, dest="query")
    parser.add_argument("-r", "--top_results", default=5, required=False, dest="top_results")
    parser.add_argument("-u", "--update", default=False, required=False, dest="update")
    parser.add_argument("-s", "--stats", default=False, required=False, dest="stats")
    parser.add_argument("--sanitise", default=True, required=False, dest="sanitise")

    arguments = parser.parse_args()
    return arguments


def assign_network(G, user_data):
    edge_list = []
    G.add_nodes_from(user["username"] for user in user_data)
    for user in user_data:
        username = user["username"]
        for connected_user in user["connected_users"]:
            edge_list.append((username, connected_user))
            G.add_edge(username, connected_user)

    degree = nx.degree(G)
    edges = G.number_of_edges()
    return G, degree, edge_list, edges


class TopicQuery:
    def __init__(self, query_topic, params):
        self.topic = query_topic
        self.params = params
        self.twitter_api = Twython(CONSUMER_KEY, CONSUMER_SECRET)
        self.topic_db = INFDB["topics"]
        self.users = []
        self.upper_quartile = 0
        self.top_results = []
        self.sanitised_list = []
        self.iterations = 0
        self.output_dir = ""

        # for file in os.listdir("/var/www/html/InfluenceProfiler/"):
        #     if file.endswith(".png"):
        #         os.remove(file)

    def get_influencers(self):
        tweets = []

        for i in range(0, MAX_ATTEMPTS):
            next_max_id = None
            if COUNT_TO_BE_FETCHED < len(tweets):
                break
            if 0 == i:
                results = self.twitter_api.search(q="'{0}'".format(self.topic), count='100')
            else:
                results = self.twitter_api.search(q="'{0}'"
                                                  .format(self.topic), include_entities=True, max_id=next_max_id)

            for result in results["statuses"]:
                username = result["user"]["screen_name"]

                if not result["entities"]["user_mentions"] or len(result["entities"]["user_mentions"]) < 3:
                    continue
                else:
                    idx = next((index for (index, d) in enumerate(self.users) if d["username"] == username), None)
                    if idx is not None:
                        for mention in result["entities"]["user_mentions"]:
                            if mention["screen_name"] not in self.users[idx]["connected_users"]:
                                self.users[idx]["connected_users"].append(mention["screen_name"])
                        self.users[idx]["number_of_connections"] = len(self.users[idx]["connected_users"])
                    else:
                        connected_users = [mention["screen_name"] for mention in result["entities"]["user_mentions"]]
                        new_user = {
                            "username": username,
                            "connected_users": connected_users,
                            "number_of_connections": len(connected_users)
                        }

                        self.users.append(new_user)
            try:
                next_results_url_params = results["search_metadata"]["next_results"]
                next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
            except KeyError:
                continue

        self.users.sort(key=operator.itemgetter("number_of_connections"), reverse=True)
        self.add_topic()

    def update_topic_users(self):
        existing_usernames = []
        query_result = self.topic_db.find({"_id": self.topic}, {"users": 1, "_id": 0})
        for user in query_result[0]["users"]:
            existing_usernames.append(user["username"])

        new_usernames = [user["username"] for user in self.users]
        duplicate_users = list(set(new_usernames) & set(existing_usernames))
        db_users = list(query_result)[0]["users"]

        if duplicate_users is not None:
            for d_user in duplicate_users:
                duplicate_idx = next((index for (index, d) in enumerate(self.users) if d["username"] == d_user), None)
                user_idx = next((index for (index, d) in enumerate(db_users) if d["username"] == d_user), None)

                latest_connections = self.users[duplicate_idx]["connected_users"]
                db_connections = db_users[user_idx]["connected_users"]

                new_connections = db_connections.extend([i for i in latest_connections if i not in db_connections])
                new_entry = db_users[user_idx]

                if new_connections is not None:
                    new_number = len(new_connections)
                    new_entry["connected_users"] = new_connections
                    new_entry["number_of_connections"] = new_number

                    db_users[user_idx] = new_entry

                del self.users[duplicate_idx]

        new_entries = db_users + self.users

        self.topic_db.update_one({
            "_id": self.topic,
        }, {
            "$set": {
                "users": new_entries
            }
        })

    def add_topic(self):
        topic_doc = {
            "_id": self.topic,
            "users": self.users
        }
        check_query = self.topic_db.find_one({"_id": self.topic})

        if not check_query:
            self.topic_db.insert(topic_doc)
        else:
            self.update_topic_users()

    def create_influence_map(self):
        G = nx.Graph()

        user_data = self.get_topic_data()
        G, degree, edge_list, edges = assign_network(G, user_data)
        node_labels, node_sizes, colour_list = self.get_node_stats(degree)

        if self.params["sanitise"] == "True":
            G.clear()
            G, degree, edge_list, edges = assign_network(G, self.sanitise_topic(user_data))
            node_labels, node_sizes, colour_list = self.get_node_stats(degree)

        if len(degree) < 250:
            scale = 1
        else:
            scale = (len(degree) // 250) / 10
        pos = nx.spring_layout(G)
        for i in pos:
            pos[i][0] = pos[i][0] * scale
            pos[i][1] = pos[i][1] * scale

        fig = plt.figure()
        plt.title("'{0}' Influence Map".format(self.topic.title()), color="white")
        nx.draw(G, pos=pos, arrows=False, with_labels=False, node_size=node_sizes, node_color=colour_list)
        nx.draw_networkx_edges(G, pos=pos, edgelist=edge_list, edge_color="#839496")
        nx.draw_networkx_labels(G, pos=pos, labels=node_labels, font_size=8, font_color="white", font_weight="bold")
        fig.set_facecolor("#002b36")

        if self.params["stats"] == "True":
            print("Nodes: " + str(len(degree)))
            print("Edges: " + str(edges))
            print("Scale: " + str(scale))
            for user in self.top_results:
                print("{0}: {1}".format(user[0], user[1]))

        plt.show()
        # self.output_dir = "/var/www/html/InfluenceProfiler/{0}_{1}_".format(self.params["query"], self.topic)

        # fig.savefig("{0}imap.png".format(self.output_dir), dpi=300, facecolor="#002b36", bbox_inches="tight")

    def get_node_stats(self, nodes):
        self.top_results[:] = []
        top_results = 0 - abs(int(self.params["top_results"]))
        total_nodes = len(nodes)

        node_list = list(nodes)
        sorted_node_list = sorted(node_list, key=operator.itemgetter(1))
        self.upper_quartile = int((total_nodes + 1) * 0.75)
        u_q_list = sorted_node_list[self.upper_quartile:]

        node_labels = {}
        size_list = []
        colour_list = []
        for node in node_list:
            if len(u_q_list) <= top_results:
                node_labels[node[0]] = node[0]
            if node in u_q_list[top_results:] and node[1]:
                self.top_results.append(node)
                node_labels[node[0]] = node[0]
                if node == u_q_list[-1]:
                    size_list.append((node[0], node[1] * 15))
                    colour_list.append("#dc322f")
                else:
                    size_list.append((node[0], node[1] * 10))
                    colour_list.append("#2aa198")
            else:
                size_list.append(node)
                colour_list.append("#268bd2")

        self.top_results.sort(key=operator.itemgetter(1), reverse=True)
        return node_labels, [node[1] * 5 for node in nodes], colour_list

    def get_topic_data(self):
        query_result = self.topic_db.find({"_id": self.topic}, {"users": 1, "_id": 0})

        return list(query_result)[0]["users"]

    def sanitise_topic(self, user_data):
        top_usernames = [user[0] for user in self.top_results]
        total_connections = 0
        sub_mean_users = []

        for user in user_data:
            total_connections += user["number_of_connections"]

        for idx, user in enumerate(user_data):
            username = user["username"]
            no_connections = user["number_of_connections"]
            connected_to_top = bool(set(user["connected_users"]) & set(top_usernames))
            if username not in top_usernames and not connected_to_top and no_connections < self.upper_quartile:
                sub_mean_users.append(user_data[idx])

        sanitised_list = [user for user in user_data if user not in sub_mean_users]
        return sanitised_list


if __name__ == '__main__':
    args = vars(parse())

    topic = args["topic"].lower().replace("_", " ")
    log_file = open("/tmp/log_{0}".format(args["query"]), "w+")
    try:
        tq = TopicQuery(topic, args)
        tq.get_influencers()

        if not args["update"]:
            tq.create_influence_map()

            cloud = InfluencerCloud(topic, tq.twitter_api, tq.top_results, tq.output_dir)
            cloud.create_cloud()
            cloud.create_mention_cloud()
            username = cloud.username

            print(username)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        # log_file.write(str(e))
        # log_file.write(traceback.format_exc())
