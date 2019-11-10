import os

from flask import request, render_template, jsonify, url_for
import shotgun_api3

from . import app
from . import util


sg = shotgun_api3.Shotgun(
    os.environ.get("SG_URL"),
    script_name=os.environ.get("SG_SCRIPT_NAME"),
    api_key=os.environ.get("SG_SCRIPT_KEY"),
)


# @app.route('/', methods=["POST"])
# def hello_world():
#     post_dict = request.form.to_dict()
#     from pprint import pprint
#     pprint(post_dict)
#     entity_type = post_dict["entity_type"]
#     entity_ids = post_dict["selected_ids"] or post_dict["ids"]
#     entity_ids = [int(id_) for id_ in entity_ids.split(",")]
#     fields = post_dict["cols"].split(",")
#     fields.extend(post_dict["grouping_columns"].split(","))
#
#     # if the fields contain a linked field (eg created_by.HumanUser.firstname)
#     # then also query for the entity itself (HumanUser) so that we can make a node
#     fields.extend([f.split(".")[0] for f in fields if "." in f])
#
#     project = {"type": "Project", "id": int(post_dict["project_id"])}
#     entities = sg.find(entity_type, [["id", "in", entity_ids], ["project", "is", project]], fields)
#
#     nodes = {}
#     links = []
#     for entity in entities:
#         util.conform(entity, nodes, links)
#
#     # TODO the nested grouping needs to be respected
#     data = {
#         "nodes": list(nodes.values()),
#         "links": links
#     }
#     print(data["nodes"])
#     print("=============")
#     print(data["links"])
#     print("=============")
#     return jsonify(data)


@app.route('/')
def index():
    print(">>>")
    # print(url_for("index.html"))
    return render_template("index.html")


if __name__ == '__main__':
    app.run()


"""
    schema = sg.schema_field_read(entity_type, project_entity=project)
    query_fields = []
    for field_name, field_data in schema.items():
        if field_name in fields and field_data["data_type"]["value"] in ["multi_entity", "entity"]:
            query_fields.append(field_name)
"""
