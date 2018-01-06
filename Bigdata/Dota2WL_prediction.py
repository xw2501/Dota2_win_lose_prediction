import numpy as np
import matplotlib.pyplot as plt
import wx
import requests
import json
import os
import shutil
import math
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib.pyplot import gcf, setp
from sklearn.externals import joblib

LR_g2 = joblib.load('models/LR_g2.pkl')
LR_g4 = joblib.load('models/LR_g4.pkl')
LR_g6 = joblib.load('models/LR_g6.pkl')
LR_g8 = joblib.load('models/LR_g8.pkl')
LR_g0 = joblib.load('models/LR_g0.pkl')
LR_x2 = joblib.load('models/LR_x2.pkl')
LR_x4 = joblib.load('models/LR_x4.pkl')
LR_x6 = joblib.load('models/LR_x6.pkl')
LR_x8 = joblib.load('models/LR_x8.pkl')
LR_x0 = joblib.load('models/LR_x0.pkl')

DefaultSize = (1000, 500)
DefaultSizeMain = (1920, 1080)
ColorBackground = "#202020"
ColorText = "#A0A0A0"
ColorButton = "#606060"
ColorRadiant = "#FF0000"
ColorDire = "#00CC00"
ColorPlayer = "#EEEE00"

class Param:
    def __init__(self, initialValue=None, minimum=0., maximum=1.):
        self.minimum = minimum
        self.maximum = maximum
        if initialValue != self.constrain(initialValue):
            raise ValueError('illegal initial value')
        self.value = initialValue
        self.knobs = []
        
    def attach(self, knob):
        self.knobs += [knob]
        
    def set(self, value, knob=None):
        self.value = value
        self.value = self.constrain(value)
        for feedbackKnob in self.knobs:
            if feedbackKnob != knob:
                feedbackKnob.setKnob(self.value)
        return self.value

    def constrain(self, value):
        if value <= self.minimum:
            value = self.minimum
        if value >= self.maximum:
            value = self.maximum
        return value


