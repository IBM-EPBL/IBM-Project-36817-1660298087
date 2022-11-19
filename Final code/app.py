
import json
from multiprocessing import connection

import ibm_db
from flask import Flask, redirect, render_template, request, session, url_for

try: 
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=8e359033-a1c9-4643-82ef-8ac06f5107eb.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30120;PROTOCOL=TCPIP;UID=myd98326;PWD=NVpgKVAQaX0VFkGd;SECURITY=SSL;", '', '')
    print(ibm_db.active(conn))
    print("Successfully  connected with database")
except:
    print("Database not connected : ", ibm_db.conn_errormsg())





app = Flask(__name__)

app.secret_key = 'r'


@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signin")
def signin():
    return render_template("login.html")




@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
  
    
    sql = "SELECT * FROM register WHERE email = ?" 
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
        return render_template('login.html', msg="You are already a member, please login using your details")
    else:
        insert_sql = "INSERT INTO register VALUES (?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, password)
        ibm_db.execute(prep_stmt)
        return render_template('login.html', msg="You are Successfully Registered with IMS, please login using your details")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    sql = "SELECT * FROM register WHERE email = ?" 
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if not account:
        return render_template('signup.html', msg="You are not yet registered, please sign up using your details")
    else:
         if(password == account['PASSWORD']):
            userid = account['EMAIL']
            
            session['userid'] = userid
            return redirect("/home")
         else:
            return render_template('login.html', msg="Please enter the correct password")


 
        
@app.route("/add")
def adding():
    return render_template('add.html')



@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    print("Entering add expense")
    
    if request.method == 'POST':
        date = request.form.get('date')
        expensename = request.form.get('expensename')
        amount = request.form.get('amount')
        paymode = request.form.get('paymode')
        category = request.form.get('category')
        email = session['userid']

        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(email)
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")


        insert_sql = "INSERT INTO ADDEXPENSE VALUES (?,?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)

        print("=====================================")
        
        ibm_db.bind_param(prep_stmt, 1, date)
        ibm_db.bind_param(prep_stmt, 2, expensename)
        ibm_db.bind_param(prep_stmt, 3, amount)
        ibm_db.bind_param(prep_stmt, 4, paymode)
        ibm_db.bind_param(prep_stmt, 5, category)
        ibm_db.bind_param(prep_stmt, 6, email)


        ibm_db.execute(prep_stmt)
        print("=====================================")
        print("Successfully inserted")
        # print(date + " " + expensename + " " + amount + " " + paymode + " " + category)
        
        return redirect('/display')



@app.route("/display")
def display():

    print("============================")
    expense = []
    print(expense)
    sql = "SELECT * FROM ADDEXPENSE where email=?"
    prep_stmt = ibm_db.prepare(conn, sql)
    print("USER ID = ", session['userid'])
    ibm_db.bind_param(prep_stmt, 1, session['userid'])
    ibm_db.execute(prep_stmt)
    dictionary = ibm_db.fetch_both(prep_stmt)
    print("--------------dictionary----------")
    # print(dictionary)
    print("-------------------------")
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0
    total = 0
    incomeamount = 0
    while dictionary != False:
        print("__varutha___")
        expense.append(dictionary)
        print(dictionary)
        category = str(dictionary['CATEGORY']).strip()
        if(category == 'food'):
            t_food = int(dictionary['AMOUNT']) + t_food
        if(category == 'entertainment'):
            t_entertainment = int(dictionary['AMOUNT'])+ t_entertainment
        if(category == 'business'):
            t_business = int(dictionary['AMOUNT'])+ t_business
        if(category == 'rent'):
            t_rent = int(dictionary['AMOUNT'])+ t_rent
        if(category == 'EMI'):
            t_EMI = int(dictionary['AMOUNT'])+ t_EMI
        if(category == 'other'):
            t_other = int(dictionary['AMOUNT'])+ t_other

        
        dictionary = ibm_db.fetch_both(prep_stmt)

    total = t_food + t_entertainment + t_business + t_EMI + t_rent + t_other
    print(expense) 
    if expense:
        print("IF")
        return render_template("display.html", expense = json.dumps(expense,default=str),expenselist=expense, t_food = t_food,  t_entertainment=t_entertainment, t_business=t_business,t_rent=t_rent,t_EMI=t_EMI,t_other=t_other, total=total)
        # return render_template("display.html", expense = expense, expenselist=expense)
    else:
        print("ELSE")
        return render_template("display.html", expense = [])



