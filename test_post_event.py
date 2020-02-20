import requests

def _url(path):
    return 'http://0.0.0.0:5000' + path

def postEvent( in_out, dateandtime):
    data = {'time_stamp': dateandtime, 'event': in_out}
    r = requests.get(url=_url('/get_event/1' + '/' + in_out + '/' + dateandtime))
    return r.status_code, r.text

postEvent('in', '2020-02-08 00:05:26')
postEvent('out', '2020-02-08 00:31:26')

# postEvent('in', '2020-02-08 02:51:26')
# postEvent('out', '2020-02-08 02:19:26')
#
# postEvent('in', '2020-02-08 03:51:26')
# postEvent('out', '2020-02-08 03:19:26')
#
# postEvent('in', '2020-02-08 05:51:26')
# postEvent('out', '2020-02-08 05:19:26')
#
# postEvent('in', '2020-02-08 08:51:26')
# postEvent('out', '2020-02-08 08:19:26')
#
# postEvent('in', '2020-02-08 10:51:26')
# postEvent('out', '2020-02-08 10:19:26')
#
# postEvent('in', '2020-02-08 12:51:26')
# postEvent('out', '2020-02-08 12:19:26')
#
# postEvent('in', '2020-02-08 23:51:26')
# postEvent('out', '2020-02-08 23:19:26')