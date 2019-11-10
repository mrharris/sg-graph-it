def to_uid(entity):
    return hash((entity["id"], entity["type"]))


def conform(entity, nodes, links):
    key = to_uid(entity)
    node = {
        "key": key,
        "name": entity.get("name", entity.get("code", entity.get("title", entity.get("content", "UNKNOWN")))),
        "type": entity["type"],
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
        if field in ("name", "type"):
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
            target_node = nodes[to_uid(target_entity)]
            target_node["fields"].append({"field": dfn, "value": value})
            continue
        node.setdefault("fields", []).append({"field": field, "value": value})

    nodes.setdefault(key, {}).update(node)
