from tkinter import *;
from types import SimpleNamespace;
import matplotlib.pyplot as plt;
import numpy as np;
from PIL import ImageTk,Image;
import os;

#sub script
import analysis_edited;

#custom sort function bc i cant get zip to work
def cordsToInt(x , y):
    i = 0;
    while i < len(x):
        x[i] = float(x[i]);
        y[i] = float(y[i]);

        i += 1;

    return(x , y);

#call sub script
def callAnalysis():
    try:
        if(fightNBR_entry.get() == ''):
            fightNBR_entry.insert(END, str(1));
        checkDSOutput , individualLogs = analysis_edited.main(url_entry.get() , fightNBR_entry.get());
    except:
        displayLogResult.config(text = "Error: Please double check the link provided and try again...");

    keyStats = checkDSOutput[0];
    tbl = checkDSOutput[1];
    displayLogResult.config(text = keyStats);
    displayLogResult.grid(row=2);

    i = 1;
    logFights = '';
    while i <= len(individualLogs):
        logFights += (str(i) + " " + individualLogs[i]['zoneName'] + ": " + str(individualLogs[i]['keystoneLevel']) + "\n");
        i += 1;

    displayFightsUpper = Label(root , text = "keys:");
    displayFightsLower = Label(root , text = logFights);
    displayFightsUpper.grid(row = 0 , column = 2);
    displayFightsLower.grid(row = 1 , column = 2);

    global recentLogData; #fuck it, bad code go brrrrrrr
    recentLogData = [[]];

    i = 0;
    while i < len(tbl):
        vars = SimpleNamespace(**tbl[i])
        recentLogData[i].append(str(vars.timestamp));       #0
        recentLogData[i].append(str(vars.amount));          #1
        recentLogData[i].append(str(vars.overheal));        #2
        recentLogData[i].append(str(vars.runic_power));     #3
        recentLogData[i].append(str(vars.hitPoints));       #4
        recentLogData[i].append(str(vars.maxHitPoints));    #5
        recentLogData[i].append(str(vars.BS_absorb));       #6
        recentLogData[i].append(str(vars.hitPointsBefore)); #7
        recentLogData[i].append(str(vars.healthPbefore));   #8
        recentLogData[i].append(str(vars.healthPafter));    #9
        recentLogData[i].append(str(vars.VB_Active));       #10

        i += 1;
        recentLogData.append([]);

    #########################################
    #                                       #
    #        TIME TO GENERATE GRAPHS        #
    #                                       #
    #########################################
    try:
        os.remove('recentPie.png');
        os.remove('recentScatter.png');
        os.remove('recentBS.png');
        os.remove('recentHeatMap.png')
    except:
        pass


    #rphp graph ----------------------------------------------------------------------------------------------------------------------
    i = 0;
    xRPHP = [];
    yRPHP = [];
    while i < len(recentLogData) - 1:
        xRPHP.append(recentLogData[i][8]);
        yRPHP.append(recentLogData[i][3]);
        i += 1;

    
    xRPHP , yRPHP = cordsToInt(xRPHP , yRPHP);
    
    plt.figure(0);
    plt.scatter(xRPHP , yRPHP , marker = '*');
    lable = ['' , ''];
    plt.xlabel('HP before DS');
    plt.ylabel('RP before DS');
    plt.xticks(np.arange(0 , 110 , step = 10));
    plt.yticks(np.arange(0 , 125 , step = 15));
    plt.savefig('recentScatter.png' , bbox_inches = 'tight');
    plt.close();


    #rphp heat map ---------------------------------------------------------------------------------------------------------------
    plt.figure(1);
    plt.hist2d(xRPHP , yRPHP , bins = (50,50));
    plt.savefig('recentHeatMap.png' , bbox_inches = 'tight');
    plt.close();
    

    #vb pie chart ----------------------------------------------------------------------------------------------------------------
    i = 0;
    j = 0;
    while i < len(recentLogData) - 1:
        if(recentLogData[i][10] == 'True'):
            j += 1;
        i += 1;
    plt.figure(2);
    sizes = [float((j/i)*100) , float((1-(j/i))*100)]
    lable = ["with VB" , "without VB"];
    plt.xlabel('');
    plt.ylabel('');
    plt.pie(sizes , labels = lable , autopct = '%1.1f%%');
    plt.savefig('recentPie.png' , bbox_inches = 'tight');
    plt.close();


    #blood shield graph --------------------------------------------------------------------------------------------------------------
    i = 0;
    dataX = [];
    dataY = [];
    while i < len(recentLogData) - 1:
        dataX.append(str(recentLogData[i][0]));
        dataX[i] = dataX[i].replace(':' , '.');
        dataY.append(float(recentLogData[i][6]));
        i += 1;
    plt.figure(3);
    plt.scatter(dataX , dataY , marker = '*');
    plt.xlabel('time');
    plt.ylabel('BS ammount when DS');
    plt.xticks(np.arange(0 , 0));
    plt.yticks(np.arange(0 , 1.1 * max(dataY) , step = float(max(dataY)/10)));
    plt.savefig('recentBS.png' , bbox_inches = 'tight');
    plt.close();


    #graph creation in the UI --------------------------------------------------------------------------------------------
    global imgPie
    global Pie
    global imgScatter
    global scatter
    global imgBS
    global BS
    global HeatMap
    global imgHeatMap

    try:
        imgPie.destroy;
        imgScatter.destroy;
        imgBS.destroy;
        imgHeatMap.destroy;
    except:
        pass

    Pie = Image.open('recentPie.png');
    imgPie = Canvas(root , width = Pie.size[0] , height = Pie.size[1]);
    imgPie.grid(row = 3 , column = 0);
    Pie = ImageTk.PhotoImage(Image.open("recentPie.png"));
    imgPie.create_image(20 , 0 , image = Pie , anchor = 'nw');

    scatter = Image.open('recentScatter.png');
    imgScatter = Canvas(root , width = scatter.size[0] , height = scatter.size[1]);
    imgScatter.grid(row = 3 , column = 1);
    scatter = ImageTk.PhotoImage(Image.open("recentScatter.png"));
    imgScatter.create_image(20 , 0 , image = scatter , anchor = 'nw');

    BS = Image.open('recentBS.png');
    imgBS = Canvas(root , width = BS.size[0] , height = BS.size[1]);
    imgBS.grid(row = 4 , column = 0);
    BS = ImageTk.PhotoImage(Image.open("recentBS.png"));
    imgBS.create_image(20 , 0 , image = BS , anchor = 'nw');

    HeatMap = Image.open('recentHeatMap.png');
    imgHeatMap = Canvas(root , width = HeatMap.size[0] , height = HeatMap.size[1]);
    imgHeatMap.grid(row = 4 , column = 1);
    HeatMap = ImageTk.PhotoImage(Image.open("recentHeatMap.png"));
    imgHeatMap.create_image(20 , 0 , image = HeatMap , anchor = 'nw');
    
    
    

#window
root = Tk();

#create wigit for log result
displayLogResult = Label(root , text = "no result yet");
displayLogResult.grid(row=2,column=0);

#title / dim / icon
root.title("wow DS log analyser");
root.geometry('350x200');
root.iconbitmap("DS.ico");

#log input window
url_label = Label(root , text = "log URL:");
url_entry = Entry(root);
fightNBR_label = Label(root , text = "fight nbr (leave 1 if only 1 fight):");
fightNBR_entry = Entry(root);
fightNBR_entry.insert(END, str(1));

url_label.grid(row=0,column=0);
url_entry.grid(row=0,column=1);
fightNBR_label.grid(row = 1 , column = 0);
fightNBR_entry.grid(row = 1 , column = 1);

#button
btn1 = Button(root , text = "run DS analyser" , command = callAnalysis);
btn1.grid(row=2, column = 1);

#mainloop
root.mainloop();