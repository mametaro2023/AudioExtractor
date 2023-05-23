from yt_dlp import YoutubeDL as yd
import yt_dlp
import PySimpleGUI as sg
import ffmpeg
import os



#GUI
sg.theme('Dark Blue 3')

layout = [  [sg.Text("動画（再生リスト）のURL:",size=(30,1)),sg.Input(size=(65,1),key="link")],
            [sg.Text("出力フォルダ先:",size=(30,1)), sg.Input(size=(65,1)), sg.FolderBrowse("参照", key="path")],
            [sg.Text("")],
            [sg.Text("詳細設定",size=(30,1))],
            [sg.Text("音質",size=(30,1)),
                sg.Radio("最低", "sound quality",key="ulow",enable_events=True),
                sg.Radio("低", "sound quality",key="low",enable_events=True),
                sg.Radio("中", "sound quality", default=True,key="medium",enable_events=True),
                sg.Radio("ULTIMATE", "sound quality", key="ult",enable_events=True)],
            [sg.Text("普段使用しているブラウザ      (Cookieを使います)",size=(30,2)),
                sg.Radio("Chrome", "browser",key="chrome",enable_events=True,default=True),
                sg.Radio("Edge", "browser",key="edge",enable_events=True),],
            [sg.Text("",key="ult_caution",size=(80,4),text_color="orange")],    
            [sg.Text("コーデック",size=(30,1)),
                sg.Radio("AAC", "codec",key="aac",default=True,enable_events=True),
                sg.Radio("Opus", "codec",key="opus",enable_events=True)],
            [sg.Text("",key="codec_caution",size=(70,2),text_color="orange")],     
            [sg.Checkbox('mp3に変換',key="normalize")],
            [sg.Text("",key="caution")],
            [sg.Text("")],
            [sg.Button("実行",key="go")],
            [sg.Multiline(size=(100,20), key="out")]
            #[sg.Output(size=(100,20), key="out")]
             ]

window = sg.Window('Audio Extractor', layout)

def DL():
        try:
            URL = str(values["link"])
            output_folder = str(values["path"]+'/%(title)s'+".%(ext)s")
            
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
                extract = ".opus"
                if values["ulow"] == True:
                    audio_format = str("600"+"/599"+"/139"+"/worstaudio"+"/worst")
                elif values["low"] == True:
                    audio_format = str("249"+"/250"+"/139"+"/bestaudio[abr<=64K]"+"/best[abr<=64K]")
                elif values["medium"] == True:
                    audio_format = str("251"+"/140"+"/bestaudio[abr<=257K]"+"/best[abr<=257K]")
            
            if values["edge"] == True:
                cookie = str("edge")
            elif values["chrome"] == True:
                cookie = str("chrome")
            

            option = {
                    "cookiesfrombrowser": (cookie, ),
                    "outtmpl" : output_folder,
                    "format" : audio_format,
                    "postprocessors" : [{
                        "key": "FFmpegExtractAudio",

                    }]
                    
                }        
            
            

            event = None
            window["out"].print("ダウンロード成功")
            info = yd(option).extract_info(URL,download=True)

            filename = str(values["path"]+'/'+info["title"])

            window["out"].print("ファイル名:"+values["path"]+'/'+info["title"])

            if values["normalize"] == True:
                normalize(filename,extract)

        except yt_dlp.DownloadError:
            if values["opus"] == True:
                window["out"].print("ダウンロード失敗。YouTube上でこの音質のOpusの音声ファイルが見つかりませんでした。AACまたは別の音質のOpusを試してください。")
            else :
                window["out"].print("ダウンロード失敗。URLまたは保存先が誤っています。")
        
        except FileNotFoundError:
            if cookie == "chrome":
                window["out"].print("ダウンロード失敗。Chromeがインストールされていません。")
            if cookie == "edge":
                window["out"].print("ダウンロード失敗。Edgeがインストールされていません。")

def normalize(a,b):
    input = ffmpeg.input(a + b)
    input = ffmpeg.output(input, a+".mp3", acodec="libmp3lame", audio_bitrate="192k")
    ffmpeg.run(input,overwrite_output=True)
    os.remove(a + b)
                

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "ult":
        window["opus"].Update(disabled=True)
        window["codec_caution"].Update("")
        window["ult_caution"].Update("※音質「ULTIMATE」はYouTubeの音声をダウンロードする場合Premium加入者でかつ                         YouTube MusicのURLを貼り付ける必要があります。"+
                                     "              ※YouTube以外のサイトの場合ファイルサイズが非常に大きくなる可能性があります。")
        #window["edge"].Update(disabled=False)
        #window["chrome"].Update(disabled=False)
    elif event == "ulow" or event == "low" or event == "medium":
        window["ult_caution"].Update("")
        window["opus"].Update(disabled=False)
        window["aac"].Update()
        #window["edge"].Update(disabled=True)
        #window["chrome"].Update(disabled=True)

    if event == "opus":
        window["codec_caution"].Update("音質はAACよりも向上しますが、iPhoneでは再生できません。またOpusファイルが見つからなかった場合AACでダウンロードします。")
    elif event == "aac":
        window["codec_caution"].Update("")

    if event == "go":
        DL()
        


window.close()
