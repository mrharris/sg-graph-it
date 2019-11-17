from datetime import datetime


def to_uid(entity):
    return "{}:{}".format(entity["type"], entity["id"])


def from_uid(uid):
    try:
        _type, _id = uid.split(":")
        return {"type": _type, "id": int(_id)}
    except ValueError:
        return None


def get_field_value(node, field_name):
    for field in node["fields"]:
        name, value = field["field"], field["value"]
        if field_name == name:
            return value


def ensure_thumbnails(nodes, sg):
    by_entity_type = {}
    for uid, node in nodes.items():
        if not node["image"]:
            entity = from_uid(uid)
            by_entity_type.setdefault(entity["type"], []).append(entity["id"])
    for entity_type, ids in by_entity_type.items():
        for entity in sg.find(entity_type, [["id", "in", ids]], ["image"]):
            nodes[to_uid(entity)]["image"] = entity.get("image")


def apply_grouping(nodes, entity_type, group_field):
    # only supports one level of grouping. implementing multiple levels is not
    # trivial because it either means a node must belong to multiple groups
    # (not supported by gojs) OR it means repeating a node it it appears in
    # multiple groups
    groups = {}
    for uid, node in nodes.items():
        if node["type"] != entity_type:
            # we only want to group nodes of this type
            continue
        group_value = get_field_value(node, group_field)
        node["group"] = group_value
        if group_value not in groups:
            groups[group_value] = {"key": group_value, "text": group_value, "isGroup": True}
    return list(groups.values())


def conform(entity, nodes, links):
    key = to_uid(entity)
    node = {
        "key": key,
        "name": entity.get("name", entity.get("code", entity.get("title", entity.get("content", "UNKNOWN")))),
        "type": entity["type"],
        "image": entity.get("image", None),
        "fields": [],
    }

    # recurse through any linked entities
    for field, value in entity.items():
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if isinstance(v, dict) and "id" in v:
                # value is another entity
                links.append({"from": key, "fromPort": field, "to": to_uid(v)})
                conform(v, nodes, links)

    # process the entity fields
    for field, value in entity.items():
        # skip fields we already have
        if field in ("name", "type", "image"):
            continue
        # convert entities into just their "name" value
        elif isinstance(value, list):
            value = ",".join([v["name"] for v in value])
        elif isinstance(value, dict):
            value = value["name"]
        # move linked fields to their respective entity
        elif "." in field:
            sfn, en, dfn = field.split(".")
            target_entity = entity[sfn]
            if target_entity is None:
                # linked field does not link to anything
                continue
            target_node = nodes[to_uid(target_entity)]
            target_node["fields"].append({"field": dfn, "value": value})
            continue
        elif isinstance(value, datetime):
            value = str(value)
        if isinstance(value, str):
            # truncate the string
            value = value[:80] + (value[80:] and '..')
        node.setdefault("fields", []).append({"field": field, "value": value})

    nodes.setdefault(key, {}).update(node)
