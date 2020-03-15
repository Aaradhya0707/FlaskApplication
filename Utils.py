class Utils:
    @staticmethod
    def calculateDifferencePercent(regularPrice,offerPrice):
        disPercent=(regularPrice-offerPrice)*100/regularPrice
        return disPercent
    
    @staticmethod
    def basicParseForIdList(cursor):
        list=[]
        for doc in cursor:
            list.append(str(doc['_id']))
        return list

    @staticmethod
    def parseCursorForAverageDiscAndCount(cursor,operator,operand2):
        list=[]
        finalDis=0.0
        count=0
        for doc in cursor:
            regularPrice=doc['price']['regular_price']['value']
            offerPrice=doc['price']['offer_price']['value']
            discount=Utils.calculateDifferencePercent(regularPrice,offerPrice)
            if operator =='>':
                if discount > float(operand2):
                    list.append(str(doc['_id']))
                    finalDis+=discount
                    count+=1
            elif operator=='<':
                if discount > float(operand2):
                    list.append(str(doc['_id']))
                    finalDis+=discount
                    count+=1
            elif operator=='==':
                list.append(str(doc['_id']))
                if discount > float(operand2):
                    finalDis+=discount
                    count+=1
        return finalDis/count,count,list

    @staticmethod
    def parseCursorCase4(cursor,operator,operand2,operand12):
        list=[]
        for doc in cursor:
            napBasketPrice=doc['price']['basket_price']['value']
            comBasketPrice=doc['similar_products']['website_results'][str(operand12)]['meta']['avg_price']['basket']
            discount=calculateDifferencePercent(napBasketPrice,comBasketPrice)
            if operator =='>':
                if discount > float(operand2):
                    list.append(str(doc['_id']))
            elif operator=='<':
                if discount > float(operand2):
                    list.append(str(doc['_id']))
            elif operator=='==':
                if discount == float(operand2):
                    list.append(str(doc['_id']))
        print(len(list))
        return list