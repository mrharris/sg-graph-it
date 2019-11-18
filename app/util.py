from datetime import datetime
import collections


def to_uid(entity):
    return "{}:{}".format(entity["type"], entity["id"])


def from_uid(uid):
    try:
        _type, _id = uid.split(":")
        return {"type": _type, "id": int(_id)}
    except ValueError:
        return None


def has_field(node, field_name):
    for field in node["fields"]:
        name, value = field["field"], field["value"]
        if field_name == name:
            return True
    return False


def get_field_value(node, field_name):
    for field in node["fields"]:
        name, value = field["field"], field["value"]
        if field_name == name:
            return value
    raise LookupError("Field {} is not a member of node {}".format(field_name, node["key"]))


def query_additional_fields(nodes, by_entity_type, sg):
    for entity_type, data in by_entity_type.items():
        ids = data["ids"]
        fields = data["fields"]
        for entity in sg.find(entity_type, [["id", "in", list(ids)]], list(fields)):
            node = nodes[to_uid(entity)]
            for field in fields:
                if field == "image":
                    node["image"] = entity.get("image")
                else:
                    if not has_field(node, field):
                        node["fields"].append({"field": field, "value": entity[field]})


def get_additional_fields(nodes, fields, entity_type_filter=None):
    """
    {
        Asset: {
            ids: [23,5,688],
            fields: [image],
        }
        Task: {
            ids: [23,5,688],
            fields: [image],
        }
    }
    """
    by_entity_type = {}
    for uid, node in nodes.items():
        for field in fields:
            if not has_field(node, field):
                entity = from_uid(uid)
                entity_type, entity_id = entity["type"], entity["id"]
                if entity_type_filter and entity_type not in entity_type_filter:
                    continue
                by_entity_type.setdefault(entity_type, {"ids": set(), "fields": set()})
                by_entity_type[entity_type]["ids"].add(entity_id)
                by_entity_type[entity_type]["fields"].add(field)
    return by_entity_type


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
        if not has_field(node, group_field):
            continue
        group_value = get_field_value(node, group_field)
        if group_value:
            if isinstance(group_value, list):
                group_value = ",".join([v["name"] for v in group_value])
            elif isinstance(group_value, dict):
                group_value = group_value["name"]
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


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]