##parameters=dir, datastructure, **kw

datamodel = datastructure.getDataModel()

mapping = {}
for key, value in datamodel.items():
    if value:
        mapping[key] = value

result_fields = context.getDirectoryResultFields(dir.getId(), dir.title_field)

aclu = context.acl_users
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
mtool = context.portal_membership
if call_context is not None:
    dict_roles = mtool.getMergedLocalRoles(call_context, withgroups=0)
    search_restricted_list = dict_roles.keys()
    mapping[dir.id_field] = search_restricted_list
results = dir.searchEntries(return_fields=return_fields, **mapping)

#
# Check if there's groups with local roles
#

dict_roles = mtool.getMergedLocalRoles(call_context, withgroups=1)
groups = [x[len('group:'):] for x in dict_roles if x.startswith('group:')]

# special handling of special groups to behave as the RecipientRules logic
if "role:Authenticated" in groups and not aclu.is_role_authenticated_empty:
    results = dir.searchEntries(return_fields=return_fields)
    skip_groups = True
elif "role:Anonymous" in groups and not aclu.is_role_anonymous_empty:
    results = dir.searchEntries(return_fields=return_fields)
    skip_groups = True
else:
    skip_groups = False

if not skip_groups:
    for group_id  in groups:
        group_mapping = {'groups': [group_id]}
        group_member_results = dir.searchEntries(return_fields=return_fields,
                                                 **group_mapping)
        for member in group_member_results:
            if member not in results:
                results.append(member)

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
