import requests
import re, os, datetime, sys
import urllib

url_base = 'https://itunesconnect.apple.com%s'
signin_url = url_base % '/WebObjects/iTunesConnect.woa'
download_csv_url = 'https://iad.apple.com/itcportal/generatecsv'

def getPublisherID(session):
    """
    publisher ID is a number that is buried deep... lets hope
    this code doesn't break often
    """
    #FIXME: doesn't work at the moment
    headers = {'Content-type': 'text/x-gwt-rpc; charset=UTF-8'}
    iad_service_url = 'https://iad.apple.com/itcportal/service/startup?requestId=GUEST_1331628761939_0__1331628761950__null'
    body = '5|0|4|https://iad.apple.com/itcportal/itcportal/|E8DB97D87973D76A7C9096DCF8A83BB5|com.qwapi.portal.itc.client.rpc.IITCStartupService|getStartupData|1|2|3|4|0|'
    r = session.post(iad_service_url, data=body, headers=headers)
    endpos = r.text.find('com.qwapi.portal.client.rpc.dto.UserDTO')
    endpos = r.text.find('"', endpos - 4)
    startpos = r.text.rfind('"', endpos - 20, endpos - 4)
    pubID = r.text[startpos + 1:endpos]
    if not int(pubID):
        raise Exception("Failed to get publisher ID")
    return pubID


def downloadiAdFiles(appleId, password, publisherId=None, outputDirectory='.', daysToDownload=14, outputFormat='iAd_D_%m-%d-%Y.txt'):
    """
    Download iAd report files.
    """
    session = requests.session()  #session used to maintain cookies etc.

    #get signin page to find url for posting signin credentials
    r = session.get(signin_url)
    match = re.search('" action="(.*)"', r.text)

    #login to ITC
    params = {'theAccountName':appleId,
            'theAccountPW':password,
            '1.Continue.x':'0',
            '1.Continue.y':'0',
            'theAuxValue':''}
    
    headers = {'Content-Length':'0',
               'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:16.0) Gecko/20100101 Firefox/16.0'}
    
    r = session.post(url_base % match.group(1), params=params, headers={})
    
    if publisherId is None:
        publisherId = getPublisherID(session)

    reportDates = [datetime.date.today() - datetime.timedelta(i + 1) for i in range(daysToDownload)]

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
            'searchTerms':'Search%20Apps',
            'adminFlag':'false',
            'fromDate':dateString,
            'toDate':dateString,
            'dataType':'byName'
        }
        
        cookieParams = {'s_sq' : 'applesuperglobal%3D%2526pid%253DiTC%252520Home%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fiad.apple.com%25252Fitcportal%2526ot%253DA',
                        's_cc' : 'true',
                        'ds01' : r.cookies['ds01'],
                        'myacinfo' : r.cookies['myacinfo']}
        
        headers = {'Cookie' : urllib.urlencode(cookieParams).replace("&", "; "),
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:16.0) Gecko/20100101 Firefox/16.0'}
        
        r = session.get(download_csv_url, params=params, headers=headers)
        
        if r.status_code != 200:
            raise Exception("Script failed to dowload - check login credentials & publisher ID")

        with open(filename, 'wb') as f:
            f.write(r.content)
        filenames.extend([filename])

    return filenames


def main():
    '''
    Test iAd reports
    '''
    argv = sys.argv[1:]
    argvLength = len(argv)

    appleId = argv[0] if argvLength > 0 else "" #provide account
    password = argv[1] if argvLength > 1 else "" #provide password
    publisherId = argv[2] if argvLength > 2 else 0 #provide publisherId
    
    downloadiAdFiles(appleId, password, publisherId)    


if __name__ == "__main__":
    main()
