#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import subprocess as sub
import os
from math import *

#
##      DEFINE
#

INDICE_SIZE = 10
SDCOEF = 1.5
COEF_UNDER_SELL = 0.2
COEF_LOOSE_MAX = 0.1
MAX_TO_INV = 0.8
MAX_TO_INV_BOLL = 0.4
marketplace_list = ["crypto", "raw_material", "stock_exchange", "forex"]
MAX_CURR = 200
VAR_COEF = 1.2

#
##      MAIN VARIABLES
#

CURR = [[], [], [], []]
#moneyaction#MACT = CASH, NBR CRPT, NBR RWMT, NBR FOREX, NBR STCK
MACT = [10000, 0, 0, 0, 0]
#BUYVALUE = BUY VALUE OF ACUTEL CRPT, RWMT, FOREX, STCK
BUYVALUE = [0, 0, 0, 0]
#MAXVALUE = MAX VALUE OF ACUTEL CRPT, RWMT, FOREX, STCK
MAXVALUE = [0, 0, 0, 0]
#BU = ARRAY WITH BU of CRPT, RWMT, FOREX, STCK
BU = [[], [], [], []]
BL = [[], [], [], []]
PRINTBOOL = False

########################################################################################################
##      @param: GetValue
##      @def: thxRoro
##      @brief: get the Value from the MARKET my bro
##      @return: value of the last occurence in a marketplace
########################################################################################################

def GetValue(marketplace):
    path = "../push_index/.index.db"
    try:
        os.mkfifo(path)
    except OSError:
        pass
    
    my_value = -1
    fifo = open(path, "r")
    
    for line in fifo:
        if (line.split(':')[0] == marketplace):
            my_value = float(line.split(':')[1])
            break
    fifo.close()
    return my_value

########################################################################################################
##      @param: command to write, the value if it get one otherwise -1, the market
##      @def: write_cmd
##      @brief: write the command
##      @return: /
########################################################################################################

def write_cmd(cmd, value, market):
    if value == -1:
        if (cmd == "STATS" or cmd == "HELP" or cmd == "EXIT"):
            sys.stdout.write(cmd)
            sys.stdout.write("\n")
            sys.stdout.flush()
        return ;
    if (cmd == "BUY" or cmd == "SELL"):
        if (value == 0):
            return ;
        sys.stdout.write(cmd)
        sys.stdout.write(":")
        sys.stdout.write(str(value))
        sys.stdout.write(":")
        sys.stdout.write(str(market))
        sys.stdout.write("\n")
        sys.stdout.flush()

########################################################################################################
##      @param: 
##      @def: main
##      @brief: call the algorythm fct. Got the datas with all the indexes data per monney.
##      MACT = MONEY + ACTION IN A TAB
##      @return: 0
########################################################################################################

def     calc_band_bollinger(MA, SD):
    BUP = float(MA) + (float(SD) * float(SDCOEF))
    BLP = float(MA) - (float(SD) * float(SDCOEF))
    return BUP, BLP

########################################################################################################
##      @param:  /
##      @def:   calc_band bollinger for each courb
##      @brief: 
##      @return: /
########################################################################################################

def standard_deviation(floatlist, MA):
    lt = floatlist[-10:]
    summ = 0
    for j in lt:
        summ = summ + ((j - MA) * (j - MA))
    total = summ / len(lt)
    total = sqrt(total)
    return (total)

########################################################################################################
##      @param:  /
##      @def:   moving_average_on_period
##      @brief: compute moving average on a given period
##      @return: /
########################################################################################################

def     moving_average_on_period(floatlist):
    lt = floatlist[-10:]
    summ = 0
    for i in lt:
        summ = summ + float(i)
    total = summ / len(lt)
    return (total)

########################################################################################################
##      @param:  /
##      @def:   calc_bollinger
##      @brief:  calc band bollinger band
##      @return: /
########################################################################################################

def calc_bollinger(floatlist, PERIOD):
    MA = moving_average_on_period(floatlist)
    SD = standard_deviation(floatlist, MA)
    BUP, BLO = calc_band_bollinger(MA, SD)
    return BUP, BLO

########################################################################################################
##      @param:  /
##      @def:   calc_band
##      @brief: compute bollinger band for each curve
##      @return: /
########################################################################################################

def calc_band():
    i = 0
    while (i < 4):
        BUP, BLO = calc_bollinger(CURR[i], INDICE_SIZE)
        BU[i].append(BUP)
        BL[i].append(BLO)
        i = i + 1

########################################################################################################
##      @param:  /
##      @def:   valcVarCoef
##      @brief: calc coef variation > 1 ca monte < 1 ca descend et plus
##      c'est plus grand que un c'est que ca monte bcp
##      @return: /
########################################################################################################

def VarCoef(tab):
    zone = tab[-5:]
    summ = 0
    for i in zone:
        summ = summ + i
    total = summ / len(zone)
    coefvar = tab[-1] / total
    return coefvar;

