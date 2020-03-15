from flask import Flask 
from flask import request
from flask_pymongo import PyMongo  
import json
from Utils import *
# Flask constructor takes the name of  
# current module (__name__) as argument. 
app = Flask(__name__) 
app.config["MONGO_URI"]="mongodb://localhost:27017/Assignment"
mongo=PyMongo(app)  


@app.route('/average',methods=["GET","POST"])  
def nap_products_with_discount_greater_than_n_percent():
    list=[]
    dict={}
    if request.method=="POST":
        jsonRequest=request.json#returns a dictionary
        queryType=jsonRequest['query_type']
        if queryType=='discounted_products_list':
            listFilter=jsonRequest['filters']# returns a list
            for x in range(len(listFilter)):
                operand1=listFilter[x]['operand1']
                operand2=listFilter[x]['operand2']
                operator=listFilter[x]['operator']
                if operand1 == 'discount':    
                    cursor=mongo.db.Dataset.find({'$where':'this.price.regular_price.value > this.price.offer_price.value'},{'_id':1,'price.regular_price.value':1,'price.offer_price.value':1})
                    a,b,list=Utils.parseCursorForAverageDiscAndCount(cursor,operator,operand2)
                    cursor.close
                if operand1=='brand.name' and operator=='==':
                    cursor=mongo.db.Dataset.find({operand1:operand2})
                    for doc in cursor:
                        regularPrice=doc['price']['regular_price']['value']
                        offerPrice=doc['price']['offer_price']['value']
                        if offerPrice<regularPrice:
                            list.append(str(doc['_id']))
                    cursor.close
            dict['discounted_products_list']=list
            return(str(dict))
        if queryType=='discounted_products_count|avg_discount':
            count=0
            totalDiscount=0.0
            listFilter=jsonRequest['filters']# returns a list
            for x in range(len(listFilter)):
                operand1=listFilter[x]['operand1']
                operand2=listFilter[x]['operand2']
                operator=listFilter[x]['operator']
                if operand1 == 'discount':    
                    cursor=mongo.db.Dataset.find({'$where':'this.price.regular_price.value > this.price.offer_price.value'},{'_id':1,'price.regular_price.value':1,'price.offer_price.value':1})
                    totalDiscount,count,list=parseCursorForAverageDiscAndCount(cursor,operator,operand2)
                    cursor.close
                if operand1=='brand.name' and operator=='==':
                    cursor=mongo.db.Dataset.find({operand1:operand2})
                    for doc in cursor:
                        regularPrice=doc['price']['regular_price']['value']
                        offerPrice=doc['price']['offer_price']['value']
                        if offerPrice<regularPrice:
                            count+=1
                            totalDiscount+=calculateDifferencePercent(regularPrice,offerPrice)
                    if count>0:
                        totalDiscount=totalDiscount/float(count)
                    cursor.close
            dict['discounted_products_count']=count
            dict['avg_dicount']=totalDiscount
            return (str(dict))
        if queryType=='expensive_list':
            if 'filters' in jsonRequest:
                listFilter=jsonRequest['filters']# returns a list
                for x in range(len(listFilter)):
                    operand1=listFilter[x]['operand1']
                    operand2=listFilter[x]['operand2']
                    operator=listFilter[x]['operator']
                    if operand1=='brand.name' and operator=='==':
                        cursor=mongo.db.Dataset.find({'$where':'this.price.basket_price.value > this.similar_products.meta.avg_price.basket','brand.name':operand2},{'_id':1,'price.regular_price.value':1,'price.offer_price.value':1})
                        list=basicParseForIdList(cursor)
                        cursor.close
            else:
                cursor=mongo.db.Dataset.find({'$where':'this.price.basket_price.value > this.similar_products.meta.avg_price.basket'},{'_id':1})
                list=basicParseForIdList(cursor)
                cursor.close
            dict={}
            dict['expensive_list']=list
            return str(dict)
        if queryType=='competition_discount_diff_list':
            if 'filters' in jsonRequest:
                if len(jsonRequest['filters']) == 2:
                    listFilter=jsonRequest['filters']# returns a list
                    operand01=listFilter[0]['operand1']
                    operand02=listFilter[0]['operand2']
                    operator0=listFilter[0]['operator']
                    operand11=listFilter[1]['operand1']
                    operand12=listFilter[1]['operand2']
                    operator1=listFilter[1]['operator']
                    if operand01=='discount_diff' and operand11=='competition' and operator1 == '==':
                        cursor=mongo. db.Dataset.find()
                        list=parseCursorCase4(cursor,operator0,operand02,operand12)
                dict['competition_discount_diff_list']=list
            return str(dict)

# main driver function 
if __name__ == '__main__': 
  
    # run() method of Flask class runs the application  
    # on the local development server. 
    app.run(host='0.0.0.0',port=6060) 