@app.route('/delete/<expensename>', methods = ['POST', 'GET' ])
def delete(expensename):
    print("-----------")
    print(expensename)
    sql = "SELECT * FROM ADDEXPENSE WHERE expensename = ?"
    print(sql)
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, expensename)
    ibm_db.execute(stmt)
   
    expenses = ibm_db.fetch_row(stmt)
    print ("The Name is : ", expenses)
    if expenses:
        print("*****************************88")
        sql = f"DELETE FROM ADDEXPENSE WHERE expensename= ?"
        print(sql)
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, expensename)
        ibm_db.execute(stmt)
        return redirect('/display')
       

@app.route("/limit")
def limit():
    return render_template("limit.html")

@app.route("/limitnum",methods=['POST'])
def limitnum():
    if request.method == "POST":
        number = request.form.get('number')

        insert_sql = "INSERT INTO limits VALUES (?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)

        print("=====================================")
        
        ibm_db.bind_param(prep_stmt, 1, number)
        ibm_db.execute(prep_stmt)
        print("=====================================")
        print("Successfully inserted")
        return redirect('/limit')

@app.route("/today")
def today():
    return render_template("today.html")


@app.route("/month")
def month():
    return render_template("month.html")


@app.route("/year")
def year():
    return render_template("year.html")



