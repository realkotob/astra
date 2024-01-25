import sys
import os
import time
from datetime import datetime
import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
from src.astra import Astra  # noqa: E402

obs = None


# startup (should be separated)
    # queue_get() thread
    # create_db()
    # __log()
    # read_config()
    # read_schedule()
    # load_devices()

def test_startup():
    '''
    Tests initialising Astra Object
    '''
    global obs 
    try:
        obs = Astra('/Users/peter/Github/astra/code/config/Callisto.yml')
        time.sleep(0.1) # to permit sqlworker to catchup
        ## TODO: descript property denoting initialisation
        assert True
    except Exception as e:
        raise e

def test_queue_get():
    '''
    Queue thread test
    '''

    # find queue thread in obs.threads array
    queue_get_thread = None
    count = 0
    for i in obs.threads:
        if i['type'] == 'queue':
            count += 1
            queue_get_thread = i['thread']
    
    # check only one queue thread
    assert count == 1
    # check if alive
    assert queue_get_thread.is_alive() is True

def test_create_db():
    '''
    Test db creation
    '''

    rows = obs.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    assert rows == [('polling',), ('images',), ('log',), ('autoguider_ref',), ('autoguider_log_new',), ('autoguider_info_log',), ('sqlite_sequence',)]

def test_log():
    '''
    Testing Astra's internal logger
    '''

    rows = obs.cursor.execute("SELECT * FROM log ORDER BY datetime DESC LIMIT 1;")

    dt = rows[0][0]
    # check last log in previous 1s
    assert (datetime.utcnow() - pd.to_datetime(dt)).total_seconds() < 1

    # check message is "Astra initialized"
    assert rows[0][2] == "Astra initialized"

def test_queue():
    '''
    Test queue after db creation
    '''

    obs.queue.put(({}, {"type" : "log", "data" : ('debug', 'Testing queue')}))
    
    start_time = time.time()
    while obs.queue.empty() is False:
        if time.time() - start_time > 1: # 1 seconds
            raise TimeoutError('queue_get timed out')
    
    # should return empty if queue_get thread is working
    assert obs.queue.empty() is True

def test_read_config():
    '''
    Tests reading the config file
    '''
    # TODO: more thorough test
    assert len(obs.observatory) > 0
    assert obs.error_free is True

def test_read_schedule():
    '''
    Tests reading the config file
    '''
    # TODO: more thorough test
    assert isinstance(obs.schedule, pd.DataFrame)
    assert obs.error_free is True

def test_load_devices():
    '''
    Tests loading devices
    '''
    # TODO: more thorough test
    assert isinstance(obs.devices, dict)
    assert obs.error_free is True

# connect_all()
    # test device polling
    # start_watchdog() TODO: Move out of connect all

@pytest.mark.timeout(10)
def test_connect_all():
    '''
    Tests connect all.
    '''
    obs.connect_all()

    # TODO: more thorough test
    assert obs.error_free is True

def test_polling():
    '''
    Test that a device is begun polling
    '''

    polled_list = {}

    for device_type in obs.devices:
        
        polled_list[device_type] = {}

        for device_name in obs.devices[device_type]:
            
            polled_list[device_type][device_name] = {}

            polled = obs.devices[device_type][device_name].poll_latest()

            assert polled is not None

            polled_keys = polled.keys()

            assert len(polled_keys) > 0

            for k in polled_keys:

                polled_list[device_type][device_name][k] = {}
                polled_list[device_type][device_name][k]['value'] = polled[k]['value']
                polled_list[device_type][device_name][k]['datetime'] = polled[k]['datetime']

                assert (datetime.utcnow() - polled[k]['datetime']).total_seconds() < 5

def test_start_watchdog():
    '''
    Testing start_watchdog, which was started by connect_all.
    '''
    # find watchdog thread in obs.threads array
    watchdog_thread = None
    count = 0
    for i in obs.threads:
        if i['type'] == 'watchdog':
            count += 1
            watchdog_thread = i['thread']
    
    # check only one watchdog thread
    assert count == 1
    # check if alive
    assert watchdog_thread.is_alive() is True

# def test_watchdog():
    # different scenerios
    
# open_observatory()
    
def test_open_observatory():
    '''
    Test open observatory
    '''

    # open without paired_devices
    obs.open_observatory()

    # open with paired_devices
    paired_devices = obs.observatory['Camera'][0]['paired_devices']
    obs.open_observatory(paired_devices)


    # NEED to make speculoos specific true flag based.

    assert True



# close_observatory()

# start_schedule()

# cool_camera()

# pre_sequence()

# setup_observatory()

# object_sequence()

# flats_sequence()

# calibration_sequence()

# monitor_action()


# image saving, guiding?, should be in seperate tests.

