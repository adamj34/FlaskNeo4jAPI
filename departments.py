import asyncio
from flask import request, jsonify, Blueprint
from driver import driver

departments = Blueprint('departments', __name__)


# get departments
def get_departments(tx, sort_by = '', sort_type = '', filter_phrase = '', filter_by = ''):
    query = "MATCH (dept:Department) RETURN dept"
    print(filter_by, filter_phrase)
    if (sort_type == 'descending'):
        if (sort_by == 'name'):
            query = "MATCH (dept:Department) RETURN dept ORDER BY dept.name DESC"
        elif (sort_by == 'number_of_employees'):
            query = "MATCH (dept:Department)<-[:WORKS_IN]-(e:Employee) WITH dept, count(e) as num_of_employees RETURN dept, num_of_employees ORDER BY num_of_employees DESC"

    if (sort_type == 'ascending'):
        if (sort_by == 'name'):
            query = "MATCH (dept:Department) RETURN dept ORDER BY dept.name"
        elif (sort_by == 'number_of_employees'):
            query = "MATCH (dept:Department)<-[:WORKS_IN]-(e:Employee) WITH dept, count(e) as num_of_employees RETURN dept, num_of_employees ORDER BY num_of_employees DESC"

    if (filter_by == 'name'):
        print('here')
        query = f"MATCH (dept:Department) WHERE dept.name CONTAINS '{filter_phrase}' RETURN dept"
        
    results = tx.run(query).data()
    departments = [{'name': res['dept']['name']} for res in results]

    return departments


@departments.route('/departments', methods=['GET'])
def get_departments_route():
    args = request.args
    sort_by = args.get("sort_by")
    sort_type = args.get("sort_type")
    filter_phrase = args.get("filter_phrase")
    filter_by = args.get("filter_by")

    with driver.session() as session:
        departments = session.execute_read(get_departments, sort_by, sort_type, filter_phrase, filter_by)

    res = {'departments': departments}
    return jsonify(res)



# get employees in department
def get_employees_in_department(tx, department):
    query = f"MATCH (e:Employee)-[:WORKS_IN]->(d:Department) WHERE d.name = '{department}' RETURN e"

    if query:
        results = tx.run(query).data()
        employees = [{'name': res['e']['name'], 'last_name': res['e']['last_name']} for res in results]
    else:
        return "Department not found."

    return employees


@departments.route('/departments/<string:department>/employees', methods=['GET'])
def get_employees_in_department_route(department):
    with driver.session() as session:
        employees = session.execute_read(get_employees_in_department, department)

    res = {'msg': employees}
    return jsonify(res)