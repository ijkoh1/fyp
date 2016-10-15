import math
import datetime
class TaxiStand:
    def __init__(self, standLoc, taxiNum, passengerTime, chanceOfPeak):
        self.standLoc = standLoc
        self.taxiNum = taxiNum
        self.passengerTime = passengerTime
        self.dist = None
        self.score = None
        self.peakChance = chanceOfPeak

    def getStandLoc(self):
        return self.standLoc

    def getTaxiNum(self):
        return self.taxiNum

    def getPassengerTime(self):
        return self.passengerTime

    def setDistance(self,distance):
        self.dist = distance

    def getDistance(self):
        return self.dist

    def getScore(self):
        return self.score

    def getPeakChance(self):
        return self.peakChance

    def scoreFunction(self, check1, check2):
        self.score = (self.dist*-2)
        if check1:
            self.score += (self.taxiNum*-1)
        elif check2:
            self.score += (1.5*self.peakChance)
            currentHour = datetime.datetime.now().hour
            if self.withinPassengerTiming(currentHour,self.passengerTime):
                self.score *= 1.2
        if check1 and check2:
            self.score = math.log(self.score)

    def withinPassengerTiming(self,hour,preferedTime):
        if hour >= 0 and hour < 12 and preferedTime == "Morning":
            return True
        elif hour >= 12 and hour < 18 and preferedTime == "Afternoon":
            return True
        elif hour >= 18 and hour < 20 and preferedTime == "Evening":
            return True
        elif hour >= 20 and hour < 0 and preferedTime == "Night":
            return True
        return False
