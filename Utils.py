class Utils:
    #list of all the compeititor's hashes
    BRAND_ID_LIST=['5da94f4e6d97010001f81d72','5da94f270ffeca000172b12e','5d0cc7b68a66a100014acdb0','5da94ef80ffeca000172b12c','5da94e940ffeca000172b12a']
    #method for calculating percacentage as (ar1-ag2)/(arg1)*100
    @staticmethod
    def calculateDifferencePercent(regularPrice,offerPrice):
        disPercent=(regularPrice-offerPrice)*100/regularPrice
        return disPercent
    
    #method to parse cursor for getting ids based on disocunt percentage
    @staticmethod
    def parseCursorForGettingObjectIdCondtions(cursor,operator,operand2):
        set={""}
        set.clear
        finalDis=0.0
        count=0
        for doc in cursor:
            regularPrice=doc['price']['regular_price']['value']
            offerPrice=doc['price']['offer_price']['value']
            discount=Utils.calculateDifferencePercent(regularPrice,offerPrice)
            s=str(discount) + operator + str(operand2)
            if eval(s):
                set.add(str(doc['_id']))
        return set

    #method to parse cursor to a set of object ids
    @staticmethod
    def parseCursorIntoSet(cursor):
        set={""}
        for doc in cursor:
            set.add(str(doc['_id']))
        return set
    
    #method to parse cursor based on comparison with similar products in specific hashes
    @staticmethod
    def paresCursorForGettingIdForAllBrands(cursor):    
        set={""}
        for brand in Utils.BRAND_ID_LIST:
            tempSet=Utils.paresCursorForSpecificBrand(cursor,brand)
            set|=tempSet
        return set

    #comparing with specific hash of web
    @staticmethod
    def paresCursorForSpecificBrand(cursor,brandId):
        set={""}
        for doc in cursor:
            napBasketPrice,comBasketPrice=Utils.getBasketPrices(doc,brandId)
            if napBasketPrice > comBasketPrice:
                set.add(str(doc['_id']))
        # print(len(list))
        return set 

    #parsing ids for brands
    @staticmethod
    def parsingCursorForDiscountCompareForParticularBrandHash(cursor,operator,compareVal):
        set={""}
        for doc in cursor:
            for brandHash in Utils.BRAND_ID_LIST:
                napBasketPrice,comBasketPrice=Utils.getBasketPrices(doc,brandHash)
                disc=Utils.calculateDifferencePercent(napBasketPrice,comBasketPrice)
                s=str(disc)+operator+str(compareVal)
                if eval(s):
                    set.add(str(doc['_id']))
        return set

    
    @staticmethod
    def parseCursorForCompetitorProdId(cursor,brandHash):
        set={""}
        for doc in cursor:
            array=doc['similar_products']['website_results'][str(brandHash)]['knn_items']
            if len(array)>0:
                set.add(str(doc['_id']))
        return set

    #getting basket prices
    @staticmethod
    def getBasketPrices(doc,brandId):
        napBasketPrice=doc['price']['basket_price']['value']
        comBasketPrice=doc['similar_products']['website_results'][str(brandId)]['meta']['avg_price']['basket']
        return napBasketPrice,comBasketPrice

    #merging the sets
    @staticmethod
    def mergeSet(set1,set2):
        if len (set1)!=0 and len(set2)!=0:
            return set1&set2
        else:
            return set1|set2
    