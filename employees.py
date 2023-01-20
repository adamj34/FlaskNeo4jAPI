import asyncio
from flask import request, jsonify, Blueprint
from driver import driver

employees = Blueprint('employees', __name__)

# add new employee
def add_new_employee(tx, new_name, new_last_name, new_job, new_department):

    check_query = f"MATCH (emp:Employee {{name: '{new_name}', last_name: '{new_last_name}', job: '{new_job}'}}) RETURN emp"
    init_res = tx.run(check_query).data()
    print(init_res)

    if not init_res:
        insert_employee = f"CREATE ({new_name}:Employee {{name:'{new_name}', last_name:'{new_last_name}', job:'{new_job}'}})"
        assign_department = f"MATCH (emp:Employee),(dep:Department) WHERE emp.name = '{new_name}' AND emp.last_name = '{new_last_name}' AND dep.name = '{new_department}' CREATE (emp)-[:WORKS_IN]->(dep) RETURN emp"

        tx.run(insert_employee)
        tx.run(assign_department)
        return 'Employee added'
    else:
        return 'This employee already exists'


@employees.route('/employees', methods=['POST'])
def new_employee_route():
    
    print(request.form.get('name'))
    name = request.form.get('name')
    last_name = request.form.get('last_name')
    job = request.form.get('job')
    department = request.form.get('department')

    if not name or not last_name or not job or not department:
        res = {'status': 'Not all fields are filled'}
        return jsonify(res)

    with driver.session() as session:
        status = session.execute_write(add_new_employee, name, last_name, job, department)

    return jsonify({'msg': status})


# get and sort employees
def get_employees(tx, sort_by = '', sort_type = '', filter_phrase = '', filter_by = ''):
    query = "MATCH (emp:Employee) RETURN emp"      

    if (sort_type == 'descending'):
        if (sort_by == 'name'):
            query = "MATCH (emp:Employee) RETURN emp ORDER BY emp.name DESC"
        elif (sort_by == 'last_name'):
            query = "MATCH (emp:Employee) RETURN emp ORDER BY emp.last_name DESC"
        elif (sort_by == 'job'):
            query = "MATCH (emp:Employee) RETURN emp ORDER BY emp.job DESC"

    if (sort_type == 'ascending'):
        if (sort_by == 'name'):
            query = "MATCH (emp:Employee) RETURN emp ORDER BY emp.name"
        elif (sort_by == 'last_name'):
            query = "MATCH (emp:Employee) RETURN emp ORDER BY emp.last_name"
        elif (sort_by == 'job'):
            query = "MATCH (emp:Employee) RETURN emp ORDER BY emp.job"


    if (filter_by == 'name'):
        query = f"MATCH (emp:Employee) WHERE emp.name CONTAINS '{filter_phrase}' RETURN emp"
    elif (filter_by == 'last_name'):
        query = f"MATCH (emp:Employee) WHERE emp.last_name CONTAINS '{filter_phrase}' RETURN emp"
    elif (filter_by == 'job'):
        query = f"MATCH (emp:Employee) WHERE emp.job CONTAINS '{filter_phrase}' RETURN emp"
        
    results = tx.run(query).data()

    workers = [{'name': res['emp']['name'],
               'last_name': res['emp']['last_name']} for res in results]

    return workers


@employees.route('/employees', methods=['GET'])
def get_employees_route():
    args = request.args
    print(args)
    sort_by = args.get("sort_by")
    sort_type = args.get("sort_type")
    filter_phrase = args.get("filter_phrase")
    filter_by = args.get("filter_by")

    with driver.session() as session:
        workers = session.execute_read(get_employees, sort_by, sort_type, filter_phrase, filter_by)

    res = {'workers': workers}
    return jsonify(res)


# get subordinates
def get_subordinates(tx, id):
    find_subordinates_query = f"MATCH (sub:Employee)-[:MANAGES]->(emp:Employee) WHERE id(sub) = {id} RETURN emp"
    subordinates = tx.run(find_subordinates_query).data()
    
    if subordinates:
        subordinates = [{'name': res['emp']['name'],
                        'last_name': res['emp']['last_name']} for res in subordinates]
        return subordinates
    else:
        return 'No subordinates'


