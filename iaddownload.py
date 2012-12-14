import requests
import re, os, datetime

url_base = 'https://itunesconnect.apple.com%s'
signin_url = url_base % '/WebObjects/iTunesConnect.woa'
download_csv_url = 'https://iad.apple.com/itcportal/generatecsv'

def getPublisherID(session):
    """
    publisher ID is a number that is buried deep... lets hope
    this code doesn't break often
    """
    headers = {'Content-type': 'text/x-gwt-rpc; charset=UTF-8'}
    iad_service_url= 'https://iad.apple.com/itcportal/service/startup?requestId=GUEST_1331628761939_0__1331628761950__null'
    body = '5|0|4|https://iad.apple.com/itcportal/itcportal/|E8DB97D87973D76A7C9096DCF8A83BB5|com.qwapi.portal.itc.client.rpc.IITCStartupService|getStartupData|1|2|3|4|0|'
    r = session.post(iad_service_url, data=body, headers=headers)
    endpos = r.text.find('com.qwapi.portal.client.rpc.dto.UserDTO')
    endpos = r.text.find('"', endpos-4)
    startpos = r.text.rfind('"', endpos-20, endpos-4)
    pubID = r.text[startpos+1:endpos]
    if not int(pubID):
        raise Exception("Failed to get publisher ID")
    return pubID


def downloadiAdFiles(appleId, password, publisherId=None, outputDirectory='.', daysToDownload=14, outputFormat='iAd_D_%m-%d-%Y.txt'):

    session = requests.session()  #session used to maintain cookies etc.

    #get signin page to find url for posting signin credentials
    r = session.get(signin_url)
    match = re.search('" action="(.*)"', r.text)

    #login to ITC
    params = {'theAccountName':appleId,
            'theAccountPW':password,
            '1.Continue.x':'10',
            '1.Continue.y':'10',
            'theAuxValue':''}
    r = session.post(url_base % match.group(1), params=params, headers={'Content-Length':'0'})
    r = session.get('https://iad.apple.com/itcportal')

    if publisherId is None:
        publisherId = getPublisherID(session)

    reportDates = [datetime.date.today() - datetime.timedelta(i + 1 ) for i in range(daysToDownload)]

    filenames = []
    for downloadReportDate in reportDates:
        filename = os.path.join(outputDirectory, downloadReportDate.strftime(outputFormat))
        if (os.path.exists(filename)):
            continue

        dateString = downloadReportDate.strftime('%m/%d/%Y')
        params = {'pageName': 'app_homepage',
            'dashboardType':'publisher',
            'publisherId':publisherId,
            'dateRange':'customDateRange',
            'searchTerms':'Search Apps',
            'adminFlag':'false',
            'fromDate':dateString,
            'toDate':dateString,
            'dataType':'byName'
        }
        r = session.get(download_csv_url, params=params)
        if r.status_code != 200:
            raise Exception("Script failed to dowload - check login credentials & publisher ID")

        with open(filename, 'wb') as f:
            f.write(r.content)
        filenames.extend([filename])

    return filenames

