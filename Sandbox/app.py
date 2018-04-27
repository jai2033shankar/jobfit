# Dependencies
import pymongo
from pymongo import MongoClient
from flask import(
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for
    )
import numpy as np
import pandas as pd
import json
import ast
import predict_score_users


# Initialize the Flask application
app = Flask(__name__)

# MongoDB Connection
client = MongoClient('mongodb://Aiyana:jobfitt@ds253889.mlab.com:53889/jobfitt')
# Get the sampleDB database
db = client.get_database()
# Initialize the collections to variables
Education_Experience_collection = db.Education_Experience
Alternate_Titles_collection = db.Alternate_Titles 
Job_State_Salary_collection = db.Job_State_Salary 
Knowledge_Cluster_collection  = db.Knowledge_Cluster 
Salary_State_Year_collection = db.Salary_State_Year
Occupation_collection = db.Occupation 
user_input_collection = db.user_data

# App route definitions
@app.route("/")
@app.route("/index")
def landing():
    return(render_template("index.html"))

@app.route("/survey")
def survey():
    return(render_template("mysearch.html"))

@app.route("/result")
def result():
    return(render_template("results.html"))

@app.route("/trends")
def trends():
    return(render_template("trends.html"))

@app.route("/about")
def about():
    return(render_template("about.html"))
@app.route("/data")
def dataSearch():
    return(render_template("dataSearch.html"))

@app.route("/Education_Experience")
def pymongo_Education_Experience_display():
    Education_Experience_result=[]
    print("Retrieving Data from Mongo Education_Experience")
    cursor = Education_Experience_collection.find({})
    for document in cursor:
        document.pop("_id")
        Education_Experience_result.append(document)
    return jsonify(Education_Experience_result)


@app.route("/Alternate_Titles")
def pymongo_Alternate_Titles_display():
    Alternate_Titles_result=[]
    print("Retrieving Data from Mongo Alternate_Titles")
    cursor = Alternate_Titles_collection.find({})
    for document in cursor:
        document.pop("_id")
        Alternate_Titles_result.append(document)
    return jsonify(Alternate_Titles_result)


@app.route("/Job_State_Salary")
def pymongo_Job_State_Salary_display():
    Job_State_Salary_result=[]
    print("Retrieving Data from Mongo Job_State_Salary")
    cursor = Job_State_Salary_collection.find({})
    for document in cursor:
        document.pop("_id")
        Job_State_Salary_result.append(document)
    return jsonify(Job_State_Salary_result)


@app.route("/Knowledge_Cluster")
def pymongo_Knowledge_Cluster_display():
    Knowledge_Cluster_result=[]
    print("Retrieving Data from Mongo Knowledge_Cluster")
    cursor = Knowledge_Cluster_collection.find({})
    for document in cursor:
        document.pop("_id")
        Knowledge_Cluster_result.append(document)
    return jsonify(Knowledge_Cluster_result)


@app.route("/Salary_State_Year")
def pymongo_Salary_State_Year_display():
    Salary_State_Year_result=[]
    print("Retrieving Data from Mongo Salary_State_Year")
    cursor = Salary_State_Year_collection.find({})
    
    for document in cursor:
        document.pop("_id")
        try:
            document["Salary_2015"]=float(document["Salary_2015"].replace("$","").replace(",",""))
            document["Salary_2017"]=float(document["Salary_2017"].replace("$","").replace(",",""))
        except:
            pass
        Salary_State_Year_result.append(document)
    return jsonify(Salary_State_Year_result)

@app.route("/Occupation")
def pymongo_Occupation_display():
    Occupation_result=[]
    print("Retrieving Data from Mongo Occupation")
    cursor = Occupation_collection.find({})
    for document in cursor:
        document.pop("_id")
        Occupation_result.append(document)
    return jsonify(Occupation_result)

