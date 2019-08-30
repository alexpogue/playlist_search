from flask import abort, jsonify

def get_by_id(model_cls, lookup_id, schema):
    model_obj = model_cls.query.get(lookup_id)
    if model_obj is None:
        abort(404)
    result = schema.dump(model_obj)
    result_without_errors = result[0]

    table_name = model_cls.__table__.name
    keyed_result = {table_name: result_without_errors}
    return jsonify(keyed_result)

