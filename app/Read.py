import rdflib
from rdflib import RDF,Namespace
from rdflib.plugins.sparql import prepareQuery
from geopy.geocoders import Nominatim
from .TaxiStand import TaxiStand
from copy import deepcopy
import geocoder
import math
import time

class Read:
    def __init__(self):
        self.owl_file = "Sample Database.owl"
        self.graph = None
        self.driver = {}
        self.taxiStand = []

    def extractOWl(self):
        self.graph = rdflib.Graph()
        self.graph.parse(self.owl_file)
        q2 = prepareQuery('SELECT ?standLoc WHERE { ?s ?taxiStand ?standLoc .}')
        q3 = prepareQuery('SELECT ?standLoc ?taxiNum ?passengerTime ?peakChance WHERE { ?s ?taxiStandRef ?standLoc. ?s ?taxiStationedRef ?taxiNum. ?s ?passengerRef ?passengerTime. ?s ?peakRef ?peakChance.}')
        driverQuery = prepareQuery('SELECT ?name ?plateNo ?currentLoc WHERE {?road ?linksTo ?driver. ?plate ?linksTo ?driver. ?driver ?driverRef ?name. ?plate ?plateRef ?plateNo. ?road ?roadRef ?currentLoc. }')
        roadRef = rdflib.term.URIRef("http://www.semanticweb.org/ivan/ontologies/2016/7/untitled-ontology-3#Road_Location")
        nameRef = rdflib.term.URIRef("http://www.semanticweb.org/ivan/ontologies/2016/7/untitled-ontology-3#Name")
        plateRef = rdflib.term.URIRef("http://www.semanticweb.org/ivan/ontologies/2016/7/untitled-ontology-3#Car_Plate_Number")
        taxiStandRef = rdflib.term.URIRef("http://www.semanticweb.org/ivan/ontologies/2016/7/untitled-ontology-3#Taxi_Stand_Location")
        taxiNoRef = rdflib.term.URIRef("http://www.semanticweb.org/ivan/ontologies/2016/7/untitled-ontology-3#Number_of_Taxi_Stationed")
        passengerRef = rdflib.term.URIRef("http://www.semanticweb.org/ivan/ontologies/2016/7/untitled-ontology-3#Passenger_Timings")
        peakRef = rdflib.term.URIRef("http://www.semanticweb.org/ivan/ontologies/2016/7/untitled-ontology-3#Chance_Of_Peak")
        sameRef = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#sameAs")
        qres = self.graph.query(driverQuery, initBindings={'linksTo' : sameRef, 'driverRef' : nameRef, 'plateRef' : plateRef, 'roadRef' : roadRef})
        qres2 = self.graph.query(q2, initBindings= {'taxiStand' : taxiStandRef})
        qres3 = self.graph.query(q3, initBindings= {'taxiStandRef' : taxiStandRef, 'taxiStationedRef' : taxiNoRef, 'passengerRef' : passengerRef, 'peakRef' : peakRef})
        # for stand in qres2:
        #     self.taxiStand.append(stand[0].toPython())
        for stand in qres3:
            # self.taxiStand.update({stand[0].toPython(): [stand[1].toPython(), stand[2].toPython()]})
            self.taxiStand.append(TaxiStand(stand[0].toPython(),stand[1].toPython(),stand[2].toPython(),stand[3].toPython()))
        for row in qres:
            self.driver.update({row[1].toPython() : [row[0].toPython(), row[2].toPython()]})

    def findClosestStand(self, startLocation):
        minDist = 10000
        nearestStand = None
        for stand in self.taxiStand:
            distance = self.calculateDistance(startLocation,stand.getStandLoc())
            if distance < minDist:
                minDist = distance
                nearestStand = stand.getStandLoc()
        return nearestStand,minDist

    def performSearch(self, startLocation, checkBox1, checkBox2):
        minDist = 10000
        tmpList = deepcopy(self.taxiStand)
        for stand in tmpList:
            dst = self.calculateDistance(startLocation,stand.getStandLoc())
            if dst is None:
                return None, None
            stand.setDistance(dst)
            stand.scoreFunction(checkBox1,checkBox2)
        tmpList = self.insertion(tmpList)
        top3BestStands = []
        bestStand, tmpList = self.findBestStand(tmpList)
        for i in range(3):
            value, tmpList = self.findBestStand(tmpList)
            top3BestStands.append(value)
        return bestStand, top3BestStands

    def findBestStand(self, list):
        value = max(list,key=lambda p:p.getScore())
        list.remove(value)
        return value, list

    def insertion(self,array):
        if array[0].getDistance() > array[1].getDistance():
            tmp = array[0]
            array[0] = array[1]
            array[1] = tmp
        for mark in range(2, len(array)):
            for i in range(mark):
                if array[i].getDistance() > array[mark].getDistance():
                    tmp = array[i]
                    array[i] = array[mark]
                    array[mark] = tmp
        return array

    def calculateDistance(self,locationA, locationB):
        geoLocationA = geocoder.google(locationA)
        geoLocationB = geocoder.google(locationB)
        if geoLocationA.status == "ZERO_RESULTS" or geoLocationB.status == "ZERO_RESULTS":
            return None
        while geoLocationA.status == "OVER_QUERY_LIMIT":
            time.sleep(5)
            geoLocationA = geocoder.google(locationA)
        while geoLocationB.status == "OVER_QUERY_LIMIT":
            time.sleep(5)
            geoLocationB = geocoder.google(locationB)
        latA,longA = geoLocationA.latlng
        latB,longB = geoLocationB.latlng
        lat_diff = latB - latA
        long_diff = longB - longB
        a = math.pow(math.sin(lat_diff/2),2) + (math.pow(math.sin(long_diff/1),2)*math.cos(latA)*math.cos(latB))
        c = 2*0.0174532925*math.asin(math.sqrt(a))
        radius = 6371
        dist = radius * c
        return dist
