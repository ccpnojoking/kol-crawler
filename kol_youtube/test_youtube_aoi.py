import json
import requests


def test_youtube_api():
    apis = [
        "AIzaSyDUqtjrvlmmuS5ynb_mFialzNFit89JdBM",
        "AIzaSyCjc9lZDKu7KxQaqgoF2eqShQWsIr8aruI",
        "AIzaSyAH7bYKXY0KmWBLblYjYYcjuDg91NVuL1I",
        "AIzaSyCUSlVilWw1GVAKUXTVAQr-vCf1a8tQwsU",
        "AIzaSyACnJ5TjtUE7gWIYmEpSs9xt9PlyXYYako",
        "AIzaSyDO9spLUdafSe-tLjY6RjppcdzFarSM6Zk",
        "AIzaSyDJdznkFzUkW41p_K5EJqScnikpH9EQSD0",
        "AIzaSyCGPuDqzGq5j_pP_kliywd-zSCnpC4puAI",
        "AIzaSyCWRDohhr4ow1MvGgy2NFuM_GJ9bxfgFas",
        "AIzaSyC0oHDBJb5wxNIx6e-XsjblS5zWdQ395ZM",
        "AIzaSyDiPhcFymcwM30NyukT-YYAW55yuptDAJE",
        "AIzaSyAN7CPntkEHF5YhsR9N5wJih-4SfLhtyyU",
        "AIzaSyBm2dBwrttgNaxFuL_jXBDx-pfWHuHocNs",
        "AIzaSyDuyL9eWssTE09jqt9VRlDq4bIWgjl-EAI",
        "AIzaSyBH2RR7TTilBtCgSU6coH_n-KauU8qeWhc",
        "AIzaSyCM4BE3nvEwbS26k553vOqbRhZtUr_NCAs",
        "AIzaSyD5VC1UUbazvbpoy9eq5xHum58Mlik9_6Q",
        "AIzaSyBqR5MoSfmzGkt_1Z4lBxP4FN_Q5BVEJIU",
        "AIzaSyDK2iUC24KDOXAG5PM3F4GpYkVGNI9uhiI",
        "AIzaSyCB1-Re3r4GrvDFM5OU1Cslq50-oxWsULY",
        "AIzaSyB0fvGFIkvGIZkfH803QOFhQT-eSZjrNKE",
        "AIzaSyAahlFk-jLHz3j6iJUpy1nJQBhPxVCwQyQ",
        "AIzaSyDHeKGmD2mkdtxwuljBDUScOP4vn4xTElk",
        "AIzaSyAxjn9g1bKeSb20l5JBVn23F0IW4Pclo7A",
        "AIzaSyAwcDh_6bgEzhV0pCKYRs_DYbxxuG6WyaE",
        "AIzaSyCrCzyjbMxwn_SE-jsiF-RyCsPnfHZj6Ps",
        "AIzaSyAksV-sKIfFo2vGVFjU14woN0Sa5MxUCFM",
        "AIzaSyB5gZy0wt6fH9GBzKUlLCNUyg5rFbVjlPo",
        "AIzaSyDoJOE-lpaERn1laftEjoJT5O-j3spa3Zs",
        "AIzaSyCFH1mAEIKR3cht72JDCOi0N4vonztrjuQ",
        "AIzaSyCGApgPulTJWAsk4-n8LO18nWY9luB65zI",
        "AIzaSyAKsbjL4USQhXIDQNxqMqk7cCeg401iM9s",
        "AIzaSyDNKDBE_Ny6geqgORVjioCO1Qjv8MhQaak",
        "AIzaSyCJneZa4TwtGsBRfPufg489JjDc1jxKg5A",
        "AIzaSyB2iNdkKhTGxZp6OEhpWOk--vD4d2-0rdI",
        "AIzaSyCSESAhlao988Oy7wXHxL7UVMtxoTywjxc",
        "AIzaSyCDL89jM0G-xlOKrjZwX_-0QojkrPk7L38",
        "AIzaSyC2p26iUgHgw_sGq0PsDKN-Scr6NQ0b47k",
        "AIzaSyBVEXTm1AXZF_wH4ab2N7Fbs_JC_LyUvDI"
    ]
    api_newest = [
        # ballarabella549@gmail.com	0Tv1bdpZo9
        'AIzaSyBqR5MoSfmzGkt_1Z4lBxP4FN_Q5BVEJIU',  # cccp
        'AIzaSyDK2iUC24KDOXAG5PM3F4GpYkVGNI9uhiI',  # My Project 60328

        # janeconnor536@gmail.com	gkTZT6BXWX
        'AIzaSyAwcDh_6bgEzhV0pCKYRs_DYbxxuG6WyaE',  # My Project 85361
        'AIzaSyCM4BE3nvEwbS26k553vOqbRhZtUr_NCAs',  # My Project 29052

        # hodgeopal25@gmail.com	XqkC56qhCR
        'AIzaSyDO9spLUdafSe-tLjY6RjppcdzFarSM6Zk',  # My Project 13292
        'AIzaSyCGApgPulTJWAsk4-n8LO18nWY9luB65zI',  # My Project 36552

        # marywarner3242@gmail.com	WpAM8deUxW
        'AIzaSyDiPhcFymcwM30NyukT-YYAW55yuptDAJE',  # My Project 12090
        'AIzaSyAxjn9g1bKeSb20l5JBVn23F0IW4Pclo7A',  # My Project 19477

        # chapmanimogene19@gmail.com	d2NU0gkYij
        'AIzaSyCjc9lZDKu7KxQaqgoF2eqShQWsIr8aruI',  # My Project 75069
        'AIzaSyCGPuDqzGq5j_pP_kliywd-zSCnpC4puAI',  # My Project 79844

        # babenklfred@gmail.com	oabpjhei
        'AIzaSyBH2RR7TTilBtCgSU6coH_n-KauU8qeWhc',  # My Project 99216
        'AIzaSyCrCzyjbMxwn_SE-jsiF-RyCsPnfHZj6Ps',  # My Project 42607

        # lavrentiizhebov1998@gmail.com	sgg2pu7o
        'AIzaSyCJneZa4TwtGsBRfPufg489JjDc1jxKg5A',  # My Project 29927
        'AIzaSyCFH1mAEIKR3cht72JDCOi0N4vonztrjuQ',  # My Project 46795

        # stepaenovvelor@gmail.com	fhfce775
        'AIzaSyACnJ5TjtUE7gWIYmEpSs9xt9PlyXYYako',  # My Project 9250
        'AIzaSyB2iNdkKhTGxZp6OEhpWOk--vD4d2-0rdI',  # My Project 56031

        # krrasnomiiasovlyubomir@gmail.com 	ykgawvjn5
        'AIzaSyBm2dBwrttgNaxFuL_jXBDx-pfWHuHocNs',  # My Project 4198
        'AIzaSyCDL89jM0G-xlOKrjZwX_-0QojkrPk7L38',  # My Project 19220

        # zhidooovichviktorin@gmail.com	wjsvbygwe
        'AIzaSyB5gZy0wt6fH9GBzKUlLCNUyg5rFbVjlPo',  # My Project 22822
        'AIzaSyDJdznkFzUkW41p_K5EJqScnikpH9EQSD0',  # My Project 42393

        # willielus@gmail.com	gmailwillieLU
        'AIzaSyCWRDohhr4ow1MvGgy2NFuM_GJ9bxfgFas',  # My Project 62222
        'AIzaSyAH7bYKXY0KmWBLblYjYYcjuDg91NVuL1I',  # My Project 22856

        # kysaqujnxvz@gmail.com	gma68ytty
        'AIzaSyC0oHDBJb5wxNIx6e-XsjblS5zWdQ395ZM',  # My Project 29028
        'AIzaSyAKsbjL4USQhXIDQNxqMqk7cCeg401iM9s',  # My Project 10403

        # nicole.heazel@gmail.com	gmailwillieLU
        'AIzaSyD5VC1UUbazvbpoy9eq5xHum58Mlik9_6Q',  # My Project 3662
        'AIzaSyAahlFk-jLHz3j6iJUpy1nJQBhPxVCwQyQ',  # My Project 2513

        # thea.g.buzzbreak@gmail.com	theabuzzbreakGMAIL.
        'AIzaSyCSESAhlao988Oy7wXHxL7UVMtxoTywjxc',  # My Project 9805
        'AIzaSyC2p26iUgHgw_sGq0PsDKN-Scr6NQ0b47k',  # My Project 12849

        # vickywilsonvv@gmail.com	Zhaoziyi0309
        'AIzaSyDUqtjrvlmmuS5ynb_mFialzNFit89JdBM',  # My Project 84114
        'AIzaSyCUSlVilWw1GVAKUXTVAQr-vCf1a8tQwsU',  # My Project 65202

        # vivecawww@gmail.com	zhaoziyi0309
        'AIzaSyAN7CPntkEHF5YhsR9N5wJih-4SfLhtyyU',  # My Project 36460

        # zombiezoe716@gmail.com	zoezoe716
        'AIzaSyDuyL9eWssTE09jqt9VRlDq4bIWgjl-EAI',  # My Project 17663

        # kikiklein678@gmail.com	kiki678@
        'AIzaSyDHeKGmD2mkdtxwuljBDUScOP4vn4xTElk',  # My Project 39415
    ]
    '''
    Account	                                    pwd
    ballarabella549@gmail.com	                0Tv1bdpZo9
    AIzaSyBqR5MoSfmzGkt_1Z4lBxP4FN_Q5BVEJIU     cccp
    AIzaSyDK2iUC24KDOXAG5PM3F4GpYkVGNI9uhiI     My Project 60328


    janeconnor536@gmail.com	                    gkTZT6BXWX
    AIzaSyAwcDh_6bgEzhV0pCKYRs_DYbxxuG6WyaE     My Project 85361
    AIzaSyCM4BE3nvEwbS26k553vOqbRhZtUr_NCAs     My Project 29052


    hodgeopal25@gmail.com	                    XqkC56qhCR
    AIzaSyDO9spLUdafSe-tLjY6RjppcdzFarSM6Zk     My Project 13292
    AIzaSyCGApgPulTJWAsk4-n8LO18nWY9luB65zI     My Project 36552


    marywarner3242@gmail.com	                WpAM8deUxW
    AIzaSyDiPhcFymcwM30NyukT-YYAW55yuptDAJE     My Project 12090
    AIzaSyAxjn9g1bKeSb20l5JBVn23F0IW4Pclo7A     My Project 19477


    chapmanimogene19@gmail.com	                d2NU0gkYij
    AIzaSyCjc9lZDKu7KxQaqgoF2eqShQWsIr8aruI     My Project 75069
    AIzaSyCGPuDqzGq5j_pP_kliywd-zSCnpC4puAI     My Project 79844


    babenklfred@gmail.com	                    oabpjhei
    AIzaSyBH2RR7TTilBtCgSU6coH_n-KauU8qeWhc     My Project 99216
    AIzaSyCrCzyjbMxwn_SE-jsiF-RyCsPnfHZj6Ps     My Project 42607


    lavrentiizhebov1998@gmail.com               sgg2pu7o
    AIzaSyCJneZa4TwtGsBRfPufg489JjDc1jxKg5A     My Project 29927
    AIzaSyCFH1mAEIKR3cht72JDCOi0N4vonztrjuQ     My Project 46795


    stepaenovvelor@gmail.com	                fhfce775
    AIzaSyACnJ5TjtUE7gWIYmEpSs9xt9PlyXYYako     My Project 9250
    AIzaSyB2iNdkKhTGxZp6OEhpWOk--vD4d2-0rdI     My Project 56031


    krrasnomiiasovlyubomir@gmail.com            ykgawvjn5
    AIzaSyBm2dBwrttgNaxFuL_jXBDx-pfWHuHocNs     My Project 4198
    AIzaSyCDL89jM0G-xlOKrjZwX_-0QojkrPk7L38     My Project 19220


    zhidooovichviktorin@gmail.com               wjsvbygwe
    AIzaSyB5gZy0wt6fH9GBzKUlLCNUyg5rFbVjlPo     My Project 22822
    AIzaSyDJdznkFzUkW41p_K5EJqScnikpH9EQSD0     My Project 42393


    willielus@gmail.com	                        gmailwillieLU
    AIzaSyCWRDohhr4ow1MvGgy2NFuM_GJ9bxfgFas,    My Project 62222
    AIzaSyAH7bYKXY0KmWBLblYjYYcjuDg91NVuL1I,    My Project 22856


    kysaqujnxvz@gmail.com	                    gma68ytty
    AIzaSyC0oHDBJb5wxNIx6e-XsjblS5zWdQ395ZM     My Project 29028
    AIzaSyAKsbjL4USQhXIDQNxqMqk7cCeg401iM9s     My Project 10403


    nicole.heazel@gmail.com	                    gmailwillieLU
    AIzaSyD5VC1UUbazvbpoy9eq5xHum58Mlik9_6Q     My Project 3662
    AIzaSyAahlFk-jLHz3j6iJUpy1nJQBhPxVCwQyQ     My Project 2513


    thea.g.buzzbreak@gmail.com	                theabuzzbreakGMAIL.
    AIzaSyCSESAhlao988Oy7wXHxL7UVMtxoTywjxc     My Project 9805
    AIzaSyC2p26iUgHgw_sGq0PsDKN-Scr6NQ0b47k     My Project 12849


    vickywilsonvv@gmail.com	                    Zhaoziyi0309
    AIzaSyDUqtjrvlmmuS5ynb_mFialzNFit89JdBM     My Project 84114
    AIzaSyCUSlVilWw1GVAKUXTVAQr-vCf1a8tQwsU     My Project 65202


    vivecawww@gmail.com	                        zhaoziyi0309
    AIzaSyAN7CPntkEHF5YhsR9N5wJih-4SfLhtyyU     My Project 36460


    zombiezoe716@gmail.com	                    zoezoe716
    AIzaSyDuyL9eWssTE09jqt9VRlDq4bIWgjl-EAI     My Project 17663


    kikiklein678@gmail.com	                    kiki678@
    AIzaSyDHeKGmD2mkdtxwuljBDUScOP4vn4xTElk     My Project 39415

    mcguirreclayyton@gmail.com                  rjoea5oi
    AIzaSyCegCBIgH3vYyQ6Z0oRefyXQQ99jUZl-v8     My Project 79654

    '''
    for i in apis:
        try:
            video_info_url = 'https://www.googleapis.com/youtube/v3/videos' \
                             '?' \
                             'id={}' \
                             '&' \
                             'key={}' \
                             '&' \
                             'fields=items(snippet(channelTitle,channelId),contentDetails(duration))' \
                             '&' \
                             'part=snippet,contentDetails'.format('DfG6VKnjrVw', i)  # 5
            video_info = json.loads(requests.get(video_info_url).content.decode())
            user_name = video_info['items'][0]['snippet']['channelTitle']
            channelId = video_info['items'][0]['snippet']['channelId']
            duration = video_info['items'][0]['contentDetails']['duration']
            print('success: ', i, user_name, channelId, duration)
            # home_info_url = 'https://www.googleapis.com/youtube/v3/channels' \
            #                 '?' \
            #                 'id={}' \
            #                 '&' \
            #                 'key={}' \
            #                 '&' \
            #                 'fields=items(contentDetails(relatedPlaylists(uploads)))' \
            #                 '&' \
            #                 'part=snippet,contentDetails,statistics'.format(channelId, i)
            # home_info = json.loads(requests.get(home_info_url).content.decode())
            # uploads_id = home_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            # print('success', uploads_id)
            # uploads_info_url = 'https://www.googleapis.com/youtube/v3/playlistItems' \
            #                    '?' \
            #                    'playlistId={}' \
            #                    '&' \
            #                    'key={}' \
            #                    '&' \
            #                    'fields=items(snippet(resourceId(videoId)))' \
            #                    '&' \
            #                    'part=snippet' \
            #                    '&' \
            #                    'maxResults=50'.format(uploads_id, i)
            # uploads_info = json.loads(requests.get(uploads_info_url).content.decode())
            # uploads_video_id = [i['snippet']['resourceId']['videoId'] for i in uploads_info['items']]
            # print('success', uploads_video_id)
        except Exception as e:
            print('error', i, e)


def test_job(youtube_key):
    video_info_url = 'https://www.googleapis.com/youtube/v3/videos' \
                     '?' \
                     'id={}' \
                     '&' \
                     'key={}' \
                     '&' \
                     'fields=items(snippet(channelTitle,channelId),contentDetails(duration))' \
                     '&' \
                     'part=snippet,contentDetails'.format('DfG6VKnjrVw', youtube_key)
    print(requests.get(video_info_url).json())

'AIzaSyDBj1U8vzMxS-JWbwFfja-dsmiQ0Sjqtr8'
test_job('AIzaSyDBj1U8vzMxS-JWbwFfja-dsmiQ0Sjqtr8')
