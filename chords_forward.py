import requests
from lxml import html

def influx_read(address, params):
    assert isinstance(address, str)
    assert isinstance(params, dict)
    query_result = requests.get(address, params=params)
    return query_result.json()['results'][0]['series'][0]['values']

def generate_influx_query(db, measurement, conditions):
    assert isinstance(db, str)
    assert isinstance(measurement, str)
    assert isinstance(conditions, dict)
    query_string = " AND ".join(["%s='%s'" % (i, j) for
                                 i, j in conditions.items()])
    return {'db' : db, 'q' : query_string}

def generate_chords_query(domain, instrument_id, return_format='json', start=False, end=False, key=False, last=False):

    assert return_format in ['csv', 'json', 'xml', 'jsf']
    assert(any([start, end, last]))

    base_str = "http://" + domain + ".chordsrt.com/instruments/"
    start_str = ""
    end_str = ""
    key_str = ""
    last_str = ""

    if start:
        start_str = "start=%s" % start
        assert(end)
        assert(not last)
    if end:
        end_str = "end=%s" % end
        assert(start)
    if key:
        key_str = "key=%s" % key
    if last:
        last_str = "last"

    qualifiers = "&".join([i for i in [start_str, end_str, key_str, last_str]
                             if len(i) > 0])
    request_str = base_str + str(instrument_id) + '.' + return_format + '?' + qualifiers
    return request_str


def chords_write(domain, instrument_id, data, time=False, key=False, test=False):
    
    try:
        assert(isinstance(data, dict))
    except:
        raise(TypeError("Data must be 'dict' type."))

    # Generate base URL
    base_str = "http://" + domain + ".chordsrt.com/measurements/url_create?"

    # Format instrument id as part of URL string
    instrument_str = "instrument_id=%s" % instrument_id

    # Format data as part of URL string
    data_str = "&".join(["%s=%s" % (i, j) for
                          i, j in data.items()])

    # Initialize qualifiers
    time_str = ""
    key_str = ""
    test_str = ""

    if time:
        time_str = "at=%s" % time
    if key:
        key_str = "key=%s" % key
    if test:
        test_str = "test"
    qualifiers = "&".join([i for i in [time_str, key_str, test_str]
                             if len(i) > 0])

    # Put data and qualifiers in the same URL
    write_str = "&".join(i for i in [instrument_str, data_str, qualifiers]
                             if len(i) > 0)

    # Generate the final URL
    request_str = base_str + write_str
    return requests.get(request_str)


def chords_read(domain, instrument_id, username, password, return_format='json', start=False, end=False, key=False, last=False):
    base_url = "http://" + domain + ".chordsrt.com"
    sign_in_url = base_url + "/users/sign_in"

    with requests.Session() as s:
        # retrieve the login form HTML
        login_form = s.get(sign_in_url)

        # Extract the authenticity token
        dom_tree = html.fromstring(login_form.text)
        authenticity_token_element = dom_tree.xpath('//input[@name="authenticity_token"]')
        
        authenticity_token = authenticity_token_element[0].value        
        form_data = {
        'utf8': '&#x2713',
        'authenticity_token': authenticity_token,
        'user[email]': username,
        'user[password]': password,
        'user[remember_me]': '1',
        }

        # sign in, including the authenticity token
        p = s.post(sign_in_url, data=form_data)

        # Retrieve the measurement(s) for the specified instrument
        query_str = generate_chords_query(domain, instrument_id, return_format=return_format, start=start, end=end, key=key, last=last)
        result = s.get(query_str).json()
        
    return result


result = chords_read("storm", 1, "admin@chordsrt.com", "realtimedata", last=True)

data = {"batVolt" : 111, "depth" : 5000}
chords_write("storm", 1, data, key="wireless", test=True)

chords_get_last("http://storm.chordsrt.com", 1, "admin@chordsrt.com", "realtimedata")

"http://storm.chordsrt.com/instruments/1.csv?start=2015-08-01T00:30&end=2015-08-20T12:30"

"http://storm.chordsrt.com/measurements/url_create?instrument_id=1&depth=100&batVolt=108&key=wireless&test"

r = requests.get('http://ec2-54-148-229-234.us-west-2.compute.amazonaws.com:8086/query', params={'db' : 'poseidon', 'q' : "SELECT value FROM depth_sonic WHERE node_id='9'"})

data = r.json()['results'][0]['series'][0]['values']

# curl -v -G 'http://ec2-54-148-229-234.us-west-2.compute.amazonaws.com:8086/query?pretty=true' --data-urlencode "db=poseidon" --data-urlencode "q=SELECT value FROM depth_sonic WHERE node_id='9'"