class CanvasFrame(wx.Frame):
    def __init__(self, rc, str_):
        wx.Frame.__init__(self, None, title="Real Time "+str_+" Comparison", size=DefaultSize)
        self.figure = Figure(facecolor=ColorBackground, edgecolor=ColorBackground)
        self.lines = []
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_subplot(111)
        self.canvas.callbacks.connect('button_press_event', self.mouseDown)
        self.canvas.callbacks.connect('motion_notify_event', self.mouseMotion)
        self.canvas.callbacks.connect('button_release_event', self.mouseUp)
        self.state = ''
        self.mouseInfo = (None, None, None, None)
        if str_=="Gold":
            select = "gold_t"
        else:
            select = "xp_t"
        self.str = str_
        PlayersStats = []
        for i in range(10):
            PlayersStats.append(rc["players"][i][select])
        PlayersStats = np.asarray(PlayersStats)
        RadiantStats = sum(PlayersStats[0:5])
        DireStats = sum(PlayersStats[5:10])
        RadiantAdv = (RadiantStats - DireStats).tolist()
        x = []
        base = []
        for i in range(len(RadiantAdv)):
            x.append(i)
            base.append(0)
        x = np.asarray(x)
        base = np.asarray(base)
        self.lower = min(RadiantAdv)
        self.upper = max(RadiantAdv)
        RadiantAdv = np.asarray(RadiantAdv)
        self.axes.plot(x, RadiantAdv, x, base, color=ColorText, mec=ColorBackground, mfc=ColorBackground)
        self.axes.fill_between(x, RadiantAdv, base, where=RadiantAdv>=base, facecolor=ColorRadiant, interpolate=True)
        self.axes.fill_between(x, RadiantAdv, base, where=RadiantAdv<=base, facecolor=ColorDire, interpolate=True)
        self.axes.set_xlabel('time/minute', {'color':ColorText})
        self.axes.set_ylabel('Radiant '+str_+' Adv', {'color':ColorText})
        self.axes.set_facecolor(ColorBackground)
        self.axes.set_xticklabels(self.axes.get_xticks(), color=ColorText)
        self.axes.set_yticklabels(self.axes.get_yticks(), color=ColorText)
        self.axes.tick_params(axis='both', color=ColorText)
        self.axes.set_frame_on(False)
        self.f0 = Param(0., minimum=0., maximum=float(len(x)))
        self.RadiantAdv = RadiantAdv
        self.draw()
        self.f0.attach(self)
        self.Bind(wx.EVT_SIZE, self.sizeHandler)
        
    def sizeHandler(self, *args, **kwargs):
        self.canvas.SetSize(self.GetSize())
        
    def mouseDown(self, evt):
        if self.lines[0] in self.figure.hitlist(evt):
            self.state = 'frequency'
        else:
            self.state = ''
        self.mouseInfo = (evt.xdata, evt.ydata, self.f0.value)

    def mouseMotion(self, evt):
        if self.state == '':
            return
        x, y = evt.xdata, evt.ydata
        if x is None:
            return
        x0, y0, f0Init = self.mouseInfo
        if self.state == 'frequency':
            self.f0.set((x-x0)+f0Init)
                    
    def mouseUp(self, evt):
        self.state = ''

    def draw(self):
        x1, y1 = self.compute(self.f0.value)
        self.lines += self.axes.plot(x1, y1, color=ColorText, linewidth=1)
        time = self.f0.value
        preIndex = math.floor(time)
        posIndex = math.ceil(time)
        RadiantAdv = (self.RadiantAdv[posIndex]-self.RadiantAdv[preIndex])*(time-preIndex)
        RadiantWinRate = 0.5
        self.text1 = self.axes.text(0.05, .95, "time: "+str(time), verticalalignment='top', transform = self.axes.transAxes, color = ColorText)
        self.text2 = self.axes.text(0.05, .90, "adv: "+str(RadiantAdv), verticalalignment='top', transform = self.axes.transAxes, color = ColorText)
        self.text3 = self.axes.text(0.05, .85, "winRate: "+str(RadiantWinRate), verticalalignment='top', transform = self.axes.transAxes, color = ColorText)
        
        
    def compute(self, f0):
        x = np.arange(self.lower, self.upper, 10)
        f = np.full(x.shape, f0)
        return f, x

    def repaint(self):
        time = self.f0.value
        preIndex = math.floor(time)
        posIndex = math.ceil(time)
        RadiantAdv = (self.RadiantAdv[posIndex]-self.RadiantAdv[preIndex])*(time-preIndex) + self.RadiantAdv[preIndex]
        time_ratio = time/len(self.RadiantAdv)
        if self.str=="Gold":
            if time_ratio<0.2:
                RadiantWinRate = LR_g2.predict_proba(RadiantAdv)[0][1]
            elif time_ratio<0.4:
                RadiantWinRate = LR_g4.predict_proba(RadiantAdv)[0][1]
            elif time_ratio<0.4:
                RadiantWinRate = LR_g6.predict_proba(RadiantAdv)[0][1]
            elif time_ratio<0.4:
                RadiantWinRate = LR_g8.predict_proba(RadiantAdv)[0][1]
            else:
                RadiantWinRate = LR_g0.predict_proba(RadiantAdv)[0][1]
        else:
            if time_ratio<0.2:
                RadiantWinRate = LR_x2.predict_proba(RadiantAdv)[0][1]
            elif time_ratio<0.4:
                RadiantWinRate = LR_x4.predict_proba(RadiantAdv)[0][1]
            elif time_ratio<0.4:
                RadiantWinRate = LR_x6.predict_proba(RadiantAdv)[0][1]
            elif time_ratio<0.4:
                RadiantWinRate = LR_x8.predict_proba(RadiantAdv)[0][1]
            else:
                RadiantWinRate = LR_x0.predict_proba(RadiantAdv)[0][1]
        self.text1.set_text("time: "+str(time))
        self.text2.set_text("adv: "+str(RadiantAdv))
        self.text3.set_text("winRate: "+str(RadiantWinRate))
        self.canvas.draw()

    def setKnob(self, value):
        x1, y1 = self.compute(self.f0.value)
        setp(self.lines[0], xdata=x1, ydata=y1)
        self.repaint()

class HelloFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title="Dota WL Predictor", size=DefaultSizeMain)

        pnl = wx.Panel(self)
        pnl.SetBackgroundColour(ColorBackground)
        self.pnl = pnl

        st = wx.StaticText(pnl, label="Dota2 Statistics", pos=(25,25))
        st.SetForegroundColour(ColorText)
        TitleFont = wx.Font(40, wx.SCRIPT, wx.NORMAL, wx.BOLD, False)
        st.SetFont(TitleFont)

        self.CreateStatusBar()
        self.SetStatusText("Welcome to Dota2!")  
        
        TextTitle = wx.StaticText(pnl, label="Enter an match ID", pos=(100, 100))
        TextTitle.SetForegroundColour(ColorText)
        self.txt = wx.TextCtrl(pnl, pos=(100, 125), style=wx.NO_BORDER)
        self.txt.SetForegroundColour(ColorText)
        self.txt.SetBackgroundColour("#181818")
        self.btn = []
        self.btn.append(wx.Button(pnl, label='Load Match', pos=(100,175), style=wx.NO_BORDER))
        self.btn[0].SetBackgroundColour(ColorBackground)
        self.btn[0].SetForegroundColour(ColorText)
        self.btn.append(wx.Button(pnl, label='Show Gold', pos=(225,175), style=wx.NO_BORDER))
        self.btn[1].SetBackgroundColour(ColorBackground)
        self.btn[1].SetForegroundColour(ColorText)
        self.btn.append(wx.Button(pnl, label='Show Exp', pos=(350,175), style=wx.NO_BORDER))
        self.btn[2].SetBackgroundColour(ColorBackground)
        self.btn[2].SetForegroundColour(ColorText)
        self.btn.append(wx.Button(pnl, label='Show Stat R', pos=(225,750), style=wx.NO_BORDER))
        self.btn[3].SetBackgroundColour(ColorBackground)
        self.btn[3].SetForegroundColour(ColorText)
        self.btn.append(wx.Button(pnl, label='Show Stat D', pos=(350,750), style=wx.NO_BORDER))
        self.btn[4].SetBackgroundColour(ColorBackground)
        self.btn[4].SetForegroundColour(ColorText)
        self.btn[0].Bind(wx.EVT_BUTTON, self.GetMatch)
        self.btn[0].Bind(wx.EVT_ENTER_WINDOW, lambda event: self.MouseOver(event, 0))
        self.btn[0].Bind(wx.EVT_LEAVE_WINDOW, lambda event: self.MouseLeave(event, 0))
        self.btn[1].Bind(wx.EVT_BUTTON, self.ShowGold)
        self.btn[1].Bind(wx.EVT_ENTER_WINDOW, lambda event: self.MouseOver(event, 1))
        self.btn[1].Bind(wx.EVT_LEAVE_WINDOW, lambda event: self.MouseLeave(event, 1))
        self.btn[2].Bind(wx.EVT_BUTTON, self.ShowExp)
        self.btn[2].Bind(wx.EVT_ENTER_WINDOW, lambda event: self.MouseOver(event, 2))
        self.btn[2].Bind(wx.EVT_LEAVE_WINDOW, lambda event: self.MouseLeave(event, 2))
        self.btn[3].Bind(wx.EVT_BUTTON, self.ShowStatR)
        self.btn[3].Bind(wx.EVT_ENTER_WINDOW, lambda event: self.MouseOver(event, 3))
        self.btn[3].Bind(wx.EVT_LEAVE_WINDOW, lambda event: self.MouseLeave(event, 3))
        self.btn[4].Bind(wx.EVT_BUTTON, self.ShowStatD)
        self.btn[4].Bind(wx.EVT_ENTER_WINDOW, lambda event: self.MouseOver(event, 4))
        self.btn[4].Bind(wx.EVT_LEAVE_WINDOW, lambda event: self.MouseLeave(event, 4))
        
    def ShowStatR(self, event):
        bitmap = wx.Bitmap('temp/xp_R.png', wx.BITMAP_TYPE_ANY)
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(400, 250, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.BitmapFromImage(image)
        wx.StaticBitmap(self.pnl, -1, bitmap, pos=(50,225))
        bitmap = wx.Bitmap('temp/go_R.png', wx.BITMAP_TYPE_ANY)
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(400, 250, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.BitmapFromImage(image)
        wx.StaticBitmap(self.pnl, -1, bitmap, pos=(50,475))
        
    def ShowStatD(self, event):
        bitmap = wx.Bitmap('temp/xp_D.png', wx.BITMAP_TYPE_ANY)
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(400, 250, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.BitmapFromImage(image)
        wx.StaticBitmap(self.pnl, -1, bitmap, pos=(50,225))
        bitmap = wx.Bitmap('temp/go_D.png', wx.BITMAP_TYPE_ANY)
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(400, 250, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.BitmapFromImage(image)
        wx.StaticBitmap(self.pnl, -1, bitmap, pos=(50,475))
    
    def MouseOver(self, event, index):
        self.btn[index].SetBackgroundColour(ColorButton)
        event.Skip()
        
    def MouseLeave(self, event, index):
        self.btn[index].SetBackgroundColour(ColorBackground)
        event.Skip()
        
    def GetMatch(self, event):
        content = self.txt.GetLineText(0)
        response = requests.get("https://api.opendota.com/api/matches/"+content).text
        rc = json.loads(response)
        self.rc = rc
        self.ShowMatchInfo()
        self.PlotStats()
        wx.MessageBox("Loading is done!")
        
    def PlotStats(self):
        players_xp = []
        players_go = []
        rc = self.rc
        index = len(rc["players"][0]["xp_t"])-1
        for i in range(10):
            players_xp.append(rc["players"][i]["xp_t"][index])
            players_go.append(rc["players"][i]["gold_t"][index])
        players_xp = np.asarray(players_xp)
        players_go = np.asarray(players_go)
        base = range(5)
        acc = []
        acc.append(0)
        for i in range(4):
            acc.append(acc[i]+players_xp[i])
        acc.append(0)
        for i in range(4):
            acc.append(acc[i+5]+players_xp[i+5])
        acc = np.asarray(acc)

        figure = plt.figure(facecolor=ColorBackground, edgecolor=ColorBackground)
        axes = figure.add_subplot(111)
        top = acc[4]+players_xp[4]
        axes.bar(base, acc[0:5], label='others', color=ColorRadiant)
        axes.bar(base, players_xp[0:5], bottom=acc[0:5], label='player', color=ColorPlayer)
        axes.bar(base, top-acc[0:5]-players_xp[0:5], bottom=acc[0:5]+players_xp[0:5], label='others', color=ColorRadiant)
        axes.set_xlabel('Players', {'color':ColorText})
        axes.set_ylabel('Exp percentage', {'color':ColorText})
        axes.set_facecolor(ColorBackground)
        axes.set_xticklabels(axes.get_xticks(), color=ColorText)
        axes.set_yticklabels(axes.get_yticks(), color=ColorText)
        axes.tick_params(axis='both', color=ColorText)
        axes.set_frame_on(False)
        figure.savefig('temp/xp_R.png', facecolor=ColorBackground, edgecolor=ColorBackground)

        figure = plt.figure(facecolor=ColorBackground, edgecolor=ColorBackground)
        axes = figure.add_subplot(111)
        top = acc[9]+players_xp[9]
        axes.bar(base, acc[5:10]-acc[5], label='others', color=ColorDire)
        axes.bar(base, players_xp[5:10], bottom=acc[5:10]-acc[5], label='player', color=ColorPlayer)
        axes.bar(base, top-acc[5:10]+acc[5]-players_xp[5:10], bottom=acc[5:10]-acc[5]+players_xp[5:10], label='others', color=ColorDire)
        axes.set_xlabel('Players', {'color':ColorText})
        axes.set_ylabel('Exp percentage', {'color':ColorText})
        axes.set_facecolor(ColorBackground)
        axes.set_xticklabels(axes.get_xticks(), color=ColorText)
        axes.set_yticklabels(axes.get_yticks(), color=ColorText)
        axes.tick_params(axis='both', color=ColorText)
        axes.set_frame_on(False)
        figure.savefig('temp/xp_D.png', facecolor=ColorBackground, edgecolor=ColorBackground)
        
        acc = []
        acc.append(0)
        for i in range(4):
            acc.append(acc[i]+players_go[i])
        acc.append(0)
        for i in range(4):
            acc.append(acc[i+5]+players_go[i+5])
        acc = np.asarray(acc)

        figure = plt.figure(facecolor=ColorBackground, edgecolor=ColorBackground)
        axes = figure.add_subplot(111)
        top = acc[4]+players_go[4]
        axes.bar(base, acc[0:5], label='others', color=ColorRadiant)
        axes.bar(base, players_go[0:5], bottom=acc[0:5], label='player', color=ColorPlayer)
        axes.bar(base, top-acc[0:5]-players_go[0:5], bottom=acc[0:5]+players_go[0:5], label='others', color=ColorRadiant)
        axes.set_xlabel('Players', {'color':ColorText})
        axes.set_ylabel('Gold percentage', {'color':ColorText})
        axes.set_facecolor(ColorBackground)
        axes.set_xticklabels(axes.get_xticks(), color=ColorText)
        axes.set_yticklabels(axes.get_yticks(), color=ColorText)
        axes.tick_params(axis='both', color=ColorText)
        axes.set_frame_on(False)
        figure.savefig('temp/go_R.png', facecolor=ColorBackground, edgecolor=ColorBackground)

        figure = plt.figure(facecolor=ColorBackground, edgecolor=ColorBackground)
        axes = figure.add_subplot(111)
        top = acc[9]+players_go[9]
        axes.bar(base, acc[5:10]-acc[5], label='others', color=ColorDire)
        axes.bar(base, players_go[5:10], bottom=acc[5:10]-acc[5], label='player', color=ColorPlayer)
        axes.bar(base, top-acc[5:10]+acc[5]-players_go[5:10], bottom=acc[5:10]-acc[5]+players_go[5:10], label='others', color=ColorDire)
        axes.set_xlabel('Players', {'color':ColorText})
        axes.set_ylabel('Gold percentage', {'color':ColorText})
        axes.set_facecolor(ColorBackground)
        axes.set_xticklabels(axes.get_xticks(), color=ColorText)
        axes.set_yticklabels(axes.get_yticks(), color=ColorText)
        axes.tick_params(axis='both', color=ColorText)
        axes.set_frame_on(False)
        figure.savefig('temp/go_D.png', facecolor=ColorBackground, edgecolor=ColorBackground)
        
    def ShowGold(self, event):
        frame = CanvasFrame(self.rc, 'Gold')
        frame.Show()
        
    def ShowExp(self, event):
        frame = CanvasFrame(self.rc, 'Exp')
        frame.Show()

    def ShowMatchInfo(self):
        rc = self.rc
        Heros = []
        for i in range(10):
            Heros.append(rc["players"][i]["hero_id"])
        self.ShowHeros(Heros)
        self.ShowPlayers()
        
    def ShowHeros(self, Heros):
        HeroStats = json.loads(requests.get("https://api.opendota.com/api/heroStats").text)
        team = wx.StaticText(self.pnl, label="Radiant", pos=(500,50))
        font = team.GetFont()
        font.PointSize += 10
        font = font.Bold()
        team.SetFont(font)
        team.SetForegroundColour(ColorRadiant)
        text = wx.StaticText(self.pnl, label="hero & player", pos=(660,50))
        text.SetForegroundColour(ColorText)
        text = wx.StaticText(self.pnl, label="KDA", pos=(820,50))
        text.SetForegroundColour(ColorText)
        text = wx.StaticText(self.pnl, label="gold per min", pos=(980,50))
        text.SetForegroundColour(ColorText)
        text = wx.StaticText(self.pnl, label="exp per min", pos=(1140,50))
        text.SetForegroundColour(ColorText)
        text = wx.StaticText(self.pnl, label="kill per min", pos=(1300,50))
        text.SetForegroundColour(ColorText)
        for i in range(5):
            StartIndex = 0
            if int(Heros[i])<len(HeroStats):
                StartIndex = int(Heros[i])
            else:
                StartIndex = len(HeroStats)-1
            while int(HeroStats[StartIndex]["id"])!=int(Heros[i]):
                StartIndex -= 1
            url = "https://api.opendota.com"+HeroStats[StartIndex]["img"]
            response = requests.get(url, stream=True)
            with open("temp/img.png", "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            bitmap = wx.Bitmap("temp/img.png", wx.BITMAP_TYPE_ANY)
            image = wx.ImageFromBitmap(bitmap)
            image = image.Scale(100, 50, wx.IMAGE_QUALITY_HIGH)
            bitmap = wx.BitmapFromImage(image)
            wx.StaticBitmap(self.pnl, -1, bitmap, pos=(500,100+i*60))
            text = wx.StaticText(self.pnl, label=HeroStats[StartIndex]["localized_name"], pos=(650,100+i*60))
            text.SetForegroundColour(ColorText)
            os.remove("temp/img.png")
        team = wx.StaticText(self.pnl, label="Dire", pos=(500,420))
        font = team.GetFont()
        font.PointSize += 10
        font = font.Bold()
        team.SetFont(font)
        team.SetForegroundColour(ColorDire)
        for i in range(5):
            StartIndex = 0
            if int(Heros[i+5])<len(HeroStats):
                StartIndex = int(Heros[i+5])
            else:
                StartIndex = len(HeroStats)-1
            while int(HeroStats[StartIndex]["id"])!=int(Heros[i+5]):
                StartIndex -= 1
            url = "https://api.opendota.com"+HeroStats[StartIndex]["img"]
            response = requests.get(url, stream=True)
            with open("temp/img.png", "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            bitmap = wx.Bitmap("temp/img.png", wx.BITMAP_TYPE_ANY)
            image = wx.ImageFromBitmap(bitmap)
            image = image.Scale(100, 50, wx.IMAGE_QUALITY_HIGH)
            bitmap = wx.BitmapFromImage(image)
            wx.StaticBitmap(self.pnl, -1, bitmap, pos=(500,470+i*60))
            text = wx.StaticText(self.pnl, label=HeroStats[StartIndex]["localized_name"], pos=(650,470+i*60))
            text.SetForegroundColour(ColorText)
            os.remove("temp/img.png")
        
        
    def ShowPlayers(self):
        rc = self.rc
        for i in range(5):
            kda = str(rc["players"][i]["kills"])+"/"
            kda += str(rc["players"][i]["deaths"])+"/"
            kda += str(rc["players"][i]["assists"])
            text = wx.StaticText(self.pnl, label=kda, pos=(820,120+i*60))
            text.SetForegroundColour(ColorText)
            text = wx.StaticText(self.pnl, label=str(rc["players"][i]["gold_per_min"]), pos=(980,120+i*60))
            text.SetForegroundColour(ColorText)
            text = wx.StaticText(self.pnl, label=str(rc["players"][i]["xp_per_min"]), pos=(1140,120+i*60))
            text.SetForegroundColour(ColorText)
            text = wx.StaticText(self.pnl, label=str(rc["players"][i]["kills"]/rc["duration"]*60)[:5], pos=(1300,120+i*60))
            text.SetForegroundColour(ColorText)
            if rc["players"][i]["name"] is None:
                text = wx.StaticText(self.pnl, label="unknown", pos=(660,120+i*60))
                text.SetForegroundColour(ColorText)
                continue
            text = wx.StaticText(self.pnl, label=rc["players"][i]["name"]+"("+str(rc["players"][i]["account_id"])+")", pos=(660,120+i*60))
            text.SetForegroundColour(ColorText)
            
        for i in range(5):
            kda = str(rc["players"][i+5]["kills"])+"/"
            kda += str(rc["players"][i+5]["deaths"])+"/"
            kda += str(rc["players"][i+5]["assists"])
            text = wx.StaticText(self.pnl, label=kda, pos=(820,490+i*60))
            text.SetForegroundColour(ColorText)
            text = wx.StaticText(self.pnl, label=str(rc["players"][i+5]["gold_per_min"]), pos=(980,490+i*60))
            text.SetForegroundColour(ColorText)
            text = wx.StaticText(self.pnl, label=str(rc["players"][i+5]["xp_per_min"]), pos=(1140,490+i*60))
            text.SetForegroundColour(ColorText)
            text = wx.StaticText(self.pnl, label=str(rc["players"][i+5]["kills"]/rc["duration"]*60)[:5], pos=(1300,490+i*60))
            text.SetForegroundColour(ColorText)
            if rc["players"][i+5]["name"] is None:
                text = wx.StaticText(self.pnl, label="unknown", pos=(660,490+i*60))
                text.SetForegroundColour(ColorText)
                continue
            text = wx.StaticText(self.pnl, label=rc["players"][i+5]["name"]+"("+str(rc["players"][i+5]["account_id"])+")", pos=(660,490+i*60))
            text.SetForegroundColour(ColorText)
            
        
app = wx.App()
frm = HelloFrame()
frm.Show()
app.MainLoop()
