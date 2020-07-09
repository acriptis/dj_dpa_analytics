################# Universal Import ###################################################
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# PREROOT_DIR = os.path.dirname(ROOT_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_dpa_analytics.settings")
import django
django.setup()
# #####################################################
from copy import copy
import datetime as dt
from dialogs.models import Dialog, Utterance, Annotation, UtteranceHypothesis, Author
import json
import urllib.request
import logging
logger = logging.getLogger(__name__)
import pytz
import math

class DPADumper():
    """
    Class for dumping the staf from DP-Agent DB into analytical tool
    """
    def __init__(self, dpa_base_url):
        self.dpa_base_url = dpa_base_url


    def request_api_page_for_dialogs_list(self, offset=0, limit=100, url_suffix=None,
                                          timeout=15):
        """
        Requests list of recent dialogs
        :param url_suffix: string with page suffix. Ex.: "?offset=30&limit=30"
            if None then request is from offset and limit args
        :param offset: int, how many dialogs to skip

        :param timeout: seconds of timeout for waiting

        :return: dict with dialog_list_ids and next page url. Ex.:
        {
            "dialog_ids": ["5edfaf8a4d595032bf2e7aed", "5ee0a8b3931df828d12362eb",
                "5ee0d5bc4ceff4226ebedd63", "5ee1003c287f6c1327d56a07", "5ee6435afa53109f5c6c8c39",
                "5ee73cb12334f458eb1109ea", "5ee746b8d9bbd35cdd614281", "5ee74be8b359fad8dbaac1ff",
                "5ee74c249dd442dfc2fc637d", "5ee77ab88b9fc0d06ac76d50", "5ee77bfc8b9fc0d06ac76d55",
                "5ee78ceb82d52fa04922bbc3", "5ee79326c28d00fa17666953", "5ee797fc14a371f5e3922915",
                "5ee79867d6c588e1566571a5", "5ee8d221d6c588e1566571aa", "5ee8d272d6c588e1566571af",
                "5ee8d80fd6c588e1566571b4", "5ee94b8ad6c588e1566571d7", "5ee94be5d6c588e1566571dc",
                "5ee94d9cd6c588e1566571e6", "5ee9c7e2d6c588e1566571eb", "5ee9cc7cd6c588e156657202",
                "5eea07e6d6c588e156657263", "5eea3e16d6c588e15665726c", "5eea6bffd6c588e156657275",
                "5eea6d6ad6c588e15665727a", "5eea6eefd6c588e156657294", "5eea71b3d6c588e1566572a4",
                "5eea782fd6c588e1566572a9"],
            "next": "?offset=30&limit=30"}

        """

        url_to_dialogs = "%s/api/dialogs/" % (self.dpa_base_url)

        if url_suffix:
            final_url = url_to_dialogs + url_suffix
        else:
            params = {
                "offset": offset,
                "limit": limit,
                # for dumping finished dialogs only:
                "_active": 0
            }

            url_suffix = urllib.parse.urlencode(params)
            final_url = url_to_dialogs + "?" + url_suffix

        print(f"requesting DP_Agent API: {final_url}...")
        with urllib.request.urlopen(final_url, timeout=timeout) as url:
            remote_data = json.loads(url.read().decode())

        return remote_data

    def request_api_for_dialog(self, dp_dialog_id, timeout=15, sleep=10, max_retries=10):
        """
        Requests specific dialog details from DP-Agent
        :param dp_dialog_id:
        :param timeout: seconds of timeout for waiting
        :param sleep: allows to retry request after some sleeping
        :param max_retries: number of failed attempts to request
        :return: serialized dict with dp_agent.Dialog representation
        """

        url_to_dialog = "%s/api/dialogs/%s" % (self.dpa_base_url, dp_dialog_id)
        print(f"requesting DP_Agent API: {url_to_dialog}...")
        with urllib.request.urlopen(url_to_dialog, timeout=timeout) as url:
            remote_data = json.loads(url.read().decode())

        return remote_data

def _parse_time_of_dp_agent(time_str: str):
    try:
        time = dt.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        time = dt.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    return time

