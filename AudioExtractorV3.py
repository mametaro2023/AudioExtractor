from yt_dlp import YoutubeDL as yd
import yt_dlp
import PySimpleGUI as sg
import ffmpeg
import os
import shutil
import subprocess as sp
import requests

"""
バグ報告:同一フォルダ内にすでに同じファイル名が存在する時プログラムが停止するバグがあります。

"""



#GUI
sg.theme('Dark Blue 3')

frame_sq = [  
    [sg.Radio("最低", "sound quality",key="ulow",enable_events=True)],
    [sg.Radio("低", "sound quality",key="low",enable_events=True)],
    [sg.Radio("中", "sound quality", default=True,key="medium",enable_events=True)],
    [sg.Radio("ULTIMATE", "sound quality", key="ult",enable_events=True)]
    ]

frame_browser = [
    [sg.Radio("Chrome", "browser",key="chrome",enable_events=True,default=True)],
    [sg.Radio("Edge", "browser",key="edge",enable_events=True)],
    [sg.Text("")],
    [sg.Text("※Cookieを使います")],
    ]

frame_codec = [
    [sg.Radio("AAC", "codec",key="aac",default=True,enable_events=True)],
    [sg.Radio("Opus", "codec",key="opus",enable_events=True)],
    [sg.Radio("mp3", "codec",key="mp3",enable_events=True)],
    ]


layout = [  [sg.Text("動画のURL:",size=(20,1)),sg.Input(size=(65,1),key="link",enable_events=True),sg.Button("検索",key="show")],
            [sg.Text("ファイル名:",size=(20,1)), sg.Input(size=(55,1),key="titlename",disabled_readonly_background_color="gray"),sg.Text(".m4a",size=(10,1),key="extention"),],
            [sg.Text("動画情報",size=(30,1))],
            [sg.Image(filename = "",key="thumbnail",size=(240,135)),sg.Text("ID:\n動画タイトル:\nチャンネル名:\n長さ:\n再生回数:",size=(40,6),key="videoinfo")],
            [sg.Text("出力フォルダ先:",size=(20,1)), sg.Input(size=(65,1),key="pathname"), sg.FolderBrowse("参照", key="path")],
            [sg.Text("詳細設定",size=(30,1))],
            [sg.Frame("音質", frame_sq,size=(150,150)),
             sg.Frame("普段使用するブラウザ",frame_browser,size=(150,150)), 
             sg.Frame("コーデック",frame_codec,size=(150,150)),],               
            [sg.Text("",key="caution",size=(80,4),text_color="orange")],                       
            [sg.Checkbox("音量調整する",key="normalize",size=(27,1),enable_events=True),
                sg.Radio("-14LUFS(音楽用)","lufs",key="14",disabled=True,default=True),
                sg.Radio("-23LUFS(作業用及びその他の目的)","lufs",key="23",disabled=True)],
            [sg.Button("実行",key="go",size=(20,2))],
            [sg.Multiline(size=(95,10), key="out")],

             ]

window = sg.Window('Audio Extractor', layout)


def DL():
        try:
            window["out"].print("ダウンロードを開始します。")
            URL = str(values["link"])    
            TITLENAME = values["titlename"].replace("/","\u29f8")
            if TITLENAME == "動画タイトル名" or "list" in values["link"]:
                TITLENAME = "%(title)s"
                output_folder = str(values["path"]+"/output/"+TITLENAME+".%(ext)s")

            else:
                output_folder = str(values["path"]+"/"+TITLENAME+".%(ext)s")
            
            if values["ult"] == True:
                audio_format = str("141"+"/140"+"/bestaudio"+"/best")

            if values["aac"] == True:
                extract = ".m4a"
                if values["ulow"] == True:
                    audio_format = str("599"+"/139"+"/worstaudio"+"/worst")
                elif values["low"] == True:
                    audio_format = str("139"+"/bestaudio[abr<=64K]"+"/best[abr<=64K]")
                elif values["medium"] == True:
                    audio_format = str("140"+"/bestaudio[abr<=257K]"+"/best[abr<=257K]")
            
            if values["opus"] == True:
                extract = ".webm"
                if values["ulow"] == True:
                    audio_format = str("600"+"/599"+"/139"+"/worstaudio"+"/worst")
                elif values["low"] == True:
                    audio_format = str("249"+"/250"+"/139"+"/bestaudio[abr<=64K]"+"/best[abr<=64K]")
                elif values["medium"] == True:
                    audio_format = str("251"+"/140"+"/bestaudio[abr<=257K]"+"/best[abr<=257K]")

            if values["mp3"] == True:
                extract = ".m4a"
                audio_format = str("141"+"/140"+"/bestaudio"+"/best")
            
            if values["edge"] == True:
                cookie = str("edge")
            elif values["chrome"] == True:
                cookie = str("chrome")
            

            option = {
                    "cookiesfrombrowser": (cookie, ),
                    "outtmpl" : output_folder,
                    "format" : audio_format,
                    "ignoreerrors" : True,
                    }        
            
            filename = values["path"] + "/" + TITLENAME   
            info = yd(option).extract_info(URL,download=True)
            window["out"].print("ダウンロード成功")
            window["out"].print("ファイル名:"+ filename)


            

            if values["normalize"] == True:
                normalization(filename,extract,values["ulow"],values["low"],values["medium"],info["ext"])

            elif values["mp3"] == True:
                ChangeTomp3(filename,extract,values["ulow"],values["low"],values["medium"])

            window["go"].Update(disabled=False)
            
        except yt_dlp.DownloadError:
            window["go"].Update(disabled=False)
            if values["opus"] == True:
                window["out"].print("ダウンロード失敗。YouTube上でこの音質のOpusの音声ファイルが見つかりませんでした。AACまたは別の音質のOpusを試してください。")

            else :
                window["out"].print("ダウンロード失敗。URLまたは保存先が誤っています。")

        
        except FileNotFoundError:
            window["go"].Update(disabled=False)
            if cookie == "chrome":
                window["out"].print("ダウンロード失敗。Chromeがインストールされていません。")

            if cookie == "edge":
                window["out"].print("ダウンロード失敗。Edgeがインストールされていません。")

