from urllib2 import urlopen
import json, os, time
from subprocess import call
import email.utils
from time import mktime
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def uploadFileGoogleDrive(files):
    # Upload the files
    global drive
    for f in files:
        # new_file = drive.CreateFile({"parents": [{"id": PARENT_ID}], "mimeType":"text/plain"})
        new_file = drive.CreateFile({"parents": [{"id": PARENT_ID}]})
        new_file.SetContentFile(f)
        new_file.Upload()
        print ("Uploaded: " + f)

def updateFileGoogleDrive(PARENT_ID_DIR, files):
    # Upload the files
    global drive
    file_list = listGoogleDriveDirectory(PARENT_ID_DIR)
    for gf in file_list:
        print (gf)
        for f in filesAll:
            if gf['title'] == f:
                updatedFile = drive.CreateFile({'id': gf['id']})
                updatedFile.SetContentFile(f)
                updatedFile.Upload()

def listGoogleDriveDirectory(PARENT_ID_DIR):
    global drive
    file_list = []
    gfile_list = drive.ListFile({'q': "'" + PARENT_ID_DIR + "' in parents and trashed=false"}).GetList()
    for file1 in gfile_list:
        file_list.append({'title': file1['title'], 'id': file1['id']})
    return file_list

def deleteFileGoogleDrive(files):
    global drive
    file_list = drive.ListFile({'q': "'1AhP69pOQfB5bO3kOYG9ZBv7mah1Uv_eu' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        if file1['title'] in files:
            file1.Delete()

def authGoogle():
    global drive
    # Define the credentials folder
    home_dir = os.path.expanduser(".")
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, "pydrive-credentials.json")
    
    # Start authentication
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile(credential_path)
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.CommandLineAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile(credential_path)
    drive = GoogleDrive(gauth)

def createFiles():
    # ----------- Conditions
    conditions = urlopen('http://api.wunderground.com/api/4a9d1f189cf7f2f8/geolookup/conditions/q/39.262733,-94.641335.json')
    json_string = conditions.read()
    parsed_json = json.loads(json_string)
    with open("/home/richard/www/actiontiles/weatherC.json", 'w+') as file:
        json.dump(parsed_json, file, indent=4)
    observationDateTime = parsed_json['current_observation']['observation_time_rfc822']
    observationDateTime_parsed = email.utils.parsedate(observationDateTime)
    observationDT = datetime.fromtimestamp(mktime(observationDateTime_parsed))
    # print (observationDT.strftime('%A %-I:%M %p'))
    conditions.close()

    html = "<!DOCTYPE html>\n"
    html += "<link rel=\"stylesheet\" href=\"./StyleSheet.css\">\n"
    html += "<div class=\"main-box\">\n"
    html += "<div class=\"city\">" + parsed_json['location']['city'] + ", " + parsed_json['location']['state'] + "</div>\n"
    html += "<div class=\"datetime\">" + observationDT.strftime('%a, %b %-d') + " as of " + observationDT.strftime('%-I:%M %p') + "</div>\n"

    html += "<table>\n"

    html += "\t<tr>\n"
    html += "\t\t<td class=\"temp\"><span class=\"temp\">" + str(int(round(parsed_json['current_observation']['temp_f'],0))) + "&deg;</span></td>\n"
    html += "\t\t<td class=\"icon\"><div class=\"frame\"><span class=\"helper\"></span><img src=" + parsed_json['current_observation']['icon_url'] + "></div></td>\n"
    html += "\t</tr>\n"

    html += "\t<tr>\n"
    html += "\t\t<td class=\"column-wide\" colspan=\"2\"><span class=\"dataTitle\">Wind: </span><span class=\"data\">" + parsed_json['current_observation']['wind_string'] + "</span></td>\n"
    html += "\t\t<td></td>\n"
    html += "\t</tr>\n"

    html += "\t<tr>\n"
    html += "\t\t<td class=\"column-wide\" colspan=\"2\"><span class=\"dataTitle\">Humidity: </span><span class=\"data\">" + str(parsed_json['current_observation']['relative_humidity']) + "</span></td>\n"
    html += "\t\t<td></td>\n"
    html += "\t</tr>\n"

    if (parsed_json['current_observation']['precip_today_in'] != '0.00' and parsed_json['current_observation']['precip_today_in'] != '10'):
        html += "\t<tr>\n"
        html += "\t\t<td class=\"column-wide\" colspan=\"2\"><span class=\"dataTitle\">Precip: </span><span class=\"data\">" + str(parsed_json['current_observation']['precip_today_in']) + "\"</span></td>\n"
        html += "\t\t<td></td>\n"
        html += "\t</tr>\n"
    if parsed_json['current_observation']['heat_index_f'] != 'NA':
        html += "\t<tr>\n"
        html += "\t\t<td class=\"column-wide\" colspan=\"2\"><span class=\"dataTitle\">Heat Index: </span><span class=\"data\">" + str(parsed_json['current_observation']['heat_index_f']) + "&deg;</span></td>\n"
        html += "\t\t<td></td>\n"
        html += "\t</tr>\n"
    if parsed_json['current_observation']['windchill_f'] != 'NA':
        html += "\t<tr>\n"
        html += "\t\t<td class=\"column-wide\" colspan=\"2\"><span class=\"dataTitle\">Wind Chill: </span><span class=\"data\">" + str(parsed_json['current_observation']['windchill_f']) + "&deg;</span></td>\n"
        html += "\t\t<td></td>\n"
        html += "\t</tr>\n"
    html += "</table>\n"
    # print (htm)

    with open("/home/richard/www/actiontiles/weatherC.html", mode='w+') as file:
        file.write(html)


    # ----------- Forecast
    forecast = urlopen('http://api.wunderground.com/api/4a9d1f189cf7f2f8/geolookup/forecast/q/39.262733,-94.641335.json')
    json_string = forecast.read()
    parsed_json = json.loads(json_string)
    # print (parsed_json)
    with open("/home/richard/www/actiontiles/weatherForecaset.json", 'w+') as file:
        json.dump(parsed_json, file, indent=4)

    for x in range (0, 8):
        html = "<!DOCTYPE html>\n"
        html += "<link rel=\"stylesheet\" href=\"./StyleSheet.css\">\n"
        html += "<div class=\"main-box\">\n"
        html += "\t<div class=\"box-forecast\">\n"
        html += "\t\t<img src=\"" + parsed_json['forecast']['txt_forecast']['forecastday'][x]['icon_url'] + "\" align=\"left\">\n"
        html += "\t\t<div class=\"city forecastTitle\">" + parsed_json['forecast']['txt_forecast']['forecastday'][x]['title'] + "</div>\n"
        html += "\t\t<div class=\"forecastTemp\"><span class=\"dataTitleF\">High </span><span class=\"dataF\">" + parsed_json['forecast']['simpleforecast']['forecastday'][x//2]['high']['fahrenheit'] + "&deg; / </span><span class=\"dataTitleF\">Low </span><span class=\"dataF\">" + parsed_json['forecast']['simpleforecast']['forecastday'][x//2]['low']['fahrenheit'] + "&deg;</span></div>\n"
        html += "\t\t<div class=\"forecast\"><span class=\"dataF\">" + parsed_json['forecast']['txt_forecast']['forecastday'][x]['fcttext'] + "</span></div>\n"
        if parsed_json['forecast']['txt_forecast']['forecastday'][x]['pop'] != '0':
            html += "\t\t<div class=\"forecast\"><span class=\"dataTitleF\">Precipitation Chance: </span><span class=\"dataF\">" + parsed_json['forecast']['txt_forecast']['forecastday'][x]['pop'] + "%</span></div>\n"
        html += "\t</div>\n"
        html += "</div>\n"

        with open("/home/richard/www/actiontiles/weather%s.html" % x, mode='w+') as file:
            file.write(html)

    os.system("/usr/local/bin/phantomjs /home/richard/www/actiontiles/image_weather.js")
    
if __name__ == '__main__':
    filesAll = ['weather0.png', 'weather1.png', 'weather2.png', 'weather3.png', 'weather4.png', 'weather5.png', 'weather6.png', 'weather7.png', 'weatherC.png']
    path = "/home/richard/www/actiontiles/"
    createFiles()

    PARENT_ID = "1AhP69pOQfB5bO3kOYG9ZBv7mah1Uv_eu" #Google Drive directory ID for www/actiontiles
    
    authGoogle()
    print("\nupdate files on Google Drive")
    updateFileGoogleDrive(PARENT_ID, filesAll)