def dump_new_dialogs(dpagent_base_url):

    dpad = DPADumper(dpa_base_url=dpagent_base_url)

    page_suffix = "?limit=5"

    while page_suffix is not None:
        # TODO make DP-Agent to return new dialogs first
        ######################################################################
        # request dp_agent api for list of dialogs
        results = dpad.request_api_page_for_dialogs_list(url_suffix=page_suffix)
        # parse results:
        if results:
            page_suffix =results['next']
            dialog_ids = results['dialog_ids']
            for each_dialog_id in dialog_ids:

                try:
                    dialog_obj = Dialog.objects.get(dp_id=each_dialog_id)

                except Exception as e:
                    # dialog creation routine
                    print(e)

                    # ##### create ###########################################
                    # request api for viewing dialogs
                    remote_data = dpad.request_api_for_dialog(each_dialog_id)

                    # get or create authors
                    author_h, _ = Author.objects.get_or_create(
                        user_type='human',
                        dp_id=remote_data['human']['id']
                    )

                    author_b, _ = Author.objects.get_or_create(
                        user_type='bot')

                    ##############################################################################
                    # Start data creation:
                    dp_id = remote_data['dialog_id']
                    parsed_dt = _parse_time_of_dp_agent(remote_data['date_start'])
                    # parsed_dt = pytz.utc.localize(each_dialog_row['first_utt_time'])
                    dialog = Dialog.objects.create(
                        conversation_id=dp_id,
                        start_time=parsed_dt,
                        dp_id=dp_id,
                        # rating=rating,
                        human=author_h,
                        bot=author_b
                    )
                    # for utt_idx, each_utterance in enumerate(dialog_dict['utterances']):
                    # import ipdb; ipdb.set_trace()

                    for utt_idx, each_utterance in enumerate(remote_data['utterances']):
                        # is_human = utt_idx % 2 == 0
                        version = None
                        if 'user' in each_utterance:
                            if each_utterance['user']['user_type'] == "bot":
                                author = author_b
                                active_skill = each_utterance['active_skill']
                                version = None
                            elif each_utterance['user']['user_type'] == "human":
                                author = author_h
                                active_skill = "human"
                                try:
                                    version = each_utterance['attributes']['version']
                                except Exception as e:
                                    print(e)
                                    print("we have problems in extracting the version! Skipping!")
                            else:
                                print("Unknown error with detection of typo of author!")
                                import ipdb;
                                ipdb.set_trace()
                                # self destruct to avoid corruptedf dialogs:
                                dialog.delete()
                                return
                        else:
                            raise Exception("No user attr in utterance!")

                        # we use create to write duplicated utterance in one dialog separately
                        # TODO annotate with timestamp
                        # parse datetime... dp_agent has two formats...
                        try:
                            parsed_dt = dt.datetime.strptime(each_utterance['date_time'],
                                                             "%Y-%m-%d %H:%M:%S.%f")
                        except Exception as e:
                            parsed_dt = dt.datetime.strptime(each_utterance['date_time'],
                                                             "%Y-%m-%d %H:%M:%S")
                        parsed_dt = pytz.utc.localize(parsed_dt)

                        utt = Utterance.objects.create(
                            text=each_utterance['text'],
                            parent_dialog=dialog,
                            author=author,
                            timestamp=parsed_dt,
                            active_skill=active_skill,
                            version=version
                        )

                        # ANNOTATIONS:
                        # import ipdb; ipdb.set_trace()
                        try:
                            for each_anno_key, each_anno_dict in remote_data['utterances'][utt_idx][
                                'annotations'].items():
                                # anno, _ = Annotation.objects.get_or_create(
                                anno = Annotation.objects.create(
                                    parent_utterance=utt,
                                    annotation_type=each_anno_key,
                                    annotation_dict=each_anno_dict
                                )
                        except Exception as e:
                            print(e)
                            import ipdb;
                            ipdb.set_trace()
                            print("Investigate")

                        # HYPOTHESES:
                        if 'hypotheses' in remote_data['utterances'][utt_idx]:
                            for each_hypo in remote_data['utterances'][utt_idx]['hypotheses']:

                                # lets add dictionary with extra attributes from skills:
                                other_attrs = copy(each_hypo)
                                del other_attrs['skill_name']
                                del other_attrs['text']
                                del other_attrs['confidence']
                                try:
                                    # anno, _ = UtteranceHypothesis.objects.get_or_create(
                                    anno = UtteranceHypothesis.objects.create(
                                        parent_utterance=utt,
                                        skill_name=each_hypo['skill_name'],
                                        text=each_hypo['text'],
                                        confidence=each_hypo['confidence'],
                                        other_attrs=other_attrs
                                    )
                                except Exception as e:
                                    print(e)
                                    import ipdb;
                                    ipdb.set_trace()
                                    print("Investigate")

                    logger.info(f'Successfully added a new conversation {dp_id} to local DB.')

            # find dialog ids that are missed
        else:
            logger.warning("No dialogs in DP-Agent!")
        print(results)


if __name__=="__main__":
    # get list of dialogs:
    from django.conf import settings
    dump_new_dialogs(dpagent_base_url=settings.DP_AGENT_BASE_URL)
