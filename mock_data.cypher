CREATE (Angela:Employee {name:"Angela", last_name: "Kinsley", job:"Accountant"})
CREATE (Michael:Employee {name:"Michael", last_name: "Scoot", job:"Boss"})
CREATE (Tobby:Employee {name:"Tobby", last_name:"Flenderson", job:"HR Manager"})
CREATE (Pam:Employee {name:"Pam", last_name: "Beesly", job:"Secretary"})
CREATE (Dwight:Employee {name:"Dwight", last_name: "Schrute", job:"Salesman"})
CREATE (Jim:Employee {name:"Jim", last_name: "Halper", job:"Salesman"})
CREATE (Ryan:Employee {name:"Ryan", last_name: "Howard", job:"Intern"})
CREATE (Creed:Employee {name:"Creed", last_name: "Bratton", job:"Accountant"})


CREATE (Sales:Department {name:"Sales"})
CREATE (HR:Department {name:"HR"})
CREATE (Finance: Department {name:"Finance"})
CREATE (Miscellaneous: Department {name:"Miscellaneous"})


CREATE (Angela)-[:WORKS_IN]->(Finance)
CREATE (Michael)-[:WORKS_IN]->(Miscellaneous)
CREATE (Tobby)-[:WORKS_IN]->(HR)
CREATE (Pam)-[:WORKS_IN]->(Miscellaneous)
CREATE (Dwight)-[:WORKS_IN]->(Sales)
CREATE (Jim)-[:WORKS_IN]->(Sales)
CREATE (Ryan)-[:WORKS_IN]->(Miscellaneous)
CREATE (Creed)-[:WORKS_IN]->(Finance)



CREATE (Creed)-[:MANAGES]->(Angela)
CREATE (Tobby)-[:MANAGES]->(Michael)
    

MATCH (Michael:Employee {name:"Michael", last_name: "Scoot", job:"Boss"})
MATCH (e:Employee)
WHERE e.job <> "Boss"
CREATE (Michael)-[:MANAGES]->(e)