@employees.route('/employees/<int:id>/subordinates', methods=['GET'])
def get_subordinates_route(id):
    with driver.session() as session:
        subordinates = session.execute_read(get_subordinates, id)

    res = {'subordinates': subordinates}
    return jsonify(res)


# update employee info
def update_employee(tx, id, new_name, new_last_name, new_job, new_department):
    find_query = f"MATCH (emp:Employee)-[:WORKS_IN]->(dep:Department) WHERE id(emp) = {id} RETURN emp, dep"

    res = tx.run(find_query).data()
    name = new_name or res[0]['emp']['name']
    last_name = new_last_name or res[0]['emp']['last_name']
    job = new_job or res[0]['emp']['job']
    department = new_department or res[0]['dep']['name']
    
    if res:
        update_employee_info = f"MATCH (emp:Employee {{name: '{res[0]['emp']['name']}', last_name: '{res[0]['emp']['last_name']}', job: '{res[0]['emp']['job']}'}}) SET emp.name='{name}', emp.last_name='{last_name}', emp.job='{job}' RETURN emp"

        del_curr_rel = f"MATCH (emp:Employee {{name: '{name}', last_name: '{last_name}', job: '{job}'}})-[r:WORKS_IN]->(dep:Department {{name:'{res[0]['dep']['name']}'}}) DELETE r"

        update_rel = f"MATCH (emp:Employee),(dep:Department) WHERE emp.name = '{name}' AND emp.last_name = '{last_name}' AND emp.job = '{job}' AND dep.name = '{department}' CREATE (emp)-[:WORKS_IN]->(dep) RETURN emp, dep"

        up = tx.run(update_employee_info)
        tx.run(del_curr_rel)
        update_res = tx.run(update_rel).data()
        print(update_res)
        return {'name': update_res[0]['emp']['name'], 'last_name': update_res[0]['emp']['last_name'], 'job': update_res[0]['emp']['job'], 'department': update_res[0]['dep']['name']}
    else:
        return 'Employee with this id not found'


@employees.route('/employees/<int:id>', methods=['PUT'])
def updateWorkerRoute(id):

    name = request.form.get('name')
    last_name = request.form.get('last_name')
    job = request.form.get('job')
    department = request.form.get('department')

    with driver.session() as session:
        res = session.write_transaction(update_employee, id, name, last_name, job, department)

    if res == 'Employee with this id not found':
        response = {'message': res}
        return jsonify(response), 404
    else:
        response = {'status': res}
        return jsonify(response), 201


# delete employee
def delete_employee(tx, id):
    find_query = f"MATCH (emp:Employee)-[rel]->(dep:Department) WHERE id(emp) = {id} RETURN emp,dep,rel"
    res = tx.run(find_query).data()
    name = res[0]['emp']['name']
    last_name = res[0]['emp']['last_name']
    job = res[0]['emp']['job']
    department = res[0]['dep']['name']
    relationship = res[0]['rel'][1]

    if res:
        delete_node_and_rels = f"MATCH (emp:Employee) WHERE emp.name='{name}' AND emp.last_name='{last_name}' AND emp.job = '{job}' DETACH DELETE emp"
        tx.run(delete_node_and_rels)

        left_employees_query = f"MATCH (emp:Employee)-[rel:{relationship}]->(dep:Department) WHERE dep.name = '{department}' RETURN emp, dep, rel"
        employees_left = tx.run(left_employees_query).data()
        
        if not employees_left:
            delete_department = f"MATCH (dep:Department) WHERE dep.name = '{department}' DETACH DELETE dep"
            tx.run(delete_department)
        
        return {'name': name, 'surname': last_name, 'job': job, 'department': department}
    else:
        return 'Employee with this id not found'


@employees.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee_route(id):
    with driver.session() as session:
        res = session.write_transaction(delete_employee, id)

    if res == 'Employee with this id not found':
        response = {'msg': res}
        return jsonify(response), 404
    else:
        response = {'deleted': res}
        return jsonify(response), 204