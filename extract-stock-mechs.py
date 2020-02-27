import os
import shutil
import json
import re
from collections import Iterable
from itertools import chain

from json import JSONDecodeError


def add_missing_commas(content):
    content = content.replace('"}', '",}')
    return content


def cauterize_json(string):
    string = re.sub(",[ \t\r\n]+}", "}", string)
    string = re.sub(",[ \t\r\n]+\]", "]", string)
    # string = add_missing_commas(string)
    return string


def do_a_thing(directory, mechs, flashpoints, contracts, lancedefs):
    # Grab all mechs, flashpoints, associated contracts...
    for root, dirs, files in os.walk(directory):
        for file in files:

            if not file.endswith('.json') \
                    or r'conversation' in root:
                continue

            file_location = os.path.join(root, file)
            with open(file_location) as fd:
                if r'mechdef' in file.lower():
                    try:
                        mech = json.loads(cauterize_json(fd.read()))
                        id = mech['Description']['Id']
                        tags = set(mech['MechTags']['items'])
                    except JSONDecodeError as error:
                        print(f'[{file_location}] - [{error}]')
                        raise

                    mechs.append((id, file, file_location, tags))

                if r'flashpoints' in root and r'contracts' not in root:
                    flashPoints.append(os.path.join(root, file))

                if r'flashpoint' in root and r'contracts' in root:
                    try:
                        contract = json.loads(cauterize_json(fd.read()))
                        id = contract['ID']
                    except JSONDecodeError as error:
                        print(f'[{file_location}] - [{error}]')
                        raise

                    mechOverrides = []

                    lanceOverrides = [lanceOverride for lanceOverride in contract['targetTeam']['lanceOverrideList']]
                    lanceOverrides += [lanceOverride for lanceOverride in contract['player1Team']['lanceOverrideList']]

                    for lanceOverride in lanceOverrides:
                        for unitSpawnPointOverride in lanceOverride['unitSpawnPointOverrideList']:
                            unitDefId = unitSpawnPointOverride['unitDefId']
                            if \
                                    r'inherit' not in unitDefId.lower() and \
                                            r'turret' not in unitDefId.lower() and \
                                            r'vehicle' not in unitDefId.lower() and \
                                            unitDefId not in ['Tagged', 'mechDef_None', 'UseLance', '']:
                                mechOverrides.append(unitDefId)

                    contracts.append((id, file, file_location, mechOverrides))

                if r'lancedef' in file.lower():
                    try:
                        lance = json.loads(cauterize_json(fd.read()))
                        id = lance['Description']['Id']
                        mechsDefs = [unit['unitId'] for unit in lance['LanceUnits'] if unit['unitType'] == 'Mech' and unit['unitId'] != 'Tagged']
                        req_tags = set(list(chain.from_iterable([unit['unitTagSet']['items'] for unit in lance['LanceUnits'] if unit['unitType'] == 'Mech' and unit['unitId'] == 'Tagged'])))
                        res_tags = set(list(chain.from_iterable([unit['excludedUnitTagSet']['items'] for unit in lance['LanceUnits'] if unit['unitType'] == 'Mech' and unit['unitId'] == 'Tagged'])))
                        res_tags.add('BLACKLISTED')

                        required_tags = lance
                        lancedefs.append((id, file, file_location, mechsDefs, req_tags, res_tags))

                    except JSONDecodeError as error:
                        print(f'[{file_location}] - [{error}]')
                        raise

    return mechs


if __name__ == '__main__':
    base_directory = r'D:\Test Data\BT Base Data'
    dlc_directory = r'C:\Users\Stephen Weistra\gitrepos\bt-dlc-designdata'
    output_file = r'c:\tmp\HBS-Mech-Usage.csv'

    flashPoints = []
    contracts = []
    stock_mechs = []
    dlc_mechs = []
    lancedefs = []

    do_a_thing(base_directory, stock_mechs, flashPoints, contracts, lancedefs)
    do_a_thing(dlc_directory, dlc_mechs, flashPoints, contracts, lancedefs)

    mechSummary = []

    mechs = stock_mechs + dlc_mechs

    for mech in mechs:
        id = mech[0]
        contract_usage = [contract for contract in contracts if mech[0] in contract[3]]
        tags = mech[3]
        specific_lance_usage = [lance for lance in lancedefs if mech in lance[3]]
        tag_lance_usage = [lance for lance in lancedefs if len(lance[4]) > 0 and (len(tags & lance[4]) == len(lance[4]) and len(tags & lance[5]) == 0)]
        mechSummary.append((mech[0], len(contract_usage), len(specific_lance_usage), len(tag_lance_usage), mech[2].replace('Stephen Weistra','vengefire'), True if id in [mech[0] for mech in stock_mechs] else False))
        if id == 'mechdef_battlemaster_BLR-1G_fp_morganKell':
            pass

    data = f'Mech,File,Base,Flash Point Contracts,Specified Lances, Tagged Lances\r'
    data += '\r'.join([f'{summary[0]},{summary[4]},{summary[5]},{summary[1]},{summary[2]},{summary[3]}' for summary in mechSummary])

    # for summary in mechSummary:
        # data += f'{summary[0]},{summary[4]},{summary[5]},{summary[1]},{summary[2]},{summary[3]}'

    print(data)

    with open(output_file, mode='w') as fd:
        fd.write(data)

    '''for root, dirs, files in os.walk(dlc_directory):
        for file in files:
            if r'mechdef' in file.lower():
                dlc_mechs.append((file, os.path.join(root, file)))

    print('--STOCK MECHS--')
    print('\r\n'.join(f'{entry[0]} - {entry[1]}' for entry in stock_mechs))
    print('--DLC MECHS--')
    print('\r\n'.join(f'{entry[0]} - {entry[1]}' for entry in dlc_mechs))'''