def AddDirectory(f):
    f_plusext = str(values["path"]+"/output/") + f
    return os.path.splitext(f_plusext)[0]

def Extentions(f):
    f_plusext = str(values["path"]+"/output/") + f
    return os.path.splitext(f_plusext)[1]

def AddDirectoryPlusExt(f):
    return str(values["path"]+"/output/") + f

def GetThumbnail():

    info = yd().extract_info(values["link"],download=False)
    window["titlename"].Update(info["title"],disabled=False)
    
    videoinfo = str("ID:"+info["id"]+
                "\n動画タイトル:"+info["title"]+
                "\nチャンネル名:"+info["uploader"]+
                "\n長さ:"+str(info["duration"])+"秒"+
                "\n再生回数:"+str(info["view_count"])+"回"
            )
    window["videoinfo"].Update(videoinfo)

    data = requests.get(info["thumbnail"])
    picture = data.content
    thumbnail_output = "Pictures/" + info["title"] + ".png"
    conved_output = "Pictures/conved_" + info["title"] + ".png"
    with open(thumbnail_output, "wb") as writepicture:
        writepicture.write(picture)
        writepicture.close()
    picconv = ffmpeg.input(thumbnail_output)
    picconv = ffmpeg.filter(picconv, "scale" ,width = 240,height = -1)
    picconv = ffmpeg.output(picconv, conved_output,update=True,vcodec="png")
    ffmpeg.run(picconv,overwrite_output=True)
    window["thumbnail"].Update(filename = conved_output)

        


    
    

def ChangeTomp3(a,b,ulow,low,mid):
    window["out"].print("mp3に変換します。")

    if ulow == True:
        bitrate = "64k"
    if low == True:
        bitrate = "96k"
    if mid == True:
        bitrate = "192k"

    input = ffmpeg.input(a + b)
    input = ffmpeg.output(input,a +".mp3", acodec="libmp3lame", audio_bitrate=bitrate)
    ffmpeg.run(overwrite_output=True)
    window["out"].print("mp3に変換しました。")
    os.remove(a + b)


