##parameters=dir, datastructure, **kw

from cgi import escape

datamodel = datastructure.getDataModel()

mapping = {}
for key, value in datamodel.items():
    if value:
        mapping[key] = value

result_fields = context.getDirectoryResultFields(dir.getId(),
                                                 dir.title_field)

return_fields = []
sort_by = None
sort_direction = None
process_fields = {}
for field in result_fields:
    return_fields.append(field['id'])
    sorted = field.get('sort')
    if sorted == 'asc':
        sort_by = field['id']
        sort_direction = 'asc'
    elif sorted == 'desc':
        sort_by = field['id']
        sort_direction = 'desc'
    if field.get('process'):
        process_fields[field['id']] = field['process']

    call_context = kw.get('call_context')
    if call_context is not None:
        mtool = context.portal_membership
        dict_roles = mtool.getMergedLocalRoles(call_context, withgroups=0)
        search_restricted_list = dict_roles.keys()
        mapping['search_restricted_member_list'] = search_restricted_list
    results = dir.searchEntries(return_fields=return_fields,
                                **mapping)

for field, process_meth in process_fields.items():
    meth = getattr(context, process_meth, None)
    if not meth:
        continue
    for item in results:
        value = item[1].get(field)
        item[1][field] = meth(field, value)

if sort_by:
    items = [(item[1].get(sort_by), item) for item in results]
    items.sort()
    if sort_direction == 'desc':
        items.reverse()
    results = [item[1] for item in items]

rendered = dir.content_notify_email_search_results(results=results)

return rendered, 'results'
