import soundcloud
import urllib
import requests
import sys
from bs4 import BeautifulSoup
from xml.etree import ElementTree


reload(sys)  # Reload system to fix some encoding issues
sys.setdefaultencoding('UTF8')

def getSoundCloudList(username):
    #Can edit client info and soundcloud url to download playlists, or other pages
    client = soundcloud.Client(client_id='14896021762c6804e501468d3d30aa05')
    tracks = client.get('/resolve', url="https://soundcloud.com/%s/likes" % username)
    titles = []
    #Limit the amount of recent tracks here by using list(tracks)[:10], [:20], etc.
    for track in list(tracks):
        titles.append(track.title)
        print "Track #" + str(len(titles)) +" is " + str(track.title).encode(sys.getfilesystemencoding())
    return titles

def getYoutubeURLList(tracks):
    URLList = []
    for track in tracks:
        searchURL1 = "https://www.youtube.com/results?search_query=" + str(track) + "-'music video'" +" +hd +original"
        try:
            searchURL2 = urllib.urlopen(searchURL1).read()
            soup = BeautifulSoup(searchURL2, "html.parser")
            url = soup.find_all("div", class_='yt-lockup yt-lockup-tile yt-lockup-video vve-check clearfix yt-uix-tile')
            URLList.append("https://www.youtube.com/watch?v=" + url[0].get('data-context-item-id'))
        except:
            pass
    return URLList

def getVideoToMp3Urls(urls):
    mp3URLs=[]
    for url in urls:
        try:
            r = requests.post("http://www.listentoyoutube.com/cc/conversioncloud.php", data={"mediaurl": url, "client_urlmap": "none"})
            xmlFileURL = eval(r.text)["statusurl"].replace('\\/','/')
            r2 = requests.get(xmlFileURL)
        #KeyError occurs if the website boots us out temporarily
        except KeyError:
            print 'Uh oh.. the conversion website kicked us out!'
            print 'Go to www.listentoyoutube.com and fill out a captcha'
            break
        #Parsing xml file for 'downloadurl' key
        while True:
            try:
                mp3URL = ElementTree.fromstring(r2.content).find('downloadurl').text
                print mp3URL
                mp3URLs.append(mp3URL)
                break
            except:
                break
    return mp3URLs

def saveMp3(downloadURLs, saveLocation, tracks):
    download=0
    try:
        for url in downloadURLs:
            try:
                urllib.urlretrieve(url, (saveLocation + '\\' + tracks[download].encode(sys.getfilesystemencoding()) +'.mp3'))
            except:
                urllib.urlretrieve(url, (saveLocation + '\\' + 'invalidTitle' + str(download) +'.mp3'))
            download+=1
            print 'Downloaded ' + str(download) +' songs...'
    except:
        print 'Invalid Save Location'

def execute(soundCloudUsername, saveLocation):
    print "Getting your track list from SoundCloud..."
    tracks = getSoundCloudList(soundCloudUsername)
    print "Getting the best Youtube video that coincides to each track..."
    youtubeURLs = getYoutubeURLList(tracks)
    print "Getting mp3 download URLs..."
    downloadURLs = getVideoToMp3Urls(youtubeURLs)
    print 'Saving mp3 download URLs to your specified folder...'
    saveMp3(downloadURLs, saveLocation, tracks)
    print 'Save complete!'

#Example: execute('toddashley13','Desktop')
execute('yourSoundCloudUsernameHere','yourSaveLocationHere')


    