"""

@app.route("/updatebalance", methods=["POST"])
def update():
    incomeamount = request.form.get("incomeamount")
    # incomeamount= data['incomeamount']
    sql = "UPDATE ADDEXPENSE SET incomeamount = ? WHERE email = ?"
    prep_stmt = ibm_db.prepare(conn, sql)
    print("USER ID = ", session['userid'])
    ibm_db.bind_param(prep_stmt, 1, incomeamount)
    ibm_db.bind_param(prep_stmt, 2, session['userid'])
     
    ibm_db.execute(prep_stmt)
    return redirect(url_for('display'))
    

@app.route("/updatebalance")
def update():
    incomeamount=data['incomeamount']
    return render_template("display.html")


@app.route("/limit" )
def limit():
       return redirect('/limitn')

@app.route("/limitnum" , methods = ['POST'])
def limitnum():
     if request.method == "POST":
         number= request.form['number']
       

         sql = "INSERT INTO limits VALUES (?,?)"
         stmt = ibm_db.prepare(conn, sql)
         ibm_db.bind_param(stmt, 1, session['userid'])
         ibm_db.bind_param(stmt, 2, number)
         ibm_db.execute(stmt)
         
         return redirect('/limitn')
     
         
@app.route("/limitn") 
def limitn():
    
    sql = "SELECT * FROM limits WHERE email = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session['userid'])
    dictionary = ibm_db.execute(stmt)

    # print("==========================")
    # print(res)
    # limit = ibm_db.fetch_both(stmt)
    # print(limit)
    # # s = limit[0]
    row = []
    # s = "/-"
    s = ""
    while dictionary != False:

        temp = []
        temp.append(dictionary["LIMIT"])
        print(temp)
        row.append(temp)
        dictionary = ibm_db.fetch_assoc(stmt)
        s = temp[len(temp)-1]
    print("----s-----")  
    print(s)
    return render_template("limit.html" , y= s)

#REPORT

@app.route("/today")
def today():
    

      param1 = "SELECT TIME(date) as tn, amount FROM ADDEXPENSE WHERE userid = " + str(session['userid']) + " AND DATE(date) = DATE(current timestamp) ORDER BY date DESC"
      res1 = ibm_db.exec_immediate(conn, param1)
      dictionary1 = ibm_db.fetch_assoc(res1)
      texpense = []

      while dictionary1 != False:
          temp = []
          temp.append(dictionary1["TN"])
          temp.append(dictionary1["AMOUNT"])
          texpense.append(temp)
          print(temp)
          dictionary1 = ibm_db.fetch_assoc(res1)
      
 

      param = "SELECT * FROM ADDEXPENSE WHERE userid = " + str(session['userid']) + " AND DATE(date) = DATE(current timestamp) ORDER BY date DESC"
      res = ibm_db.exec_immediate(conn, param)
      dictionary = ibm_db.fetch_assoc(res)
      expense = []
      while dictionary != False:
          temp = []
        #   temp.append(dictionary["ID"])
          temp.append(dictionary["USERID"])
          temp.append(dictionary["DATE"])
          temp.append(dictionary["EXPENSENAME"])
          temp.append(dictionary["AMOUNT"])
          temp.append(dictionary["PAYMODE"])
          temp.append(dictionary["CATEGORY"])
          expense.append(temp)
          print(temp)
          dictionary = ibm_db.fetch_assoc(res)

  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += int(x[3])
          if x[5] == "food":
              t_food += int(x[3])
            
          elif x[5] == "entertainment":
              t_entertainment  += int(x[3])
        
          elif x[5] == "business":
              t_business  += int(x[3])
          elif x[5] == "rent":
              t_rent  += int(x[3])
           
          elif x[5] == "EMI":
              t_EMI  += int(x[3])
         
          elif x[5] == "other":
              t_other  += int(x[3])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
     

@app.route("/month")
def month():
  

      param1 = "SELECT DATE(date) as dt, SUM(amount) as tot FROM ADDEXPENSE WHERE userid = " + str(session['userid']) + " AND MONTH(date) = MONTH(current timestamp) AND YEAR(date) = YEAR(current timestamp) GROUP BY DATE(date) ORDER BY DATE(date)"
      res1 = ibm_db.exec_immediate(conn, param1)
      dictionary1 = ibm_db.fetch_assoc(res1)
      texpense = []

      while dictionary1 != False:
          temp = []
          temp.append(dictionary1["DT"])
          temp.append(dictionary1["TOT"])
          texpense.append(temp)
          print(temp)
          dictionary1 = ibm_db.fetch_assoc(res1)
    

      param = "SELECT * FROM ADDEXPENSE WHERE userid = " + str(session['userid']) + " AND MONTH(date) = MONTH(current timestamp) AND YEAR(date) = YEAR(current timestamp) ORDER BY date DESC"
      res = ibm_db.exec_immediate(conn, param)
      dictionary = ibm_db.fetch_assoc(res)
      expense = []
      while dictionary != False:
          temp = []
        #   temp.append(dictionary["ID"])
          temp.append(dictionary["USERID"])
          temp.append(dictionary["DATE"])
          temp.append(dictionary["EXPENSENAME"])
          temp.append(dictionary["AMOUNT"])
          temp.append(dictionary["PAYMODE"])
          temp.append(dictionary["CATEGORY"])
          expense.append(temp)
          print(temp)
          dictionary = ibm_db.fetch_assoc(res)

  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += int(x[3])
          if x[5] == "food":
              t_food += int(x[3])
            
          elif x[5] == "entertainment":
              t_entertainment  += int(x[3])
        
          elif x[5] == "business":
              t_business  += int(x[3])
          elif x[5] == "rent":
              t_rent  += int(x[3])
           
          elif x[5] == "EMI":
              t_EMI  += int(x[3])
         
          elif x[5] == "other":
              t_other  += int(x[3])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         
@app.route("/year")
def year():
   

      param1 = "SELECT MONTH(date) as mn, SUM(amount) as tot FROM ADDEXPENSE WHERE userid = " + str(session['userid']) + " AND YEAR(date) = YEAR(current timestamp) GROUP BY MONTH(date) ORDER BY MONTH(date)"
      res1 = ibm_db.exec_immediate(conn, param1)
      dictionary1 = ibm_db.fetch_assoc(res1)
      texpense = []

      while dictionary1 != False:
          temp = []
          temp.append(dictionary1["MN"])
          temp.append(dictionary1["TOT"])
          texpense.append(temp)
          print(temp)
          dictionary1 = ibm_db.fetch_assoc(res1)

      param = "SELECT * FROM ADDEXPENSE where userid = " + str(session['userid']) + " AND YEAR(date) = YEAR(current timestamp) ORDER BY date DESC"
      res = ibm_db.exec_immediate(conn, param)
      dictionary = ibm_db.fetch_assoc(res)
      expense = []
      while dictionary != False:
          temp = []
        #   temp.append(dictionary["ID"])
          temp.append(dictionary["USERID"])
          temp.append(dictionary["DATE"])
          temp.append(dictionary["EXPENSENAME"])
          temp.append(dictionary["AMOUNT"])
          temp.append(dictionary["PAYMODE"])
          temp.append(dictionary["CATEGORY"])
          expense.append(temp)
          print(temp)
          dictionary = ibm_db.fetch_assoc(res)

  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += int(x[3])
          if x[5] == "food":
              t_food += int(x[3])
            
          elif x[5] == "entertainment":
              t_entertainment  += int(x[3])
        
          elif x[5] == "business":
              t_business  += int(x[3])
          elif x[5] == "rent":
              t_rent  += int(x[3])
           
          elif x[5] == "EMI":
              t_EMI  += int(x[3])
         
          elif x[5] == "other":
              t_other  += int(x[3])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )



"""


@app.route('/logout')
def logout():

   session.pop('password',None)
   session.pop('userid', None)
   return render_template('home.html')

    
if __name__== "__main__":
    app.run(host='0.0.0.0',port=5000)