@app.route('/Predict_Score_Users', methods=['POST'])
def pymongo_Predict_Score_Users():
    
    # Read input info  => Read the hidden input that has info submitted by user 
    # user_input = request.form["USERINPUT"] 
    #user_dict1 = request.form.get()
    #user_dict1 = request.form.get("USERINPUT")
    #first_name = request.form.get("Name")
    #phone1 = request.form.get("Phone")
    print('In Predict Score users - Printing user input')
    user_dict1 = request.form.get('data')
    print(user_dict1)

    input_dict = ast.literal_eval(user_dict1)
    print(input_dict['Name'])
    print(input_dict['Skills'])

    result_id = user_input_collection.insert(input_dict)  #posting.__dict__
    # Give info of inserted IDs
    print(f"Inserted record ID: {result_id}")


    #Write info into collection with predicted values 
    print("Reading user input info")
    #print (user_input)

    #Write info in the collection object 
    Knowledge_Cluster_result=[]
    print("Retrieving Data from Mongo Knowledge_Cluster")
    cursor = Knowledge_Cluster_collection.find({})
    for document in cursor:
        document.pop("_id")
        Knowledge_Cluster_result.append(document)

    #TODO -> Also pass the user_response collection on latest submission
    skills_input = {}
    skills_input = input_dict['Skills']
    print("SKILLS INPUT TO predict_title_grouping")
    print(skills_input)
    print(f"Type of skills_input to Predict: {type(skills_input)}")
    
    predicted_title_group = predict_score_users.predict_title_grouping(Knowledge_Cluster_result, skills_input)

    #Get the Education Experinece Scoring Data present 
    Education_Experience_result=[]
    print("Retrieving Data from Mongo Education_Experience")
    cursor = Education_Experience_collection.find({})
    for document in cursor:
        document.pop("_id")
        Education_Experience_result.append(document)

    #Read the Occupation collection info and pass it to the function 
    Occupation_result=[]
    print("Retrieving Data from Mongo Occupation")
    cursor = Occupation_collection.find({})
    for document in cursor:
        document.pop("_id")
        Occupation_result.append(document)

    #TODO -> Also pass the user_response collection on latest submission
    scored_titles =  predict_score_users.score_user(input_dict['Work Experience Level'], 
                                                    input_dict['Education Level'],
                                                    predicted_title_group, 
                                                    Education_Experience_result, 
                                                    Occupation_result)
    print (scored_titles)
    #STored the result in mondoDB collection
    #result_collection = db.results
    #result_ids = result_collection.insert_many(scored_titles)  #posting.__dict__
    # Give info of inserted IDs
    #print(result_ids.inserted_ids)
    #STep 1: Write this data into a JSON file
    with open('static/Data/results.json', 'w') as resultFileHandle:
        json.dump(scored_titles, resultFileHandle)
    # Step 2: Write inputs shared by user ad prediction into json file 
    # Step 3: return a redirect to results page 
    #return redirect(url_for('result'))
    return jsonify(scored_titles)

@app.route("/Alternate_Titles_User")
def pymongo_Display_Alternate_Titles_For_User():
    Alternate_Titles_result=[]
    print("Retrieving Data from Mongo Alternate_Titles")
    cursor = Alternate_Titles_collection.find({})
    for document in cursor:
        document.pop("_id")
        Alternate_Titles_result.append(document)

    #TODO -> Also pass the user_response collection on latest submission
    user_alt_titles = predict_score_users.show_alternate_titles(Alternate_Titles_result)
    return jsonify(user_alt_titles)

#extra route
@app.route("/result_output")
def results_info():
   DF=pd.read_json("static/Data/results.json")
   DF=DF.T.to_dict().values()

   return jsonify(list(DF))

@app.route("/results_bar_plot")
def results_bar_plot():
    DF=pd.read_json("static/Data/results.json")
    labels=[]
    values=[]
    y_axis=[]
    for index,item in DF.iterrows():
        db_obj=Salary_State_Year_collection.find_one({"Job_Title":item["Title"]})
        labels.append(item["Title"])
        try:
            values.append(db_obj["Salary_2017"])
        except:
            all_obj =Salary_State_Year_collection.find_one({"Job_Title":"All Occupations"})
            values.append(all_obj["Salary_2017"])
            
    # Convert the y axis currency into a integer list
    #for val in values:
    #    y_axis.append(int(val.replace("$","").replace(",","")))
        
    # Create and Sort the dataframe in descending order of salaries
    bar_graph=pd.DataFrame({"x":labels,"y":values})
    bar_graph=bar_graph.sort_values(by=["y"],ascending=False)
    
    # Store the dataframe as dictionary before returning the variable to the route
    labels=bar_graph["x"].tolist()
    values=bar_graph["y"].tolist()
    bar_graph_variable={"x":labels,"y":values}
    
    # Return the bar_graph_variable
    return jsonify(bar_graph_variable)

@app.route("/results_map_plot")
def results_map_plot():
    DF=pd.read_json("static/Data/results.json")
    map_variable={}
    for index,item in DF.iterrows():
        title=item["Title"]
        values=[]
        cursor=Job_State_Salary_collection.find({"Job_Title":item["Title"]})
        for document in cursor:
            doc={"State":document["State"],
                "Salary":document["Salary"].replace("$","").replace(",",""),
                "Title":document["Job_Title"]}
            values.append(doc)
        map_variable[title]=values
    return jsonify(map_variable)

@app.route("/results_line_plot")
def results_line_plot():
    DF=pd.read_json("static/Data/results.json")
    line_variable={}
    titles=[]
    
    x_axis=["2015","2017"]
    for index,item in DF.iterrows():
        y_axis=[]
        db_obj=Salary_State_Year_collection.find_one({"Job_Title":item["Title"]})
        titles.append(item["Title"])
        print(item["Title"])
        try:
            y_axis.append(int(db_obj["Salary_2015"].replace("$","").replace(",","")))
            y_axis.append(int(db_obj["Salary_2017"].replace("$","").replace(",","")))
        except:
            all_obj =Salary_State_Year_collection.find_one({"Job_Title":"All Occupations"})
            y_axis.append(int(all_obj["Salary_2015"].replace("$","").replace(",","")))
            y_axis.append(int(all_obj["Salary_2017"].replace("$","").replace(",","")))
        line_variable[item["Title"]]={"Title":item["Title"],
                                     "x":x_axis,
                                     "y":y_axis}
   
    
    # Return the bar_graph_variable
    return jsonify(line_variable)

# Run the Application
if __name__ == "__main__":
	app.run(debug = True,port=3316) 