########################################################################################################
##      @param:  /
##      @def:   valcVarCoef
##      @brief: calc coef of variation periodic
##      @return: /
########################################################################################################

def valcVarCoef():
    lt = []
    ji = 0
    while (ji < 4):
        lt.append(VarCoef(CURR[ji]))
        ji = ji + 1
    return lt


########################################################################################################
##      @param:  sellCrypto
##      @def:   sell the crypto
##      @brief: Sell the currencies
##      @return: /
########################################################################################################
#essayer en la vendant si elle descend de 5% ou moins
def sellCrypto():
    if (CURR[0][-1] > BUYVALUE[0] * 1.05):
        if (CURR[0][-1] < CURR[0][-2]):# and CURR[0][-3] > CURR[0][-2]):
            write_cmd("SELL", MACT[1], marketplace_list[0])
            MACT[0] = MACT[0] + MACT[1] * CURR[0][-1]
            MACT[1] = 0
            BUYVALUE[0] = 0
            MAXVALUE[0] = 0
                                                                            
########################################################################################################
##      @param:  sellCurrencies
##      @def:   sell the currencies
##      @brief: Sell the currencies
##      @return: /
########################################################################################################
    
def sellCurrencies():
    j = 1
    sellCrypto();
    while (j < 4):
        #Si l'action baisse de 5 pourcent
        if (MACT[j + 1] > 0):
            if (CURR[j][-1] < BUYVALUE[j] * (1 - COEF_UNDER_SELL)):
                write_cmd("SELL", MACT[j + 1], marketplace_list[j])
                MACT[0] = MACT[0] + MACT[j + 1] * CURR[j][-1]
                MACT[j + 1] = 0
                BUYVALUE[j] = 0
                MAXVALUE[j] = 0
                 #si l'action baisse de 5 pourcent par rapport a son pic
            elif (CURR[j][-1] < (MAXVALUE[j] * (1 - COEF_LOOSE_MAX))):
                write_cmd("SELL", MACT[j + 1], marketplace_list[j])
                MACT[0] = MACT[0] + MACT[j + 1] * CURR[j][-1]
                MACT[j + 1] = 0
                BUYVALUE[j] = 0
                MAXVALUE[j] = 0
        j = j + 1

########################################################################################################
##      @param:  setpic
##      @def:   set the spike of the currency in stock
##      @brief: function who set the spike
##      @return: /
########################################################################################################
        
def setpic():
    j = 0
    while (j < 4):
        #Si l'action baisse de 5 pourcent
        if (MAXVALUE[j] > 0 and MAXVALUE[j] < CURR[j][-1]):
            MAXVALUE[j] = CURR[j][-1]
        j = j + 1

########################################################################################################
##      @param:  VARCOEF
##      @def:   buy curriences
##      @brief: function who buy currencies
##      @return: 0
########################################################################################################
        
def bandeSeResserent(BandU, BandL):
    lt = []
    ltprov1 = BandU[-10:]
    ltprov2 = BandL[-10:]
    if (len(ltprov1) != len(ltprov2)):
        return False;
    i = 0
    while (i < len(ltprov1)):
        lt.append(ltprov1[i] - ltprov2[i])
        i = i + 1;
    if (len(lt) != 10):
        return False;
    summ = 0
    for j in lt :
        summ = summ + j
    summ = summ / len(lt)
    if (lt[-1] < summ):
        return True
    return False

########################################################################################################
##      @param:  i got the Monney
##      @def:   check if i got the money for 1 crypto DUDE
##      @brief: function who buy currencies
##      @return: 0
########################################################################################################

def sellAll():
    if (MACT[0] >= CURR[0][-1]):
        return
    i = 1
    while (i < 4):
        if (MACT[i + 1] > 0):
            write_cmd("SELL", MACT[i + 1], marketplace_list[i])
            MACT[0] = MACT[0] + MACT[i + 1] * CURR[i][-1]
            MACT[i + 1] = 0
            BUYVALUE[i] = 0
            MAXVALUE[i] = 0
        i = i + 1

########################################################################################################
##      @param:  VARCOEF
##      @def:   buy curriences
##      @brief: function who buy currencies
##      @return: 0
########################################################################################################

def iGotTheMonneyInCurrencies():
    SUMM = MACT[0]
    i = 1
    while (i < 4):
        if (MACT[i + 1] > 0):
            SUMM = SUMM + MACT[i + 1] * CURR[i][-1]
        i = i + 1
    if SUMM >= CURR[0][-1]:
        return True
    return False

########################################################################################################
##      @param:  VARCOEF
##      @def:   buy curriences
##      @brief: function who buy currencies
##      @return: 0
########################################################################################################