def normalization(a,b,ulow,low,mid,ext):
    if "list" in values["link"]:
        foldername = str(values["path"]+"/output/")
        files = os.listdir(foldername)
        window["out"].print(files)
        temp00 = files
        temp01= map(AddDirectory, files)
        ext_temp = map(Extentions, files)
        files = list(temp01)
        extents = list(ext_temp)
    
        

    else: 
        files = [a]
        extents = ["."+ext]
        
    counter = 0

    if values["14"] == True:
        lufs = int(14)
    elif values["23"] == True:
        lufs = int(23)

    if b == ".m4a":
        if values["mp3"] == True:
            audicodec = "libmp3lame"
        else:
            audicodec = "aac"
        
        if ulow == True:
            bitrate = "64k"
        if low == True:
            bitrate = "96k"
        if mid == True:
            bitrate = "192k"
    elif b == ".webm":
        audicodec = "libopus"
        if ulow == True:
            bitrate = "48k"
        if low == True:
            bitrate = "64k"
        if mid == True:
            bitrate = "128k"
            
    
    for i in files:
        #print(i+extents[counter])
        input = ffmpeg.input(i + extents[counter])
        input = ffmpeg.filter(input, "ebur128" ,metadata=1,framelog="verbose",)
        input = ffmpeg.filter(input, "ametadata", mode="print", file=i+".txt")
        input = ffmpeg.output(input, "-" ,f="null")
        ffmpeg.run(input,overwrite_output=True)

        loud = open(i+".txt", "r")
        le_loudness_note = loud.readlines()
        le_loudness = le_loudness_note[-4]
        target = le_loudness.find("=")
        loudness = float(le_loudness[target + 1:])
        gain = float(- (lufs + loudness))
        loud.close()
        os.remove(i + ".txt")

        window["out"].print("音量調整を行います。")
        

        re_input = ffmpeg.input(i + extents[counter])
        re_input = ffmpeg.filter(re_input, "volume",str(gain)+"dB")
        
        if values["mp3"] == True:
            re_input = ffmpeg.output(re_input, i + ".mp3",acodec="libmp3lame",audio_bitrate=bitrate)
            ffmpeg.run(re_input)
            os.remove(i + extents[counter])
        else:
            re_input = ffmpeg.output(re_input, i + "normalized_"+b,acodec=audicodec,audio_bitrate=bitrate)
            ffmpeg.run(re_input,overwrite_output=True)
            os.remove(i + extents[counter])
            os.rename(i + "normalized_"+b,i+b)
        
        window["out"].print("音量調整しました。")
        window["out"].print("元の音量から"+str(gain)+"dB変更しました。")
        counter += 1
    
    if len(files) > 1:
        files = os.listdir(foldername)
        temp02=files
        temp03= map(AddDirectoryPlusExt, files)
        files = list(temp03)
        j = 0
        for i in files:
            shutil.move(i,str(values["path"]) + "/" + temp02[j])
            j += 1
        shutil.rmtree(foldername)


while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    """
    if event == "link":
        if "https://www.youtube.com/watch?v=" in values["link"]:
            try:
                info = yd().extract_info(values["link"],download=False)
                window["titlename"].Update(info["title"])
            except yt_dlp.DownloadError:
                window["out"].print("指定URLで検索しましたが動画または音声が見つかりませんでした。")
    """
    if event == "normalize":
        if values["normalize"] == True:
            window["14"].Update(disabled=False)
            window["23"].Update(disabled=False)
        else:
            window["14"].Update(disabled=True)
            window["23"].Update(disabled=True)
    

    if event == "show":
            try:
                if "list" in values["link"]:
                    window["out"].print("再生リストは複数の動画をダウンロードするため、複数動画のダウンロード先フォルダ名のみ指定できます。")
                    window["titlename"].Update("動画タイトル名",disabled=True)
                else:
                    
                    window.perform_long_operation(GetThumbnail,"completed")
                    


                    #window["thumbnail"].Update(filename = "Pictures/watch this.png")
            except yt_dlp.DownloadError:
                window["out"].print("指定URLで検索しましたが動画または音声が見つかりませんでした。")
            


    if event == "ult":
        window["opus"].Update(disabled=True)
        window["mp3"].Update(disabled=True)
        window["caution"].Update("")
        window["caution"].Update("※音質「ULTIMATE」はYouTubeの音声をダウンロードする場合Premium加入者でかつYouTube MusicのURLを貼り付ける必要があります。\n※YouTube以外のサイトの場合ファイルサイズが非常に大きくなる可能性があります。")
    elif event == "ulow" or event == "low" or event == "medium":
        window["caution"].Update("")
        window["opus"].Update(disabled=False)
        window["mp3"].Update(disabled=False)
        window["aac"].Update()
        
    if event == "opus":
        window["extention"].Update(".webm")
        window["caution"].Update("音質はAACよりも向上しますが、iPhoneでは再生できません。またOpusファイルが見つからなかった場合AACでダウンロードします。")
    elif event == "aac":
        if values["ult"] == False:
            window["caution"].Update("")
        window["extention"].Update(".m4a")
        
    elif event == "mp3":
        window["extention"].Update(".mp3")
        window["caution"].Update("ファイルサイズがOpusやAACよりもやや大きくなります。")


    if event == "go":
        
        if values["titlename"] == "":
            info = yd().extract_info(values["link"],download=False)
            window["titlename"].Update(info["title"])
            window["out"].print("ファイル名が指定されていません。")
            window["out"].print("ファイル名は動画または音声のタイトルに設定しました。")  
        #elif "/" in values["titlename"]:
        #    window["out"].print("ファイル名に'/'を含めることはできません。")         
        elif values["pathname"] == "":
            window["out"].print("出力フォルダ先が指定されていません。")
        else:
            window.perform_long_operation(DL, "complete")
            window["go"].Update(disabled=True)



window.close()
