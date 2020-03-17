from flask import Flask 
from flask import request
from flask_pymongo import PyMongo  
import json
from Utils import *
from bson.objectid import ObjectId
# Flask constructor takes the name of  
# current module (__name__) as argument. 
app = Flask(__name__) 
app.config["MONGO_URI"]="mongodb://localhost:27017/Assignment"
mongo=PyMongo(app)  

#defining end point for the api
@app.route('/',methods=["POST"])  
def nap_products_with_discount_greater_than_n_percent():
    #creating list for the required query
    listProds=[] 
    brand_set={""}
    brand_set.remove("")
    disc_set={""}
    disc_set.remove("")
    # creating dict for the output
    dict={}
    #checking the request type
    if request.method=="POST":
        jsonRequest=request.json#returns a dictionary
        if 'query_type' in jsonRequest:
            #fetching the request dictionary
            queryType=jsonRequest['query_type']
            #checking for request type discounted products list 
            if queryType=='discounted_products_list':
                set={""}
                listFilter=jsonRequest['filters']# returns a list
                #running all the scenarios
                for x in range(len(listFilter)):
                    #fetching the conditons
                    operand1=listFilter[x]['operand1']
                    operand2=listFilter[x]['operand2']
                    operator=listFilter[x]['operator']
                    #selecting the case to be used
                    if operand1 == 'discount':    
                        #getting the cursor to fetch the dicounted products,i.e., regular price > offer price and getting only the required fields
                        cursor=mongo.db.Dataset.find({'$where':'this.price.regular_price.value > this.price.offer_price.value'},{'_id':1,'price.regular_price.value':1,'price.offer_price.value':1})
                        #function call to parse and getting the required things
                        tempSet=Utils.parseCursorForGettingObjectIdCondtions(cursor,operator,operand2)
                        brand_set|=tempSet
                        #closing the cursor
                        cursor.close
                    #checking if the second filter is used 
                    elif operand1=='brand.name' and operator=='==':
                        #quering the database to find the brand.name == operand2
                        cursor=mongo.db.Dataset.find({'$where':'this.price.regular_price.value > this.price.offer_price.value',operand1:operand2},{'_id':1,'price.regular_price.value':1,'price.offer_price.value':1})
                        disc_set|=Utils.parseCursorIntoSet(cursor)
                        
                        #closing the cursor
                        cursor.close
                #applying the results to the dictionary and breaking the flow of the program in such a manner that even if any wrong query is fired then the output will be empty set
                set=Utils.mergeSet(brand_set,disc_set)
                set.remove('')
                dict['discounted_products_list']=list(set)
                print(len(set))
                return(str(dict))
            if queryType=='discounted_products_count|avg_discount':
                set={""}
                dict
                #creating variables for the count and discount
                count=0
                totalDiscount=0.0
                listFilter=jsonRequest['filters']
                for x in range(len(listFilter)):
                    operand1=listFilter[x]['operand1']
                    operand2=listFilter[x]['operand2']
                    operator=listFilter[x]['operator']
                    if operand1 == 'discount':   
                        #searching where regular price > offer price  
                        cursor=mongo.db.Dataset.find({'$where':'this.price.regular_price.value > this.price.offer_price.value'},{'_id':1,'price.regular_price.value':1,'price.offer_price.value':1})
                        #getting the ids of all the products required according to opperand supplied
                        disc_set|=Utils.parseCursorForGettingObjectIdCondtions(cursor,operator,operand2)
                        #closing the cursor
                        cursor.close
                    if operand1=='brand.name' and operator=='==':
                        #searching where regular price > offer price and brand.name= operand 2
                        cursor=mongo.db.Dataset.find({'$where':'this.price.regular_price.value > this.price.offer_price.value',operand1:operand2},{'_id':1,'price.regular_price.value':1,'price.offer_price.value':1})
                        #getting the ids in a set 
                        brand_set|=Utils.parseCursorIntoSet(cursor)
                        #closing the cursor
                        cursor.close
                #and operation on the set
                set=Utils.mergeSet(disc_set,brand_set)
                if "" in set:
                    set.remove("")
                #iterating for all the ids in the set and calculating discount
                for id in set:
                    #finding data using id
                    cursor=mongo.db.Dataset.find({'_id':ObjectId(id)})
                    for doc in cursor:
                        regularPrice=doc['price']['regular_price']['value']
                        offerPrice=doc['price']['offer_price']['value']
                        totalDiscount+=Utils.calculateDifferencePercent(regularPrice,offerPrice)
                        print(totalDiscount)
                    cursor.close
                count=len(set)
                #case where no ids are found
                if count>0:
                    print(totalDiscount)
                    totalDiscount=totalDiscount/float(count)
                #setting the values
                dict['discounted_products_count']=len(set)
                dict['avg_dicount']=totalDiscount
                return (str(dict))
            if queryType=='expensive_list':
                set={""}
                if 'filters' in jsonRequest:
                    listFilter=jsonRequest['filters']# returns a list
                    #iterating
                    for x in range(len(listFilter)):
                        operand1=listFilter[x]['operand1']
                        operand2=listFilter[x]['operand2']
                        operator=listFilter[x]['operator']
                        if operand1=='brand.name' and operator=='==':
                            #finding docs with brand.name == operand2 
                            cursor=mongo.db.Dataset.find({operand1:operand2})
                            #finding the ids of products where basket_price > similar_product's basket prices
                            set|=Utils.paresCursorForGettingIdForAllBrands(cursor)
                            cursor.close
                else:
                    #finding all the ids of the products 
                    cursor=mongo.db.Dataset.find({'$where':'/^/'})
                    #finding the ids of products where basket_price > similar_product's basket prices for all the products
                    set|=Utils.paresCursorForGettingIdForAllBrands(cursor)
                    cursor.close
                if "" in set:
                    set.remove("")
                #setting the data and sending it
                dict['expensive_list']=list(set)
                print(len(list(set)))
                return str(dict)
            if queryType=='competition_discount_diff_list':
                set={""}
                length=len(jsonRequest['filters'])
                listFilter=jsonRequest['filters']# returns a list
                #running all the scenarios
                for x in range(len(listFilter)):
                    operand1=listFilter[x]['operand1']
                    operand2=listFilter[x]['operand2']
                    operator=listFilter[x]['operator']
                    if operand1=='discount_diff':
                        cursor=mongo.db.Dataset.find()
                        #querying according to the discount according to operator and operand2
                        disc_set|=Utils.parsingCursorForDiscountCompareForParticularBrandHash(cursor,operator,operand2)
                        cursor.close
                    if operand1=='competition' and operator=='==':
                        #querying according to discount for a particular brand hash 
                        cursor=mongo.db.Dataset.find({'$where':'/^/'},{'similar_products.website_results.'+str(operand2)+'.knn_items':1,'_id':1})
                        brand_set|=Utils.parseCursorForCompetitorProdId(cursor,operand2)
                        cursor.close
                #and the results for particular brands
                set=Utils.mergeSet(brand_set,disc_set)
                if "" in set:
                    set.remove("")
                # setting the results
                dict['competition_discount_diff_list']=list(set)
                return str(dict)

# main driver function 
if __name__ == '__main__': 
  
    # run() method of Flask class runs the application  
    # on the local development server. 
    app.run(host='0.0.0.0',port=6060) 