def buyCrypto():
    if (MACT[1] > 0):
        return
    MOY = 0
    SUMM = 0
    lt = CURR[0][-10:]
    for i in lt:
        SUMM = SUMM + i
    MOY = SUMM / len(lt)
    if (iGotTheMonneyInCurrencies() == True and CURR[0][-1] < MOY):
        sellAll()
        nbrCurr = int(MACT[0] / CURR[0][-1])
        if (nbrCurr * CURR[0][-1] <= MACT[0]):
            write_cmd("BUY", nbrCurr, marketplace_list[0])
            MACT[0] = MACT[0] - nbrCurr * CURR[0][-1]
            MACT[1] = nbrCurr
            BUYVALUE[0] = CURR[0][-1]
            MAXVALUE[0] = CURR[0][-1]

########################################################################################################
##      @param:  VARCOEF
##      @def:   buy curriences
##      @brief: function who buy currencies
##      @return: 0
########################################################################################################

def buyCurrencies(VARCOEF):
    buyCrypto()
    if (MACT[0] > 0):
        j = 0
        while (j < 4):
            BOL = True
            if (VARCOEF[j] > VAR_COEF and MACT[j + 1] == 0):
                #Max 90 % de la somme à cette ligne
                nbrCurr = int((MACT[0] * MAX_TO_INV) / CURR[j][-1])
                if (nbrCurr > MAX_CURR):
                    nbrCurr = MAX_CURR
                if (nbrCurr * CURR[j][-1] < MACT[0]):
                    write_cmd("BUY", nbrCurr, marketplace_list[j])
                    MACT[0] = MACT[0] - nbrCurr * CURR[j][-1]
                    MACT[j + 1] = nbrCurr
                    BUYVALUE[j] = CURR[j][-1]
                    MAXVALUE[j] = CURR[j][-1]
                    BOL = False
            if (len(BU[j]) >= 10 and len(BL[j]) >= 10 and BOL == True):
                if (bandeSeResserent(BU[j], BL[j]) == True and MACT[j + 1] == 0):
                    nbrCurr = int((MACT[0] * MAX_TO_INV_BOLL) / CURR[j][-1])
                    if (nbrCurr > MAX_CURR):
                        nbrCurr = MAX_CURR
                    if (nbrCurr * CURR[j][-1] < MACT[0]):
                        write_cmd("BUY", nbrCurr, marketplace_list[j])
                        MACT[0] = MACT[0] - nbrCurr * CURR[j][-1]
                        MACT[j + 1] = nbrCurr
                        BUYVALUE[j] = CURR[j][-1]
                        MAXVALUE[j] = CURR[j][-1]
            j = j + 1

########################################################################################################
##      @param: 
##      @def: my algrotythm
##      @brief: main function of algorythm
##      @return: 0
########################################################################################################

def my_algorithm():
    #vériie qu'il y a au moins 10 trucs
    j = 0
    while (j < 4):
        if (len(CURR[j]) < 10):
            return
        j = j + 1
    #calcul les bandes de bollinger
    calc_band()
    #Coef de variations
    VARCOEF = valcVarCoef()
    #Vérife les pics des actions qu'on a
    setpic()
    sellCurrencies()
    buyCurrencies(VARCOEF)
    return

#vérifier si acheter :
#vérifier si il y a assez de bandes de bollinger -> ou pas acheter le truc qui monte
#si il y a une croissance de + 10% d'un coup acheter aussi
#pour choisir quel cour acheter -> renvoyer celui avec le meilleur coef de variation -> dernier nbr/moyennes
#sinon acheter un cour qui monte
#idea = si la valeur à baissé de -de 10% la vendre

#tant que la valeur grimpe la garder. Si la valeur baisse de -de 5% que la plus haute valeur atteinte vendre
#Trouver les marchés qui grimpent -> vérifier les 10 dernière occurences et calculer les fluctuations
# regarder le marché ou les bandes de bollinger se sont resseré. Acheter. Retenir la valeur d'achat

########################################################################################################
##      @param: /
##      @def: sell_all_then_exit
##      @brief: sell all the currencys then exit
##      @return: 0
########################################################################################################
        
def sell_all_then_exit(MACT):
    i = 0
    while (i < 4):
        if (MACT[i + 1] > 0):
            write_cmd("SELL", MACT[i + 1], marketplace_list[i])
            MACT[0] = MACT[0] + MACT[i + 1] * CURR[i][-1]
        i = i + 1
    if (PRINTBOOL== True):
        print(MACT[0])
    write_cmd("STATS", -1, "stats")
    write_cmd("EXIT", -1, "exit")
    return (0)

########################################################################################################
##      @param: /
##      @def: main
##      @brief: call the algorythm fct. Got the datas with all the indexes data per monney.
##      MACT = MONEY + ACTION IN A TAB
##      @return: 0
########################################################################################################
        
def main():
    i = 0;
    j = 0;
    while (i < 360) :
        j = 0
        if (PRINTBOOL== True):
            print("RANK", i, MACT, "\n")
        while (j < 4):
            CURR[j].append(GetValue(marketplace_list[j]))
            j = j + 1
        my_algorithm()
        time.sleep(0.5)
        i = i + 1;
    return (sell_all_then_exit(MACT))

if (__name__ == '__main__'):
    main()
